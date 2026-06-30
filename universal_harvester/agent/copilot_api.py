import json
import os
import random
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

COPILOT_BASE = "https://copilot.microsoft.com"
AUTH_FILE = os.environ.get("AUTH_FILE_PATH", "copilot_auth.json")
COOKIE_FILE = os.environ.get("COOKIE_FILE_PATH", "copilot_cookies.json")


def _load_auth_entry() -> Dict[str, Any]:
    """
    Load the captured auth JSON and return the most useful entry
    (one that hits /c/api/conversations and has an Authorization header).
    """
    if not os.path.exists(AUTH_FILE):
        raise RuntimeError(f"{AUTH_FILE} not found. Run capture_auth.py first.")

    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise RuntimeError(f"{AUTH_FILE} contains invalid JSON.")

    if not isinstance(data, list):
        raise RuntimeError(f"{AUTH_FILE} must contain a JSON array of request logs.")

    # Prefer a conversations/history entry, fall back to any conversations entry
    best: Optional[Dict[str, Any]] = None
    for entry in data:
        url = entry.get("url", "")
        headers = entry.get("headers", {})
        if "/c/api/conversations" in url and "authorization" in headers:
            # Prefer history endpoints if present
            if "/history" in url:
                return entry
            best = entry

    if best is None:
        raise RuntimeError(
            "No suitable conversations entry with Authorization header found in copilot_auth.json."
        )

    return best


def _build_session() -> Tuple[requests.Session, str]:
    """
    Build a requests.Session with the captured headers.
    Returns (session, referer) so we can reuse a sane referer.
    """
    auth_entry = _load_auth_entry()
    headers = auth_entry.get("headers", {})
    referer = headers.get("referer", "https://copilot.microsoft.com/")

    # Only keep headers that are safe and useful for API calls
    allowed_keys = {
        "authorization",
        "x-search-uilang",
        "user-agent",
        "sec-ch-ua",
        "sec-ch-ua-platform",
        "sec-ch-ua-mobile",
        "sec-ch-ua-bitness",
        "sec-ch-ua-model",
        "sec-ch-ua-arch",
        "sec-ch-ua-full-version",
        "sec-ch-ua-full-version-list",
        "sec-ch-ua-platform-version",
        "baggage",
        "sentry-trace",
    }

    session_headers = {
        k: v for k, v in headers.items() if k.lower() in allowed_keys
    }
    session_headers["referer"] = referer

    s = requests.Session()
    s.headers.update(session_headers)
    
    # Inject required base Copilot API headers
    s.headers.update({
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://copilot.microsoft.com",
    })

    # Load cookies into the session
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                cookies = json.load(f)
                for cookie in cookies:
                    s.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain"))
        except Exception as e:
            print(f"Warning: Failed to load cookies from {COOKIE_FILE}: {e}")
            
    return s, referer


