import time

class Clock:
    def __init__(self):
        self.start = time.time()

    def now(self) -> float:
        return time.time()

    def uptime(self) -> float:
        return time.time() - self.start
