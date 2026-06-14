# universal_harvester/agent/ui_chat_scroll.py

from typing import List, Dict, Any
from playwright.async_api import Page, TimeoutError

CHAT_WINDOW_SELECTORS = [
    'div[data-message-container="true"]',
    '[data-message-container]',
    'div[role="feed"]',
]

COMBINED_MESSAGE_SELECTOR = (
    'div[class*="group/user-message"], [data-message-author="user"], '
    'div[class*="group/ai-message"], [data-message-author="assistant"]'
)

class UIChatScroller:
    """
    Opens a chat, scrolls upward until the very first message loads,
    and extracts all DOM messages in order.
    """
    def __init__(self, page: Page):
        self.page = page

    async def _locate_chat_window(self):
        for sel in CHAT_WINDOW_SELECTORS:
            try:
                win = self.page.locator(sel).first
                await win.wait_for(state="visible", timeout=2000)
                return win
            except TimeoutError:
                continue
        raise RuntimeError("Chat window DOM container not found.")

    async def scroll_to_top(self, chat_window, max_iterations=200):
        """Scroll upward until the scrollHeight stops changing."""
        last_height = None
        stable = 0
        for i in range(max_iterations):
            await chat_window.evaluate("el => el.scrollTop = 0")
            await self.page.wait_for_timeout(500)
            height = await chat_window.evaluate("el => el.scrollHeight")
            if height == last_height:
                stable += 1
            else:
                stable = 0
            if stable >= 3:
                break
            last_height = height
        return i + 1

    async def extract_messages(self) -> List[Dict[str, Any]]:
        """Extract user + assistant messages from the DOM in visual order."""
        messages: List[Dict[str, Any]] = []
        blocks = await self.page.locator(COMBINED_MESSAGE_SELECTOR).all()
        for i, block in enumerate(blocks):
            text = await block.inner_text()
            html = await block.evaluate("el => el.outerHTML")
            role = "user" if "user-message" in html or 'data-message-author="user"' in html else "assistant"
            msg_id = await block.get_attribute("id") or f"{role}-{i}"
            messages.append({"id": msg_id, "role": "role", "text": text.strip()})
        return messages

    async def harvest_chat(self, chat_url: str) -> List[Dict[str, Any]]:
        """Navigate to a chat, scroll to the top, extract all messages."""
        await self.page.goto(chat_url, timeout=30000)
        await self.page.wait_for_timeout(1500)
        chat_window = await self._locate_chat_window()
        await self.scroll_to_top(chat_window)
        return await self.extract_messages()