# universal_harvester/agent/sidebar_autoscroll.py

from typing import Dict, Any
from playwright.async_api import Page, TimeoutError

SIDEBAR_SELECTORS = [
    '[data-testid="chat-history-list"]',
    'div[role="list"]',
]


class SidebarAutoScroller:
    def __init__(self, page: Page):
        self.page = page

    async def scroll_until_complete(self, max_iterations: int = 200) -> Dict[str, Any]:
        sidebar = None
        for sel in SIDEBAR_SELECTORS:
            try:
                sidebar = self.page.locator(sel).first
                await sidebar.wait_for(state="visible", timeout=2000)
                break
            except TimeoutError:
                sidebar = None

        if sidebar is None:
            raise RuntimeError("Sidebar DOM container not found.")

        last_height = -1
        stable = 0
        log = []

        for i in range(max_iterations):
            await sidebar.evaluate("el => el.scrollTop = el.scrollHeight")
            await self.page.wait_for_timeout(500)
            height = await sidebar.evaluate("el => el.scrollHeight")
            log.append({"iteration": i, "height": height})
            stable = stable + 1 if height == last_height else 0
            if stable >= 3: break
            last_height = height
        return {"iterations": len(log), "log": log}