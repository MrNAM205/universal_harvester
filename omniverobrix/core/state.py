from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class SafetyRules:
    max_iterations: Optional[int] = None
    max_errors: Optional[int] = None
    max_runtime_seconds: Optional[float] = None
    resource_caps: Optional[Dict[str, float]] = None
    deadlines: Optional[Dict[str, float]] = None

@dataclass
class MissionState:
    id: str
    status: str = "active"
    iterations: int = 0
    error_count: int = 0
    runtime_seconds: float = 0.0

    def snapshot(self) -> Dict[str, Any]:
        return {"id": self.id, "status": self.status, "iterations": self.iterations}

    def is_complete(self) -> bool:
        return self.status == "completed"

    def is_at_cluster_checkpoint(self) -> bool:
        # Mock logic: trigger clustering if status is a checkpoint
        return self.status == "cluster_checkpoint"

@dataclass
class MemoryLayer:
    reflections: List[Any] = field(default_factory=list)

    def snapshot(self) -> Dict[str, Any]:
        return {"reflection_count": len(self.reflections)}

    def store_reflection(self, reflection: Any):
        self.reflections.append(reflection)

    def commit(self):
        pass

from omniverobrix.sovereign.environment import EnvironmentModel
from omniverobrix.sovereign.operator_channel import OperatorChannel

@dataclass
class AutonomyContext:
    mission_state: MissionState
    memory: MemoryLayer = field(default_factory=MemoryLayer)
    environment: Optional[EnvironmentModel] = None
    safety_rules: SafetyRules = field(default_factory=SafetyRules)
    operator_channel: Optional[OperatorChannel] = None

@dataclass
class AutonomyState:
    status: str
    last_reflection: Dict[str, Any]

@dataclass
class StepResult:
    action_type: str
    success: bool
    data: Dict[str, Any]
