# C:\Users\Sir\Desktop\universal_harvester\test_ui_harvest.py
from playwright.sync_api import sync_playwright
from universal_harvester.agent.copilot_scraper import harvest_all_chats
import json
import os

def main():
    print("=== STARTING TEST UI HARVEST ===")
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
                
                # Format sameSite correctly for Playwright
                ss = c.get("sameSite")
                if ss and isinstance(ss, str) and ss.lower() in ("lax", "strict", "none"):
                    cleaned["sameSite"] = ss.capitalize()
                elif ss == "no_restriction":
                    cleaned["sameSite"] = "None"
                    
                cleaned_cookies.append(cleaned)
                
            context.add_cookies(cleaned_cookies)
            print(f"Loaded and cleaned {len(cleaned_cookies)} cookies.")
            
        page = context.new_page()
        print("Navigating to Copilot chats page...")
        page.goto("https://copilot.microsoft.com/chats", timeout=45000)
        
        # Wait up to 10 seconds for authentication redirect to settle
        try:
            page.wait_for_url(lambda url: "/login" not in url.lower(), timeout=10000)
        except Exception:
            pass
            
        page.wait_for_timeout(5000)
        
        try:
            print("Current URL:", page.url)
            print("Page Title:", page.title())
        except Exception as e:
            print(f"Could not read page metadata: {e}")
        
        # Save a screenshot to verify state
        os.makedirs("exports", exist_ok=True)
        page.screenshot(path="exports/debug_ui_harvest_start.png")
        print("Saved start screenshot to exports/debug_ui_harvest_start.png")
        
        print("Starting UI harvest for all visible chats...")
        results = harvest_all_chats(page)
        
        with open("ui_harvest_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        print("Done! Results saved to ui_harvest_results.json.")
        browser.close()

if __name__ == "__main__":
    main()
