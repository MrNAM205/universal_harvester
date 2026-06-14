# universal_harvester/agent/sidebar_clicker.py
from playwright.async_api import Page, TimeoutError

class SidebarClicker:
    """Handles robust click interactions in the Copilot UI sidebar."""
    def __init__(self, page: Page):
        self.page = page

    async def click_chat_by_index(self, index: int) -> bool:
        """Clicks a specific chat item in the sidebar."""
        try:
            chat_items = self.page.locator('[data-testid="chat-history-item"], div[role="option"]')
            await chat_items.nth(index).scroll_into_view_if_needed()
            await self.page.wait_for_timeout(200)
            await chat_items.nth(index).click()
            return True
        except Exception as e:
            print(f"[SidebarClicker] Failed to click chat index {index}: {e}")
            return False