import asyncio
import json
import os
from playwright.async_api import async_playwright
from universal_harvester.agent.sidebar_autoclicker import SidebarAutoClicker

PROFILE = os.environ.get('CHROME_PROFILE_PATH', r"C:\Users\Sir\AppData\Local\Google\Chrome\User Data\Default")
AUTH_OUTPUT = "copilot_auth.json"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            PROFILE,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = await browser.new_page()

        captured = []

        def log_request(req):
            url = req.url
            if any(x in url for x in ["conversations", "history", "token"]):
                if "clarity" not in url and "telemetry" not in url and "assets" not in url:
                    print(f"Captured [{req.resource_type}]: {url[:100]}...")
                    captured.append(url)

        page.on("request", log_request)

        print("Waiting for Copilot to fully load...")
        await page.goto("https://copilot.microsoft.com", wait_until="networkidle")

        autoclicker = SidebarAutoClicker(page)
        await autoclicker.click_all_chats()

        print(f"Saving auth info to {AUTH_OUTPUT}")
        with open(AUTH_OUTPUT, "w", encoding="utf-8") as f:
            json.dump({"history_endpoints": captured}, f, indent=2)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
