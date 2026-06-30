# C:\Users\Sir\Desktop\universal_harvester\interactive_login.py
import json
import os
import sys
from playwright.sync_api import sync_playwright

def main():
    print("=== COPILOT INTERACTIVE COOKIE CAPTURE ===")
    print("Launching headful browser...")
    with sync_playwright() as p:
        # Launch standard headful chromium
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("Navigating to Microsoft Copilot...")
        page.goto("https://copilot.microsoft.com/chats")
        
        print("\n" + "="*60)
        print("ACTION REQUIRED:")
        print("1. In the browser window that just opened, log in to your Microsoft Copilot account.")
        print("2. Make sure you can see your chat history / list of chats.")
        print("3. Once you are fully logged in and ready, return to this terminal and press [ENTER].")
        print("="*60 + "\n")
        
        # Wait for user to press enter in the console
        input("Press [ENTER] here once you are logged in to capture cookies...")
        
        print("\nCapturing cookies from all visited domains...")
        cookies = context.cookies()
        
        # Save to copilot_cookies.json
        cookie_path = "copilot_cookies.json"
        with open(cookie_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)
            
        print(f"[OK] Successfully captured {len(cookies)} cookies and saved to {cookie_path}!")
        
        browser.close()
        
    # Run the validation automatically
    try:
        from cookie_validator import validate_cookies
        validate_cookies()
    except Exception as e:
        print(f"Validation failed: {e}")

if __name__ == "__main__":
    main()
