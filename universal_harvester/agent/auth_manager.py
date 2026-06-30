import asyncio
import os
import json
import requests
from playwright.async_api import async_playwright

COPILOT_BASE = "https://copilot.microsoft.com"
AUTH_FILE = os.environ.get("AUTH_FILE_PATH", "copilot_auth.json")
COOKIE_FILE = os.environ.get("COOKIE_FILE_PATH", "copilot_cookies.json")

def is_auth_valid() -> bool:
    """Check if we have valid cookies and headers to hit the Copilot API."""
    if not os.path.exists(AUTH_FILE) or not os.path.exists(COOKIE_FILE):
        return False
        
    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            auth_data = json.load(f)
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
            
        best_entry = None
        for entry in auth_data:
            url = entry.get("url", "")
            headers = entry.get("headers", {})
            if "/c/api/conversations" in url and "authorization" in headers:
                best_entry = entry
                break
                
        if not best_entry:
            return False
            
        s = requests.Session()
        s.headers.update(best_entry.get("headers", {}))
        for c in cookies:
            s.cookies.set(c["name"], c["value"], domain=c.get("domain"))
            
        resp = s.get(f"{COPILOT_BASE}/c/api/conversations", params={"types": "chat"}, timeout=5)
        if resp.status_code == 200:
            return True
        return False
    except Exception as e:
        print(f"[AUTH] Validation error: {e}")
        return False

async def ensure_authenticated():
    """Ensure we have valid authentication, prompting the user via Playwright if necessary."""
    if is_auth_valid():
        print("[AUTH] Existing authentication is valid.")
        return

    print("\n" + "="*60)
    print("⚠️ AUTHENTICATION REQUIRED ⚠️")
    print("Your Copilot session has expired or is missing.")
    print("A browser will now open. Please log in to Microsoft Copilot.")
    print("The pipeline will automatically resume once login is detected.")
    print("="*60 + "\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        captured_auth_entries = []
        
        async def handle_request(route, request):
            url = request.url
            if "/c/api/conversations" in url:
                headers = await request.all_headers()
                if "authorization" in headers:
                    entry = {
                        "url": url,
                        "method": request.method,
                        "headers": headers
                    }
                    captured_auth_entries.append(entry)
            await route.continue_()
            
        await page.route("**/*", handle_request)
        await page.goto(f"{COPILOT_BASE}/chats")
        
        print("[AUTH] Waiting for successful login and API handshake...")
        
        auth_success = False
        while not auth_success:
            await asyncio.sleep(2)
            try:
                cookies = await context.cookies()
                has_auth_cookie = any(c["name"] == "_C_Auth" for c in cookies)
                has_headers = len(captured_auth_entries) > 0
                
                # Try clicking sidebar to trigger API requests if we have the auth cookie but no headers
                if has_auth_cookie and not has_headers:
                    try:
                        await page.locator("a[href*='/chats']").first.click(timeout=1000)
                    except:
                        pass
                
                if has_auth_cookie and has_headers:
                    print("[AUTH] ✅ Login detected! Capturing session data...")
                    
                    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
                        json.dump(cookies, f, indent=2)
                        
                    with open(AUTH_FILE, "w", encoding="utf-8") as f:
                        json.dump(captured_auth_entries, f, indent=2)
                        
                    auth_success = True
            except Exception as e:
                pass
                
        await browser.close()
        print("[AUTH] Session captured successfully. Resuming pipeline...\n")
