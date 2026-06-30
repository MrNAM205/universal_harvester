import asyncio
import json
from datetime import datetime


class TelemetryBus:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def publish(self, event_type: str, data: dict):
        payload = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data,
        }
        await self.queue.put(json.dumps(payload))

    async def stream(self):
        while True:
            msg = await self.queue.get()
            yield f"data: {msg}\n\n"
