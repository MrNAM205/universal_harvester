import asyncio
from playwright.async_api import Page

SIDEBAR = "div[data-testid='sidebar-expanded-content']"
CHAT_ROW = "div[data-testid='sidebar-expanded-content'] div[role='link']"

class SidebarAutoClicker:
    def __init__(self, page: Page):
        self.page = page
        self.clicked = set()

    async def wait_for_sidebar(self):
        print("[AUTOCLICK] Waiting for sidebar to mount...")
        await self.page.wait_for_selector(SIDEBAR, timeout=60000)
        print("[AUTOCLICK] Sidebar detected.")

    async def get_visible_chats(self):
        return await self.page.query_selector_all(CHAT_ROW)

    async def scroll_sidebar(self):
        sidebar = await self.page.query_selector(SIDEBAR)
        await sidebar.evaluate("""
            el => {
                el.scrollBy({ top: el.clientHeight * 0.8, behavior: 'instant' });
            }
        """)

    async def scroll_chat_window(self):
        await self.page.evaluate("""
            () => {
                const el = document.querySelector('[data-testid="conversation-view"]');
                if (el) el.scrollTop = el.scrollHeight;
            }
        """)

    async def click_all_chats(self):
        await self.wait_for_sidebar()

        last_count = -1
        stable_iterations = 0

        while stable_iterations < 4:
            chats = await self.get_visible_chats()

            if len(chats) == last_count:
                stable_iterations += 1
            else:
                stable_iterations = 0

            last_count = len(chats)

            for chat in chats:
                title_el = await chat.query_selector("p.truncate")
                if not title_el:
                    continue

                title = (await title_el.inner_text()).strip()

                if title in self.clicked:
                    continue

                print(f"[AUTOCLICK] Clicking: {title}")
                self.clicked.add(title)

                await chat.click()
                await asyncio.sleep(1.2)

                await self.scroll_chat_window()
                await asyncio.sleep(0.5)

            await self.scroll_sidebar()
            await asyncio.sleep(0.8)

        print(f"[AUTOCLICK] Completed. Total chats clicked: {len(self.clicked)}")
