# export_cookies.py
from playwright.sync_api import sync_playwright
import json
import os
from dotenv import load_dotenv

load_dotenv()

PROFILE = os.environ.get("CHROME_PROFILE_PATH", r"C:\Users\Sir\AppData\Local\Google\Chrome\User Data\Default")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            PROFILE,
            headless=False
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://copilot.microsoft.com", timeout=60000)
        print("Please sign in if prompted. Waiting 60 seconds...")
        page.wait_for_timeout(60000)

        cookies = browser.cookies()
        with open("copilot_cookies.json", "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)

        print("Cookies exported to copilot_cookies.json")
        browser.close()

if __name__ == "__main__":
    main()