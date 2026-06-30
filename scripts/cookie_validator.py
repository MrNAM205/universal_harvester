# cookie_validator.py
import json
import time
from pathlib import Path

COOKIE_FILE = Path("copilot_cookies.json")
REQUIRED_COOKIES = {"MUID", "_C_Auth"}

def validate_cookies():
    print("=== COPILOT COOKIE VALIDATOR ===")
    if not COOKIE_FILE.exists():
        print(f"[ERROR] {COOKIE_FILE} not found!")
        return

    try:
        with COOKIE_FILE.open("r", encoding="utf-8") as f:
            cookies = json.load(f)
    except json.JSONDecodeError:
        print(f"[ERROR] {COOKIE_FILE} contains invalid JSON.")
        return

    print(f"Total cookies loaded: {len(cookies)}")
    if len(cookies) == 0:
        print("[ERROR] Cookie file is empty.")
        return

    found_names = {c.get("name") for c in cookies}
    missing = REQUIRED_COOKIES - found_names

    if missing:
        print(f"[ERROR] Missing required cookies: {', '.join(missing)}")
    else:
        print(f"[OK] Required cookies present ({', '.join(REQUIRED_COOKIES)}).")

    now = time.time()
    expired = [c.get("name") for c in cookies if c.get("expires", -1) != -1 and c.get("expires", 0) < now]
    
    if expired:
        print(f"[WARN] {len(expired)} cookies have expired: {', '.join(expired[:5])}...")
    else:
        print("[OK] No expired cookies detected.")

    print("================================")
    if not missing and not expired and len(cookies) > 10:
        print("[OK] Cookies look GOOD. Authentication should succeed.")
    else:
        print("[ERROR] Cookies look BAD. Please re-run export_cookies.py.")

if __name__ == "__main__":
    validate_cookies()