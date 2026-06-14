# universal_harvester/agent/endpoint_detection.py

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

AUTH_FILE = Path(os.environ.get("AUTH_FILE_PATH", "copilot_auth.json"))

CONVERSATION_LIST_PATTERNS = [
    re.compile(r"/c/api/conversations(?:\?|$)", re.IGNORECASE),
]

HISTORY_PATTERNS = [
    re.compile(r"/c/api/conversations/[^/]+/history", re.IGNORECASE),
]

ARCHIVE_HINTS = ["archived=true", "include=all", "archive"]


def _load_auth() -> List[Dict[str, Any]]:
    if not AUTH_FILE.exists():
        raise RuntimeError(f"{AUTH_FILE} not found. Run capture_auth.py first.")
    try:
        with AUTH_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise RuntimeError(f"{AUTH_FILE} contains invalid JSON.")
    if not isinstance(data, list):
        raise RuntimeError(f"{AUTH_FILE} must contain a JSON array of request logs.")
    return data


def detect_endpoints() -> Dict[str, List[str]]:
    entries = _load_auth()
    urls = [e.get("url") for e in entries if isinstance(e.get("url"), str)]

    conv, hist, arch, unknown = [], [], [], []

    for url in urls:
        if any(p.search(url) for p in CONVERSATION_LIST_PATTERNS):
            conv.append(url)
            if any(h in url for h in ARCHIVE_HINTS):
                arch.append(url)
            continue

        if any(p.search(url) for p in HISTORY_PATTERNS):
            hist.append(url)
            continue

        if "conversations" in url.lower():
            unknown.append(url)

    return {
        "conversation_list_endpoints": sorted(set(conv)),
        "history_endpoints": sorted(set(hist)),
        "archive_endpoints": sorted(set(arch)),
        "unknown_conversation_like": sorted(set(unknown)),
    }


class EndpointProfile:
    def __init__(self, data: Dict[str, List[str]]):
        self.data = data

    def to_dict(self) -> Dict[str, List[str]]:
        return self.data

    def summary(self) -> str:
        lines = ["=== Endpoint Detection Summary ==="]
        for key, values in self.data.items():
            lines.append(f"\n{key} ({len(values)}):")
            for url in values:
                lines.append(f"  - {url}")
        return "\n".join(lines)


def detect_all_endpoints() -> EndpointProfile:
    return EndpointProfile(detect_endpoints())