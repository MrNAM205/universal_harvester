# export_cookies_fixed.py
import os
import sys
import json
import time
import subprocess
from playwright.sync_api import sync_playwright

def kill_process(name):
    print(f"[FIX] Killing any running {name} processes...")
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", f"{name}.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error killing {name}: {e}")

def try_export(user_data_dir, profile_name=None, channel=None):
    print(f"\n[FIX] Attempting export using user_data_dir: {user_data_dir} (profile={profile_name}, channel={channel})")
    
    args = []
    if profile_name:
        args.append(f"--profile-directory={profile_name}")
        
    with sync_playwright() as p:
        try:
            print("[FIX] Launching browser in HEADFUL mode...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir,
                channel=channel,
                args=args,
                ignore_default_args=["--use-mock-keychain", "--password-store=basic"],
                headless=False
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            print("[FIX] Navigating to copilot.microsoft.com/chats...")
            page.goto("https://copilot.microsoft.com/chats", timeout=30000)
            
            try:
                print("[FIX] Waiting up to 25 seconds for authenticated URL (/chats)...")
                page.wait_for_url(lambda url: "/chats" in url.lower(), timeout=25000)
                print(f"[FIX] SUCCESS: Authenticated URL detected: {page.url}")
                page.wait_for_timeout(2000) # Wait 2s for cookies to fully settle
                cookies = browser.cookies()
                browser.close()
                return cookies
            except Exception as wait_err:
                print(f"[FIX] Timeout or wait failed: {wait_err}")
                print(f"[FIX] Current Page Title: {page.title()}")
                print(f"[FIX] Current URL: {page.url}")
                browser.close()
            
        except Exception as e:
            print(f"[FIX] Failed with error: {e}")
            
    return None

def main():
    chrome_dir = r"C:\Users\Sir\AppData\Local\Google\Chrome\User Data"
    edge_dir = r"C:\Users\Sir\AppData\Local\Microsoft\Edge\User Data"
    
    cookies = None
    
    # 1. Try Edge Default (since Edge is the user's primary running browser)
    kill_process("msedge")
    time.sleep(2)
    cookies = try_export(edge_dir, profile_name="Default", channel="msedge")
    
    # 2. Try Chrome Default
    if not cookies:
        kill_process("chrome")
        time.sleep(2)
        cookies = try_export(chrome_dir, profile_name="Default")
        
    # 3. Try Chrome Profile 1
    if not cookies:
        cookies = try_export(chrome_dir, profile_name="Profile 1")
        
    if cookies:
        with open("copilot_cookies.json", "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)
        print("\n[FIX] Successfully exported cookies to copilot_cookies.json!")
        
        # Verify
        from cookie_validator import validate_cookies
        validate_cookies()
    else:
        print("\n[FIX] ERROR: Could not extract valid cookies from Chrome or Edge profile.")
        print("Please ensure you are signed in to Microsoft Copilot in your normal browser first.")

if __name__ == "__main__":
    main()
