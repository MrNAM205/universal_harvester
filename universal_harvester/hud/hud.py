import time
from datetime import datetime


class HUD:
    def __init__(self, bus=None):
        self.start_time = time.time()
        self.bus = bus

    def section(self, title):
        print("\n" + "=" * 70)
        print(f"[HUD] {title}")
        print("=" * 70)

    def info(self, msg):
        print(f"[HUD] {msg}")

    def kv(self, key, value):
        print(f"[HUD] {key}: {value}")

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def perf(self, label):
        elapsed = time.time() - self.start_time
        print(f"[HUD] PERF: {label} — {elapsed:.2f}s since start")

    async def event(self, name, **details):
        if self.bus:
            await self.bus.publish("event", {"name": name, **details})

    async def info_async(self, msg):
        if self.bus:
            await self.bus.publish("info", {"message": msg})

    async def kv_async(self, key, value):
        if self.bus:
            await self.bus.publish("kv", {key: value})
