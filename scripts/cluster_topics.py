# cluster_topics.py
import sqlite3
import json
import os
from collections import defaultdict

DB_PATH = "harvester.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCHEMA = """
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT,
    message_count INTEGER
);
CREATE TABLE IF NOT EXISTS message_topics (
    message_id TEXT PRIMARY KEY,
    topic_id INTEGER,
    FOREIGN KEY(message_id) REFERENCES messages(id),
    FOREIGN KEY(topic_id) REFERENCES topics(id)
);
"""

def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(os.path.join(BASE_DIR, DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def run_clustering():
    conn = connect_db()
    conn.executescript(SCHEMA)

    conn.execute("DELETE FROM message_topics;")
    conn.execute("DELETE FROM topics;")

    print("[CLUSTER] Fetching embeddings from database...")
    rows = conn.execute("SELECT message_id, embedding FROM message_embeddings").fetchall()

    if not rows:
        print("[CLUSTER] No embeddings found. Run generate_embeddings.py first.")
        return

    print(f"[CLUSTER] Found {len(rows)} embeddings. Clustering...")

    # Basic grouping simulation (Replace with sklearn KMeans in production)
    clusters = defaultdict(list)
    for msg_id, emb_str in rows:
        clusters[emb_str].append(msg_id)

    print(f"[CLUSTER] Generated {len(clusters)} unique topics/clusters.")

    for i, (emb_str, msg_ids) in enumerate(clusters.items()):
        label = f"Topic Cluster {i+1}"
        cur = conn.execute("INSERT INTO topics (label, message_count) VALUES (?, ?)", (label, len(msg_ids)))
        topic_id = cur.lastrowid
        conn.executemany("INSERT INTO message_topics (message_id, topic_id) VALUES (?, ?)", 
                         [(msg_id, topic_id) for msg_id in msg_ids])

    conn.commit()
    conn.close()
    print("[CLUSTER] Clustering complete. Topics saved to database.")

if __name__ == "__main__":
    run_clustering()