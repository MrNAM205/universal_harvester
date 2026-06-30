import uuid
import time
import json
from dataclasses import dataclass

@dataclass
class EmbeddingRecord:
    id: str
    mission_id: str
    timestamp: float
    kind: str
    vector: list[float]
    text: str

class MemoryEmbeddingManager:
    def __init__(self, embedder, storage):
        self.embedder = embedder
        self.storage = storage
        self._init_db()

    def _init_db(self):
        cursor = self.storage.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_embeddings (
                id TEXT PRIMARY KEY,
                mission_id TEXT,
                timestamp REAL,
                kind TEXT,
                vector TEXT,
                text TEXT
            )
        """)
        self.storage.commit()

    def add(self, mission_id, kind, text):
        vector = self.embedder.embed(text)
        record = EmbeddingRecord(
            id=str(uuid.uuid4()),
            mission_id=mission_id,
            timestamp=time.time(),
            kind=kind,
            vector=vector,
            text=text,
        )
        self._insert_embedding(record)
        return record

    def _insert_embedding(self, record: EmbeddingRecord):
        cursor = self.storage.cursor()
        cursor.execute(
            "INSERT INTO memory_embeddings VALUES (?, ?, ?, ?, ?, ?)",
            (record.id, record.mission_id, record.timestamp, record.kind, json.dumps(record.vector), record.text)
        )
        self.storage.commit()

    def _load_all_embeddings(self) -> list[EmbeddingRecord]:
        cursor = self.storage.cursor()
        cursor.execute("SELECT id, mission_id, timestamp, kind, vector, text FROM memory_embeddings")
        rows = cursor.fetchall()
        return [
            EmbeddingRecord(
                id=r[0],
                mission_id=r[1],
                timestamp=r[2],
                kind=r[3],
                vector=json.loads(r[4]),
                text=r[5]
            ) for r in rows
        ]

    def search(self, query_text, top_k=5):
        qvec = self.embedder.embed(query_text)
        all_records = self._load_all_embeddings()
        scored = [
            (self._cosine_similarity(qvec, r.vector), r)
            for r in all_records
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:top_k]]

    def _cosine_similarity(self, a, b):
        dot = sum(x*y for x, y in zip(a, b))
        na = sum(x*x for x in a) ** 0.5
        nb = sum(x*x for x in b) ** 0.5
        return dot / (na * nb + 1e-9)
