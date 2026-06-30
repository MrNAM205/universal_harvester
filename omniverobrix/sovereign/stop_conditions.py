from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class StopDecision:
    status: str        # "continue", "pause", "halt_mission", "halt_global"
    reason: str
    details: Dict[str, Any]

class FakeOperatorChannel:
    def has_hard_halt(self) -> bool:
        return False
        
    def has_pause(self) -> bool:
        return False

class StopConditionEngine:
    def __init__(self, safety_rules: Any, clusterer: Any, operator_channel: Any):
        self.safety_rules = safety_rules
        self.clusterer = clusterer
        self.operator_channel = operator_channel

    def _detect_stagnation(self, context: Any) -> bool:
        # We assume clusterer returns a list of dicts with 'summary'
        clusters = self.clusterer.get_clusters(mission_id=context.mission_state.id)
        if not clusters:
            return False
        
        # heuristic: recent clusters dominated by "retry", "failure", "no progress"
        recent_clusters = clusters[-3:]
        for c in recent_clusters:
            summary = c.get("summary", "").lower()
            if "no progress" in summary or "repeated failure" in summary:
                return True
        return False

    def _violates_safety_rules(self, context: Any) -> bool:
        rules = self.safety_rules
        if not rules:
            return False

        # 1. iteration cap
        if rules.max_iterations is not None:
            if context.mission_state.iterations > rules.max_iterations:
                return True

        # 2. error cap
        if rules.max_errors is not None:
            if context.mission_state.error_count > rules.max_errors:
                return True

        # 3. runtime cap
        if rules.max_runtime_seconds is not None:
            if context.mission_state.runtime_seconds > rules.max_runtime_seconds:
                return True

        # 4. resource caps
        if rules.resource_caps:
            env = context.environment.snapshot()
            for key, cap in rules.resource_caps.items():
                if env.get(key, 0) > cap:
                    return True

        # 5. deadlines
        if rules.deadlines:
            now = context.environment.now()
            for name, deadline in rules.deadlines.items():
                if now > deadline:
                    return True

        return False

    def evaluate(self, context: Any, reflection: Dict[str, Any], anomalies: List[Any] = None) -> StopDecision:
        # 0. Anomalies
        if anomalies:
            for a in anomalies:
                if getattr(a, "severity", "") in ("critical", "high"):
                    return StopDecision("halt_global", f"critical_anomaly: {getattr(a, 'kind', 'unknown')}", getattr(a, 'data', {}))

        # 1. Operator overrides
        if self.operator_channel.has_hard_halt():
            return StopDecision("halt_global", "operator_halt", {})

        if self.operator_channel.has_pause():
            return StopDecision("pause", "operator_pause", {})

        # 2. Mission completion
        if context.mission_state.is_complete():
            return StopDecision("halt_mission", "mission_complete", {})

        # 3. Reflection flags
        if reflection.get("halt"):
            return StopDecision("halt_mission", "reflection_requested_halt", {})

        if reflection.get("unsafe"):
            return StopDecision("halt_global", "unsafe_condition", {})

        # 4. Cluster-based stagnation / failure
        if self._detect_stagnation(context):
            return StopDecision("pause", "stagnation_detected", {})

        # 5. Safety rules
        if self._violates_safety_rules(context):
            return StopDecision("halt_global", "safety_violation", {})

        # 6. Default: continue
        return StopDecision("continue", "no_stop_condition_met", {})
