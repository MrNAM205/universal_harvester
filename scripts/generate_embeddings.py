# generate_embeddings.py
import sqlite3
import json
import os
from typing import List
from datetime import datetime, timezone

DB_PATH = "harvester.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCHEMA = """
CREATE TABLE IF NOT EXISTS message_embeddings (
    message_id TEXT PRIMARY KEY,
    embedding TEXT,
    created_at TEXT,
    FOREIGN KEY(message_id) REFERENCES messages(id)
);
"""

def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(os.path.join(BASE_DIR, DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

# --------------------------------------------------------------------
# Replace this with your real embedding call (OpenAI, Azure, etc.)
# --------------------------------------------------------------------
def embed_text(text: str) -> List[float]:
    # TODO: implement real embedding here.
    # For now, return a tiny dummy vector so the pipeline runs.
    return [float(len(text) % 10), float(len(text) % 7), float(len(text) % 5)]

def fetch_messages_without_embeddings(conn: sqlite3.Connection, limit: int = 1000):
    return conn.execute(
        """
        SELECT m.id, m.content
        FROM messages m
        LEFT JOIN message_embeddings e ON e.message_id = m.id
        WHERE e.message_id IS NULL
        LIMIT ?;
        """,
        (limit,),
    ).fetchall()

def upsert_embedding(conn: sqlite3.Connection, message_id: str, embedding: List[float]) -> None:
    conn.execute(
        """
        INSERT INTO message_embeddings (message_id, embedding, created_at)
        VALUES (?, ?, ?)
        ON CONFLICT(message_id) DO UPDATE SET
            embedding = excluded.embedding,
            created_at = excluded.created_at;
        """,
        (message_id, json.dumps(embedding), utc_now()),
    )

def run_embedding_generator(batch_size: int = 256) -> None:
    conn = connect_db()
    init_schema(conn)

    total = 0
    while True:
        rows = fetch_messages_without_embeddings(conn, limit=batch_size)
        if not rows:
            break

        for msg_id, content in rows:
            # content is stored as JSON of parts; you may want to decode it
            try:
                parts = json.loads(content)
                text = "\n".join(
                    p.get("text", "") for p in parts if isinstance(p, dict)
                ).strip()
            except Exception:
                text = str(content)

            emb = embed_text(text)
            upsert_embedding(conn, msg_id, emb)
            total += 1

        conn.commit()
        print(f"[EMBED] Processed {total} messages so far...")

    conn.close()
    print(f"[EMBED] Embedding generation complete. Total messages embedded: {total}")

if __name__ == "__main__":
    run_embedding_generator()