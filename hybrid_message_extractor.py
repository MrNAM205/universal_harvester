# hybrid_message_extractor.py
import json
import sqlite3
import glob
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DB_PATH = "harvester.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# SQLite Schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS chats (
    id TEXT PRIMARY KEY,
    title TEXT,
    source TEXT,
    created_at TEXT,
    updated_at TEXT,
    message_count INTEGER,
    harvested_at TEXT
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    chat_id TEXT,
    author_type TEXT,
    channel TEXT,
    created_at TEXT,
    content TEXT,
    source TEXT,
    FOREIGN KEY(chat_id) REFERENCES chats(id)
);
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(os.path.join(BASE_DIR, DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()

def safe_load_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[HYBRID] Failed to load {path}: {e}")
        return None

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

# ---------------------------------------------------------------------------
# JSON Normalization
# ---------------------------------------------------------------------------

def extract_conversations(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize any JSON structure into a list of chat objects.
    Handles:
    - dict with "conversations"
    - dict representing a single chat
    - list of chats
    - anything else -> empty list
    """
    if isinstance(data, dict):
        if "conversations" in data and isinstance(data["conversations"], list):
            return data["conversations"]
        if "id" in data or "conversationId" in data:
            return [data]
        return []

    if isinstance(data, list):
        return data

    return []

# ---------------------------------------------------------------------------
# Upsert Logic
# ---------------------------------------------------------------------------

def upsert_chat(conn: sqlite3.Connection, chat_id: str, title: str,
                source: str, created_at: Optional[str],
                updated_at: Optional[str], message_count: int) -> None:

    harvested_at = utc_now()

    conn.execute(
        """
        INSERT INTO chats (id, title, source, created_at, updated_at, message_count, harvested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            source=excluded.source,
            created_at=COALESCE(chats.created_at, excluded.created_at),
            updated_at=COALESCE(excluded.updated_at, chats.updated_at),
            message_count=excluded.message_count,
            harvested_at=excluded.harvested_at;
        """,
        (chat_id, title, source, created_at, updated_at, message_count, harvested_at),
    )

def upsert_message(conn: sqlite3.Connection, msg: Dict[str, Any],
                   chat_id: str, source: str) -> None:

    msg_id = msg.get("id")
    if not msg_id:
        return

    author = msg.get("author", {}).get("type")
    channel = msg.get("channel")
    created_at = msg.get("createdAt")
    content = json.dumps(msg.get("content", []), ensure_ascii=False)

    conn.execute(
        """
        INSERT INTO messages (id, chat_id, author_type, channel, created_at, content, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            chat_id=excluded.chat_id,
            author_type=excluded.author_type,
            channel=excluded.channel,
            created_at=COALESCE(messages.created_at, excluded.created_at),
            content=excluded.content,
            source=excluded.source;
        """,
        (msg_id, chat_id, author, channel, created_at, content, source),
    )

# ---------------------------------------------------------------------------
# File Processors
# ---------------------------------------------------------------------------

def process_file(conn: sqlite3.Connection, path: str, source: str) -> None:
    data = safe_load_json(path)
    if not data:
        return

    conversations = extract_conversations(data)
    print(f"[EXTRACT] Found {len(conversations)} chats in {source}.")

    for chat in conversations:
        chat_id = chat.get("id") or chat.get("conversationId")
        if not chat_id:
            continue

        title = chat.get("title") or f"Chat {chat_id}"
        messages = chat.get("messages", [])
        created_at = messages[0].get("createdAt") if messages else None
        updated_at = messages[-1].get("createdAt") if messages else None

        upsert_chat(
            conn,
            chat_id,
            title,
            source,
            created_at,
            updated_at,
            len(messages),
        )

        for msg in messages:
            upsert_message(conn, msg, chat_id, source)

# ---------------------------------------------------------------------------
# Main Extractor
# ---------------------------------------------------------------------------

def run_hybrid_extractor() -> None:
    conn = connect_db()
    init_db(conn)

    # Priority order: verified -> deleted -> api -> single
    sources = [
        ("all_chats_verified.json", "verified"),
        ("all_chats_deleted.json", "deleted"),
        ("all_chats_api.json", "api"),
    ]

    for filename, source in sources:
        path = os.path.join(BASE_DIR, filename)
        if os.path.exists(path):
            print(f"[EXTRACT] Reading {filename}...")
            process_file(conn, path, source)

    # Single chat dumps
    for path in glob.glob(os.path.join(BASE_DIR, "copilot_chat_*.json")):
        print(f"[EXTRACT] Reading {os.path.basename(path)}...")
        process_file(conn, path, "single")

    conn.commit()
    conn.close()
    print("[EXTRACT] Hybrid extraction complete.")

if __name__ == "__main__":
    run_hybrid_extractor()
