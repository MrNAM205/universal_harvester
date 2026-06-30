from dataclasses import dataclass
from typing import List

@dataclass
class ChainSynthesisResult:
    mission_id: str
    cycles_analyzed: int
    themes: List[str]
    warnings: List[str]
    improvements: List[str]
    summary: str

class ChainSynthesisManager:
    def __init__(self, storage, embedder, reasoner):
        self.storage = storage      # ReasoningChainManager
        self.embedder = embedder    # same interface as memory embeddings
        self.reasoner = reasoner    # LLM/local reasoner
        self._init_db()

    def _init_db(self):
        cursor = self.storage.storage.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chain_synthesis (
                mission_id TEXT PRIMARY KEY,
                cycles_analyzed INTEGER,
                summary TEXT,
                themes TEXT,
                warnings TEXT,
                improvements TEXT
            )
        """)
        self.storage.storage.commit()

    def synthesize(self, mission_id: str) -> ChainSynthesisResult:
        chains = self.storage.load_chains(mission_id)
        if not chains:
            return ChainSynthesisResult(
                mission_id=mission_id,
                cycles_analyzed=0,
                themes=[],
                warnings=[],
                improvements=[],
                summary="No chains available for synthesis."
            )

        texts = [self._flatten_chain(c) for c in chains]
        embeddings = [self.embedder.embed(t) for t in texts]
        clusters = self._cluster_embeddings(embeddings, texts)

        summary = self.reasoner.summarize_chain_clusters(clusters)
        themes = self.reasoner.extract_themes(summary)
        warnings = self.reasoner.extract_warnings(summary)
        improvements = self.reasoner.extract_improvements(summary)

        result = ChainSynthesisResult(
            mission_id=mission_id,
            cycles_analyzed=len(chains),
            themes=themes,
            warnings=warnings,
            improvements=improvements,
            summary=summary
        )
        self._persist(result)
        return result

    def _persist(self, result: ChainSynthesisResult):
        import json
        cursor = self.storage.storage.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO chain_synthesis (mission_id, cycles_analyzed, summary, themes, warnings, improvements) VALUES (?, ?, ?, ?, ?, ?)",
            (result.mission_id, result.cycles_analyzed, result.summary, json.dumps(result.themes), json.dumps(result.warnings), json.dumps(result.improvements))
        )
        self.storage.storage.commit()

    def _flatten_chain(self, chain):
        return "\n".join(
            f"[{step.phase}] {step.content}"
            for step in chain.steps
        )

    def _cluster_embeddings(self, embeddings, texts):
        # simple k-means / agglomerative stub
        # for now: single cluster with all texts
        return {"cluster_0": texts}
