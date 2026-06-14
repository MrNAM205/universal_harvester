# universal_harvester/agent/sidebar_dom_extraction.py

from typing import List, Dict, Any
from playwright.async_api import Page, TimeoutError

CHAT_ENTRY_SELECTORS = [
    'div[role="link"][aria-label]',
    '[role="link"]',
]

SIDEBAR_SELECTORS = [
    '[data-testid="chat-history-list"]',
    'div[role="list"]',
]


class SidebarDOMExtractor:
    def __init__(self, page: Page):
        self.page = page

    async def extract_visible_chats(self) -> List[Dict[str, Any]]:
        sidebar = None
        for sel in SIDEBAR_SELECTORS:
            try:
                sidebar = self.page.locator(sel).first
                await sidebar.wait_for(state="visible", timeout=2000)
                break
            except TimeoutError:
                sidebar = None

        if sidebar is None:
            return []

        nodes = None
        for sel in CHAT_ENTRY_SELECTORS:
            nodes = sidebar.locator(sel)
            if await nodes.count() > 0:
                break

        if nodes is None:
            return []

        results: List[Dict[str, Any]] = []
        
        # Using modern Playwright .all() instead of count() and nth()
        for i, node in enumerate(await nodes.all()):
            title = await node.get_attribute("aria-label")
            element_id = await node.get_attribute("id")
            data_attrs = await node.evaluate(
                """
                el => {
                    const out = {};
                    for (const attr of el.attributes) {
                        if (attr.name.startsWith("data-")) {
                            out[attr.name] = attr.value;
                        }
                    }
                    return out;
                }
                """
            )
            results.append({"index": i, "title": title, "aria_label": title, "element_id": element_id, "data_attrs": data_attrs})
        return results