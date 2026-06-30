# C:\Users\Sir\Desktop\universal_harvester\inspect_elements.py
from playwright.sync_api import sync_playwright
import json
import os

def main():
    print("=== INSPECTING PARENT CHAIN ===")
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
        
        # Search for elements containing "Comparing"
        print("Searching for elements containing 'Comparing'...")
        p_element = page.locator("p.truncate:has-text('Comparing')").first
        if p_element.count() > 0:
            # Let's inspect the parent chain up to 5 levels
            chain = p_element.evaluate("""el => {
                let current = el;
                let results = [];
                for (let i = 0; i < 5; i++) {
                    if (!current) break;
                    results.push({
                        level: i,
                        tagName: current.tagName,
                        className: current.className,
                        id: current.id,
                        outerHTML: current.outerHTML.substring(0, 300)
                    });
                    current = current.parentElement;
                }
                return results;
            }""")
            for node in chain:
                print(f"Level {node['level']}: Tag={node['tagName']} | Class={node['className']} | ID={node['id']}")
                print(f"  HTML: {node['outerHTML']}...")
                print("-" * 50)
        else:
            print("No matching p element found.")

        browser.close()

if __name__ == "__main__":
    main()
