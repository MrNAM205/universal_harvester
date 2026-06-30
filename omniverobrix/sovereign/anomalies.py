from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class Anomaly:
    kind: str          # "resource", "behavior", "stagnation", "safety"
    severity: str      # "low", "medium", "high", "critical"
    message: str
    data: dict

class AnomalyDetector:
    def __init__(self, resource_thresholds, behavior_thresholds):
        self.resource_thresholds = resource_thresholds
        self.behavior_thresholds = behavior_thresholds

    def detect(self, context, observation, reflection, clusters) -> list[Anomaly]:
        anomalies = []
        anomalies += self._resource_anomalies(observation)
        anomalies += self._behavior_anomalies(context, reflection, clusters)
        return anomalies

    def _resource_anomalies(self, observation):
        anomalies = []
        env_snap = observation.get("environment")
        if not env_snap:
            return anomalies
            
        resources = env_snap.resources

        cpu_cap = self.resource_thresholds.get("cpu_percent", 90)
        mem_cap = self.resource_thresholds.get("memory_mb", 1024)

        if resources.get("cpu_percent", 0) > cpu_cap:
            anomalies.append(Anomaly(
                kind="resource",
                severity="high",
                message="CPU usage above threshold",
                data={"cpu_percent": resources.get("cpu_percent")}
            ))

        if resources.get("memory_mb", 0) > mem_cap:
            anomalies.append(Anomaly(
                kind="resource",
                severity="high",
                message="Memory usage above threshold",
                data={"memory_mb": resources.get("memory_mb")}
            ))

        return anomalies

    def _behavior_anomalies(self, context, reflection, clusters):
        anomalies = []

        # repeated failure / no progress from clusters
        for c in clusters[-3:]:
            summary = c.get("summary", "").lower()
            if "repeated failure" in summary or "no progress" in summary:
                anomalies.append(Anomaly(
                    kind="stagnation",
                    severity="medium",
                    message="Stagnation pattern detected in reflection clusters",
                    data={"cluster_summary": c.get("summary", "")}
                ))

        # too many errors in mission state
        max_errors = self.behavior_thresholds.get("max_errors", 5)
        if context.mission_state.error_count > max_errors:
            anomalies.append(Anomaly(
                kind="behavior",
                severity="high",
                message="Error count above behavioral threshold",
                data={"error_count": context.mission_state.error_count}
            ))

        return anomalies
