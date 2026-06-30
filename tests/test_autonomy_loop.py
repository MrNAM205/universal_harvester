
import sqlite3
from typing import Dict, Any

from omniverobrix.core.state import AutonomyContext, MissionState, StepResult
from omniverobrix.sovereign.autonomy_loop import AutonomyLoop
from omniverobrix.sovereign.reflection_clusterer import ReflectionClusterer, ReflectionRecord, FakeEmbedder
from omniverobrix.sovereign.stop_conditions import StopConditionEngine
from omniverobrix.sovereign.environment import EnvironmentModel
from omniverobrix.sovereign.resource_monitor import ResourceMonitor
from omniverobrix.sovereign.clock import Clock
from omniverobrix.sovereign.operator_channel import OperatorChannel
from omniverobrix.sovereign.events import EventBuffer

class FakeReasoner:
    def __init__(self, halt_on_reflect: bool = True):
        self.halt_on_reflect = halt_on_reflect

    def generate_reflection(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        return {"thought": "Processing observation", "id": "ref-1"}

    def generate_post_action_reflection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"thought": "Actions completed successfully", "halt": self.halt_on_reflect, "id": "ref-2"}

    def summarize_reflection_cluster(self, texts: list) -> str:
        return f"Summary of {len(texts)} items"

    def summarize_chain_clusters(self, clusters: dict) -> str:
        return "Chain synthesis summary"

    def extract_themes(self, summary: str) -> list:
        return ["theme1", "theme2"]

    def extract_warnings(self, summary: str) -> list:
        return ["warning1"]

    def extract_improvements(self, summary: str) -> list:
        return ["improvement1"]

class FakePlanner:
    def plan(self, reflection: Dict[str, Any], context: AutonomyContext) -> list:
        return [{"type": "tool", "name": "test_action"}]

class FakeScheduler:
    def execute(self, step: Dict[str, Any], context: AutonomyContext) -> StepResult:
        return StepResult(action_type=step["type"], success=True, data={})

def create_fake_env() -> EnvironmentModel:
    return EnvironmentModel(
        resource_monitor=ResourceMonitor(),
        clock=Clock(),
        operator_channel=OperatorChannel(),
        event_buffer=EventBuffer()
    )

def test_environment_snapshot_basic():
    env = create_fake_env()
    snap = env.snapshot()
    assert snap.time is not None
    assert "cpu_percent" in snap.resources
    assert "halt" in snap.operator
    print("test_environment_snapshot_basic passed")

def test_autonomy_cycle_runs():
    db = sqlite3.connect(":memory:")
    clusterer = ReflectionClusterer(embedder=FakeEmbedder(), storage=db, reasoner=FakeReasoner())

    loop = AutonomyLoop(
        reasoner=FakeReasoner(),
        planner=FakePlanner(),
        scheduler=FakeScheduler(),
        reflection_clusterer=clusterer
    )
    
    context = AutonomyContext(
        mission_state=MissionState(id="m-100", status="active"),
        environment=create_fake_env(),
        operator_channel=OperatorChannel()
    )
    
    state = loop.run(context)
    assert state.status != "continue"
    assert state.status == "halt_mission"  # because our FakeReasoner sets halt=True in post-action
    print("test_autonomy_cycle_runs passed")

def test_safety_rule_iteration_cap():
    from omniverobrix.core.state import SafetyRules
    db = sqlite3.connect(":memory:")
    clusterer = ReflectionClusterer(embedder=FakeEmbedder(), storage=db, reasoner=FakeReasoner(halt_on_reflect=False))

    loop = AutonomyLoop(
        reasoner=FakeReasoner(halt_on_reflect=False),
        planner=FakePlanner(),
        scheduler=FakeScheduler(),
        reflection_clusterer=clusterer
    )
    
    # Set iterations past the max
    rules = SafetyRules(max_iterations=1)
    context = AutonomyContext(
        mission_state=MissionState(id="m-100", status="active", iterations=2),
        safety_rules=rules,
        environment=create_fake_env(),
        operator_channel=OperatorChannel()
    )
    
    state = loop.run(context)
    assert state.status == "halt_global"
    assert "safety_violation" in state.last_reflection["reason"]
    print("test_safety_rule_iteration_cap passed")

def test_reflection_clustering_basic():
    db = sqlite3.connect(":memory:")
    clusterer = ReflectionClusterer(embedder=FakeEmbedder(), storage=db, reasoner=FakeReasoner())
    
    r1 = ReflectionRecord(id="1", mission_id="m-1", timestamp=100.0, phase="post", content="Investigating file cleanup failures", tags=[])
    r2 = ReflectionRecord(id="2", mission_id="m-1", timestamp=101.0, phase="post", content="File cleanup succeeded after adjusting permissions", tags=[])

    clusterer.add_reflection(r1)
    clusterer.add_reflection(r2)
    clusters = clusterer.build_clusters(mission_id="m-1")

    assert len(clusters) >= 1
    assert clusters[0]["size"] == 2
    assert "Summary of 2 items" in clusters[0]["summary"]
    print("test_reflection_clustering_basic passed")

