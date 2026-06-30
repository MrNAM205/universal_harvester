from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import sqlite3
import json

@dataclass
class ReflectionRecord:
    id: str
    mission_id: str
    timestamp: float
    phase: str
    content: str
    tags: List[str]

class FakeEmbedder:
    def embed(self, text: str) -> bytes:
        # A mock embedding that just turns text into bytes
        return text.encode('utf-8')

class ReflectionClusterer:
    def __init__(self, embedder: Any, storage: Any, reasoner: Any = None):
        self.embedder = embedder
        self.storage = storage  # Assuming this is an SQLite connection for now
        self.reasoner = reasoner
        self._init_db()

    def _init_db(self):
        cursor = self.storage.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflection_embeddings (
                reflection_id TEXT PRIMARY KEY,
                mission_id TEXT,
                timestamp REAL,
                phase TEXT,
                vector BLOB
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflection_clusters (
                cluster_id TEXT,
                mission_id TEXT,
                size INTEGER,
                centroid BLOB,
                summary TEXT
            )
        """)
        self.storage.commit()

    def add_reflection(self, reflection: ReflectionRecord):
        vector = self.embedder.embed(reflection.content)
        cursor = self.storage.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO reflection_embeddings VALUES (?, ?, ?, ?, ?)",
            (reflection.id, reflection.mission_id, reflection.timestamp, reflection.phase, vector)
        )
        self.storage.commit()

    def _load_vectors(self, mission_id: Optional[str] = None) -> tuple:
        cursor = self.storage.cursor()
        if mission_id:
            cursor.execute("SELECT reflection_id, mission_id, timestamp, phase, vector FROM reflection_embeddings WHERE mission_id = ?", (mission_id,))
        else:
            cursor.execute("SELECT reflection_id, mission_id, timestamp, phase, vector FROM reflection_embeddings")
        
        rows = cursor.fetchall()
        
        meta = []
        vectors = []
        for row in rows:
            # We recreate a mock reflection record since we only stored parts in this table
            # In a real system, we'd join with the main reflections table to get full content.
            # For this MVP clustering, we decode the fake vector to get the content back.
            content = row[4].decode('utf-8') 
            meta.append(ReflectionRecord(id=row[0], mission_id=row[1], timestamp=row[2], phase=row[3], content=content, tags=[]))
            vectors.append(row[4])
        return vectors, meta

    def _run_clustering(self, vectors: List[bytes]) -> Dict[str, List[int]]:
        # Extremely basic mock clustering algorithm:
        # Group reflections by exact text match (or simply return one cluster for now)
        clusters = {"cluster_0": list(range(len(vectors)))}
        return clusters

    def _summarize_clusters(self, clusters: Dict[str, List[int]], meta: List[ReflectionRecord]) -> List[Dict[str, Any]]:
        summaries = []
        for cid, indices in clusters.items():
            texts = [meta[i].content for i in indices]
            
            if self.reasoner:
                summary = self.reasoner.summarize_reflection_cluster(texts)
            else:
                summary = f"Summary of {len(texts)} reflections: " + " ".join(texts)[:50] + "..."

            summaries.append({
                "cluster_id": cid,
                "size": len(indices),
                "summary": summary,
            })
        return summaries

    def _store_clusters(self, summaries: List[Dict[str, Any]], mission_id: Optional[str] = None):
        cursor = self.storage.cursor()
        for s in summaries:
            cursor.execute(
                "INSERT INTO reflection_clusters (cluster_id, mission_id, size, summary) VALUES (?, ?, ?, ?)",
                (s["cluster_id"], mission_id or "global", s["size"], s["summary"])
            )
        self.storage.commit()

    def build_clusters(self, mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
        vectors, meta = self._load_vectors(mission_id)
        if not vectors:
            return []

        clusters = self._run_clustering(vectors)
        summaries = self._summarize_clusters(clusters, meta)
        self._store_clusters(summaries, mission_id)
        return summaries

    def get_clusters(self, mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.storage.cursor()
        if mission_id:
            cursor.execute("SELECT cluster_id, size, summary FROM reflection_clusters WHERE mission_id = ?", (mission_id,))
        else:
            cursor.execute("SELECT cluster_id, size, summary FROM reflection_clusters")
        
        rows = cursor.fetchall()
        return [{"cluster_id": r[0], "size": r[1], "summary": r[2]} for r in rows]
