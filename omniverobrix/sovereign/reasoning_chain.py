from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ReasoningStep:
    phase: str          # "observe", "think", "plan", "act", "reflect", "learn"
    content: str
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReasoningChain:
    mission_id: str
    cycle_id: str
    steps: List[ReasoningStep] = field(default_factory=list)

    def add(self, phase: str, content: str, data: Optional[Dict[str, Any]] = None):
        self.steps.append(ReasoningStep(phase=phase, content=content, data=data or {}))