def _normalize_results_container(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize a Copilot API response that may be:
    - a list of objects
    - a dict with 'results'
    - a dict with 'items' or 'messages'
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("results", "items", "messages", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]

    raise RuntimeError("Could not normalize results container from response.")


def _extract_next_cursor(data: Any) -> Optional[str]:
    """
    Try to extract a pagination cursor from the response.
    Copilot uses 'next' for conversations; history may use 'next' or similar.
    """
    if not isinstance(data, dict):
        return None

    for key in ("nextCursor", "next", "cursor"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value

    return None


def _normalize_api_message(msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a raw API message into the unified {id, role, text, createdAt} format.
    """
    msg_id = msg.get("id", "")
    created_at = msg.get("createdAt", "")
    
    author_type = msg.get("author", {}).get("type", "user")
    role = "assistant" if author_type.lower() == "ai" else "user"
    
    # Extract text from content blocks
    text_blocks = []
    for block in msg.get("content", []):
        if block.get("type") == "text":
            text = block.get("text")
            if text:
                text_blocks.append(text)
    
    text = "\n\n".join(text_blocks)
    
    return {
        "id": msg_id,
        "role": role,
        "text": text,
        "createdAt": created_at,
        "raw": msg
    }


def _extract_chat_ids_from_auth() -> List[str]:
    """
    Scan copilot_auth.json for history endpoints and extract chat IDs.
    Example URL:
    https://copilot.microsoft.com/c/api/conversations/{chatId}/history?cursor=...&api-version=2
    """
    if not os.path.exists(AUTH_FILE):
        raise RuntimeError(f"{AUTH_FILE} not found. Run capture_auth.py first.")

    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise RuntimeError(f"{AUTH_FILE} contains invalid JSON.")

    if not isinstance(data, list):
        raise RuntimeError(f"{AUTH_FILE} must contain a JSON array of request logs.")

    chat_ids: List[str] = []

    for entry in data:
        url = entry.get("url", "")
        if "/c/api/conversations/" in url and "/history" in url:
            # Extract the chatId between /conversations/ and /history
            try:
                part = url.split("/c/api/conversations/")[1]
                chat_id = part.split("/history")[0]
                if chat_id and chat_id not in chat_ids:
                    chat_ids.append(chat_id)
            except Exception:
                continue

    return chat_ids


def fetch_chat_list_via_api() -> List[Dict[str, Any]]:
    """
    Fetch the full chat list from the /c/api/conversations endpoint,
    falling back to extracting from auth logs if needed.
    """
    session, _ = _build_session()
    all_chats: List[Dict[str, Any]] = []
    cursor: Optional[str] = None
    page_index = 0

    while True:
        params = {"types": "chat,character,xbox,group"}
        if cursor:
            params["cursor"] = cursor

        url = f"{COPILOT_BASE}/c/api/conversations"
        
        try:
            resp = session.get(url, params=params)
            
            if resp.status_code == 404:
                # Endpoint doesn't exist? Fallback.
                break
            if resp.status_code != 200:
                print(f"[API] Error getting conversations list: {resp.status_code}")
                break

            data = resp.json()
            page_chats = _normalize_results_container(data)
            all_chats.extend(page_chats)

            cursor = _extract_next_cursor(data)
            page_index += 1

            if not cursor:
                break
            time.sleep(0.2)
        except Exception as e:
            print(f"[API] Exception fetching conversations list: {e}")
            break
            
    if all_chats:
        print(f"[API] Discovered {len(all_chats)} chats from API conversations endpoint.")
        return all_chats
        
    print("[API] Falling back to discovering chats from history endpoints in auth file.")
    chat_ids = _extract_chat_ids_from_auth()
    print(f"[API] Discovered {len(chat_ids)} chats from history endpoints.")

    chats: List[Dict[str, Any]] = []
    for cid in chat_ids:
        chats.append({"id": cid, "title": f"Chat {cid}"})

    return chats


def fetch_chat_messages_via_api(chat_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all messages for a given chat via the history endpoint:
    /c/api/conversations/{chatId}/history?cursor=...&api-version=2

    We walk backwards/forwards using the 'next' cursor until exhausted.
    """
    session, _ = _build_session()

    all_messages: List[Dict[str, Any]] = []
    cursor: Optional[str] = None
    page_index = 0

    while True:
        params = {"api-version": "2"}
        if cursor:
            params["cursor"] = cursor

        url = f"{COPILOT_BASE}/c/api/conversations/{chat_id}/history"

        for attempt in range(8):
            print(f"[API] Fetching history page {page_index + 1} for chat {chat_id} (cursor={cursor})")
            resp = session.get(url, params=params)

            if resp.status_code == 429:
                wait = 2 ** attempt + random.uniform(0, 1)
                print(f"[API] 429 rate limit. Waiting {wait:.2f} seconds…")
                time.sleep(wait)
                continue

            if resp.status_code == 403:
                raise RuntimeError(
                    f"History endpoint returned 403 for chat {chat_id}. Captured headers may be incomplete."
                )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"History endpoint returned {resp.status_code} for chat {chat_id}: {resp.text[:500]}"
                )
            break

        data = resp.json()
        page_messages = _normalize_results_container(data)
        
        # Normalize the raw API messages to the unified {id, role, text} format
        for pm in page_messages:
            all_messages.append(_normalize_api_message(pm))

        cursor = _extract_next_cursor(data)
        page_index += 1

        if not cursor:
            break

        time.sleep(0.2)

    return all_messages