def test_embedding_storage_and_search():
    from omniverobrix.sovereign.embeddings import SimpleEmbedder
    from omniverobrix.sovereign.memory_embeddings import MemoryEmbeddingManager
    
    # We can reuse the sqlite db we use for clustering or create a new one. 
    # For testing, we just need any object with a cursor() and commit() method.
    db = sqlite3.connect(":memory:")
    mgr = MemoryEmbeddingManager(SimpleEmbedder(), db)
    mgr.add("mission1", "reflection", "cleanup succeeded")
    mgr.add("mission1", "reflection", "cleanup failed due to permissions")

    results = mgr.search("cleanup")
    assert len(results) == 2
    print("test_embedding_storage_and_search passed")

def test_resource_anomaly_detection():
    from omniverobrix.sovereign.anomalies import AnomalyDetector
    detector = AnomalyDetector(
        resource_thresholds={"cpu_percent": 10},
        behavior_thresholds={}
    )
    observation = {
        "environment": type("E", (), {
            "resources": {"cpu_percent": 50, "memory_mb": 100}
        })()
    }
    anomalies = detector._resource_anomalies(observation)
    assert any(a.kind == "resource" for a in anomalies)
    print("test_resource_anomaly_detection passed")

def test_reasoning_chain_records_all_phases():
    from omniverobrix.sovereign.reasoning_chain_manager import ReasoningChainManager
    db = sqlite3.connect(":memory:")
    clusterer = ReflectionClusterer(embedder=FakeEmbedder(), storage=db, reasoner=FakeReasoner())

    loop = AutonomyLoop(
        reasoner=FakeReasoner(),
        planner=FakePlanner(),
        scheduler=FakeScheduler(),
        reflection_clusterer=clusterer,
        chain_manager=ReasoningChainManager(db)
    )
    
    context = AutonomyContext(
        mission_state=MissionState(id="m-100", status="active"),
        environment=create_fake_env(),
        operator_channel=OperatorChannel()
    )
    
    state, chain = loop.run_with_chain(context)
    phases = [step.phase for step in chain.steps]
    assert phases == ["observe", "think", "plan", "act", "reflect", "learn"]
    print("test_reasoning_chain_records_all_phases passed")

def test_chain_synthesis_basic():
    from omniverobrix.sovereign.chain_synthesis import ChainSynthesisManager
    from omniverobrix.sovereign.reasoning_chain_manager import ReasoningChainManager
    
    db = sqlite3.connect(":memory:")
    cm = ReasoningChainManager(db)
    
    chain = cm.start_chain("mission-sync", "cycle-1")
    chain.add("observe", "test")
    cm.persist(chain)
    
    mgr = ChainSynthesisManager(cm, FakeEmbedder(), FakeReasoner())
    result = mgr.synthesize("mission-sync")
    assert result.cycles_analyzed == 1
    assert isinstance(result.summary, str)
    assert len(result.themes) == 2
    print("test_chain_synthesis_basic passed")

def test_cockpit_bus_receives_telemetry():
    from omniverobrix.sovereign.cockpit_bus import CockpitBus
    db = sqlite3.connect(":memory:")
    clusterer = ReflectionClusterer(embedder=FakeEmbedder(), storage=db, reasoner=FakeReasoner())

    bus = CockpitBus()
    received = []
    bus.subscribe(lambda t: received.append(t))

    loop = AutonomyLoop(
        reasoner=FakeReasoner(),
        planner=FakePlanner(),
        scheduler=FakeScheduler(),
        reflection_clusterer=clusterer,
        cockpit_bus=bus
    )
    
    context = AutonomyContext(
        mission_state=MissionState(id="m-100", status="active"),
        environment=create_fake_env(),
        operator_channel=OperatorChannel()
    )
    
    loop.run(context)
    
    assert len(received) == 1
    assert "cycle_id" in received[0]
    print("test_cockpit_bus_receives_telemetry passed")

if __name__ == "__main__":
    test_environment_snapshot_basic()
    test_embedding_storage_and_search()
    test_resource_anomaly_detection()
    test_autonomy_cycle_runs()
    test_safety_rule_iteration_cap()
    test_reflection_clustering_basic()
    test_reasoning_chain_records_all_phases()
    test_chain_synthesis_basic()
    test_cockpit_bus_receives_telemetry()
    print("All tests passed!")
