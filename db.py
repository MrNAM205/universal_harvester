import sqlite3
import time

DB_PATH = "harvested_chats.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        title TEXT,
        created_at INTEGER,
        harvested_at INTEGER
    );

    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT,
        role TEXT,
        content TEXT,
        timestamp INTEGER,
        msg_index INTEGER,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    );
    """)
    db.commit()
    db.close()

def save_conversation(conv_id, title, created_at):
    db = get_db()
    harvested_at = int(time.time())
    # Handle potentially string timestamps from Copilot API by converting to 0 if not an integer
    try:
        created_at_int = int(created_at)
    except (ValueError, TypeError):
        created_at_int = 0

    db.execute(
        "INSERT OR REPLACE INTO conversations (id, title, created_at, harvested_at) VALUES (?, ?, ?, ?)",
        (conv_id, title, created_at_int, harvested_at)
    )
    db.commit()
    db.close()

def save_message(msg_id, conv_id, role, content, timestamp, msg_index):
    db = get_db()
    # Ensure timestamp is an integer
    try:
        timestamp_int = int(timestamp)
    except (ValueError, TypeError):
        timestamp_int = 0

    db.execute(
        "INSERT OR REPLACE INTO messages (id, conversation_id, role, content, timestamp, msg_index) VALUES (?, ?, ?, ?, ?, ?)",
        (msg_id, conv_id, role, content, timestamp_int, msg_index)
    )
    db.commit()
    db.close()
