from dataclasses import dataclass

@dataclass
class EnvironmentSnapshot:
    time: float
    uptime: float
    resources: dict
    operator: dict
    events: list

class EnvironmentModel:
    def __init__(self, resource_monitor, clock, operator_channel, event_buffer):
        self.resource_monitor = resource_monitor
        self.clock = clock
        self.operator_channel = operator_channel
        self.event_buffer = event_buffer

    def snapshot(self) -> EnvironmentSnapshot:
        now = self.clock.now()
        return EnvironmentSnapshot(
            time=now,
            uptime=self.clock.uptime(),
            resources=self.resource_monitor.snapshot(),
            operator=self.operator_channel.snapshot(),
            events=self.event_buffer.last(10),
        )

    def now(self) -> float:
        return self.clock.now()
