import time

class EventBuffer:
    def __init__(self):
        self.events = []

    def push(self, event: dict):
        self.events.append((time.time(), event))

    def last(self, n: int):
        return self.events[-n:]
