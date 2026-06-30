# C:\Users\Sir\Desktop\universal_harvester\inspect_sidebar.py
from playwright.sync_api import sync_playwright
import json
import os

def main():
    print("=== INSPECTING SIDEBAR ===")
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
        
        print("Finding all 'a' tags containing '/chats/'...")
        links = page.locator('a').all()
        matching_links = []
        for l in links:
            try:
                href = l.get_attribute("href") or ""
                text = l.inner_text().strip()
                if "/chats/" in href or "chats" in href:
                    matching_links.append((href, text, l.evaluate("el => el.outerHTML")))
            except:
                pass
                
        print(f"Found {len(matching_links)} matching links:")
        for href, text, html in matching_links:
            print(f"Href: {href!r} | Text: {text!r}")
            print(f"HTML: {html[:200]}...")
            print("-" * 40)
            
        browser.close()

if __name__ == "__main__":
    main()
