import json
from omniverobrix.sovereign.reasoning_chain import ReasoningChain

class ReasoningChainManager:
    def __init__(self, storage):
        self.storage = storage
        self._init_db()

    def _init_db(self):
        cursor = self.storage.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reasoning_chains (
                mission_id TEXT,
                cycle_id TEXT,
                step_index INTEGER,
                phase TEXT,
                content TEXT,
                data TEXT
            )
        """)
        self.storage.commit()

    def start_chain(self, mission_id: str, cycle_id: str) -> ReasoningChain:
        return ReasoningChain(mission_id=mission_id, cycle_id=cycle_id)

    def persist(self, chain: ReasoningChain):
        import dataclasses
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if dataclasses.is_dataclass(obj):
                    return dataclasses.asdict(obj)
                return super().default(obj)

        cursor = self.storage.cursor()
        for i, step in enumerate(chain.steps):
            cursor.execute(
                "INSERT INTO reasoning_chains (mission_id, cycle_id, step_index, phase, content, data) VALUES (?, ?, ?, ?, ?, ?)",
                (chain.mission_id, chain.cycle_id, i, step.phase, step.content, json.dumps(step.data, cls=CustomEncoder))
            )
        self.storage.commit()

    def load_chains(self, mission_id: str) -> list[ReasoningChain]:
        cursor = self.storage.cursor()
        cursor.execute(
            "SELECT cycle_id, phase, content, data FROM reasoning_chains WHERE mission_id = ? ORDER BY cycle_id, step_index",
            (mission_id,)
        )
        rows = cursor.fetchall()
        
        chains_by_cycle = {}
        for row in rows:
            cycle_id, phase, content, data_str = row
            if cycle_id not in chains_by_cycle:
                chains_by_cycle[cycle_id] = ReasoningChain(mission_id=mission_id, cycle_id=cycle_id)
            
            data = json.loads(data_str) if data_str else {}
            chains_by_cycle[cycle_id].add(phase, content, data)
            
        return list(chains_by_cycle.values())
