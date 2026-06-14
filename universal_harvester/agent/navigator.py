# universal_harvester/agent/navigator.py
from typing import Optional
from playwright.sync_api import Page


class Navigator:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, url: str, wait_until: str = "networkidle", timeout: int = 30000):
        self.page.goto(url, wait_until=wait_until, timeout=timeout)

    def click(self, selector: str, timeout: int = 10000):
        self.page.click(selector, timeout=timeout)

    def type(self, selector: str, text: str, delay: int = 30):
        self.page.fill(selector, text)
        # or self.page.type(selector, text, delay=delay)

    def wait_for(self, selector: str, timeout: int = 15000):
        self.page.wait_for_selector(selector, timeout=timeout)

    def scroll_to_bottom(self):
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def next_page(self, selector: Optional[str] = None):
        if selector:
            self.page.click(selector)
        else:
            # naive: try a "next" link
            self.page.evaluate(
                """
                () => {
                    const link = Array.from(document.querySelectorAll('a'))
                        .find(a => /next/i.test(a.innerText));
                    if (link) link.click();
                }
                """
            )
