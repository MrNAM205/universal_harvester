class CockpitBus:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, fn):
        self.subscribers.append(fn)

    def publish(self, telemetry):
        for fn in self.subscribers:
            fn(telemetry)
