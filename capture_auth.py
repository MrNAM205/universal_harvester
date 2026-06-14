# capture_auth.py
from playwright.sync_api import sync_playwright
import json
import os
from dotenv import load_dotenv

load_dotenv()

PROFILE = os.environ.get("CHROME_PROFILE_PATH", r"C:\Users\Sir\AppData\Local\Google\Chrome\User Data\Default")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(PROFILE, headless=False)
        page = browser.new_page()
        page.goto("https://copilot.microsoft.com", timeout=60000)

        logs = []

        def on_request(request):
            url = request.url
            if "clarity" in url or "telemetry" in url or "assets" in url:
                return  # Ignore noise
            print(f"Captured [{request.resource_type}]: {url[:100]}...")
            logs.append({
                "url": url,
                "headers": request.headers,
                "method": request.method,
                "type": request.resource_type
            })

        page.on("request", on_request)

        print("Waiting for Copilot to fully load...")
        page.wait_for_timeout(10000)

        print("\n*** ACTION REQUIRED ***")
        print("1. Click one of your chats manually in the sidebar.")
        print("2. Wait for the messages to load.")
        print("Waiting 30 seconds to capture the request...\n")
        page.wait_for_timeout(30000)

        with open("copilot_auth.json", "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

        print("Saved auth info to copilot_auth.json")
        browser.close()

if __name__ == "__main__":
    main()