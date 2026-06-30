# C:\Users\Sir\Desktop\universal_harvester\inspect_selector.py
from playwright.sync_api import sync_playwright
import json
import os

def main():
    print("=== TESTING SELECTOR ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        cookie_path = "copilot_cookies.json"
        if os.path.exists(cookie_path):
            with open(cookie_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            
            cleaned_cookies = []
            for c in cookies:
                cleaned = {
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c.get("domain") or "copilot.microsoft.com",
                    "path": c.get("path") or "/",
                    "secure": c.get("secure", True),
                    "httpOnly": c.get("httpOnly", False)
                }
                expires = c.get("expires") or c.get("expirationDate")
                if expires is not None and isinstance(expires, (int, float)) and expires > 0:
                    cleaned["expires"] = float(expires)
                ss = c.get("sameSite")
                if ss and isinstance(ss, str) and ss.lower() in ("lax", "strict", "none"):
                    cleaned["sameSite"] = ss.capitalize()
                elif ss == "no_restriction":
                    cleaned["sameSite"] = "None"
                cleaned_cookies.append(cleaned)
            context.add_cookies(cleaned_cookies)
            
        page = context.new_page()
        page.goto("https://copilot.microsoft.com/chats", timeout=30000)
        page.wait_for_timeout(5000)
        
        # Test our new selector
        selector = 'div[role="link"]:has(button[id^="conversation-options-"])'
        items = page.locator(selector).all()
        print(f"Found {len(items)} chat items using selector: {selector}")
        for i, item in enumerate(items):
            aria_label = item.get_attribute("aria-label") or ""
            # Let's get the text of the first p element inside the item
            p_text = item.locator("p.truncate").first.inner_text().strip() if item.locator("p.truncate").count() > 0 else ""
            print(f"[{i}] Aria-Label: {aria_label!r} | P-Text: {p_text!r}")
            
        browser.close()

if __name__ == "__main__":
    main()
