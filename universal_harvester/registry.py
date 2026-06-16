import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).parent.parent / "harvester.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Core Entities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                title TEXT,
                source TEXT,
                harvested INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                chat_id TEXT,
                author_role TEXT,
                content TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY(chat_id) REFERENCES chats(id)
            )
        """)
        
        # Future-proofing for entities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT, -- 'character', 'project', 'prompt', etc.
                name TEXT,
                description TEXT,
                chat_id TEXT,
                message_id TEXT,
                FOREIGN KEY(chat_id) REFERENCES chats(id),
                FOREIGN KEY(message_id) REFERENCES messages(id)
            )
        """)
        
        conn.commit()

def upsert_chat(chat_id: str, title: str, source: str = "api", harvested: int = 1):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chats (id, title, source, harvested, last_updated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET 
                title=excluded.title,
                source=excluded.source,
                harvested=excluded.harvested,
                last_updated=CURRENT_TIMESTAMP
        """, (chat_id, title, source, harvested))
        conn.commit()

def upsert_message(msg_id: str, chat_id: str, role: str, content: str, created_at: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (id, chat_id, author_role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET 
                content=excluded.content,
                author_role=excluded.author_role,
                created_at=excluded.created_at
        """, (msg_id, chat_id, role, content, created_at))
        conn.commit()

def load_unharvested_chats() -> List[sqlite3.Row]:
    with get_db() as conn:
        return conn.execute("SELECT * FROM chats WHERE harvested = 0").fetchall()

if __name__ == "__main__":
    init_db()
    print(f"[REGISTRY] Initialized database at {DB_PATH}")
