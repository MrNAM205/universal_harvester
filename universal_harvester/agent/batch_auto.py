# universal_harvester/agent/batch_auto.py
import os
import glob
import re
from pathlib import Path
from multiprocessing import Pool, cpu_count
from dotenv import load_dotenv

load_dotenv()

def autodetect_chrome_profile():
    # 1. Respect .env explicitly
    env_profile = os.environ.get("CHROME_PROFILE_PATH")
    if env_profile and Path(env_profile).exists():
        print(f"[AUTO] Using Chrome profile from .env: {env_profile}")
        return str(env_profile)
        
    base = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
    if not base.exists():
        raise RuntimeError("Chrome not installed.")

    profiles = [p for p in base.iterdir() if p.is_dir()]
    copilot_profiles = []

    for profile in profiles:
        cookie_file = profile / "Network" / "Cookies"
        if not cookie_file.exists():
            cookie_file = profile / "Cookies"
        if not cookie_file.exists():
            continue

        try:
            data = cookie_file.read_bytes().decode("latin-1", errors="ignore")
            if "copilot.microsoft.com" in data:
                copilot_profiles.append(profile)
        except:
            continue

    if copilot_profiles:
        # Prefer non-Default if multiple
        copilot_profiles = sorted(copilot_profiles, key=lambda p: "Default" in p.name)
        chosen = copilot_profiles[0]
        print(f"[AUTO] Found Copilot cookies in Chrome profile: {chosen}")
        return str(chosen)

    # Fallback: Default
    default = base / "Default"
    if default.exists():
        print("[AUTO] WARNING: No Copilot cookies detected; falling back to Default.")
        return str(default)

    raise RuntimeError("No Chrome profiles contain Copilot cookies.")

def autodetect_copilot_indexeddb(profile_path):
    if not profile_path: return None
    indexeddb_root = Path(profile_path) / "IndexedDB"
    pattern = "*copilot.microsoft.com*.indexeddb.leveldb"
    matches = list(indexeddb_root.rglob(pattern))
    return str(matches[0]) if matches else None

def load_chat_urls_from_indexeddb(indexeddb_path):
    if not indexeddb_path or not os.path.exists(indexeddb_path):
        return []
    
    chat_ids = set()
    files_to_scan = glob.glob(os.path.join(indexeddb_path, "*.ldb")) + \
                    glob.glob(os.path.join(indexeddb_path, "*.log"))
                    
    for file_path in files_to_scan:
        try:
            with open(file_path, "rb") as f:
                data = f.read().decode("latin-1", errors="ignore")
                urls = re.findall(r'https://copilot\.microsoft\.com/chats/([a-zA-Z0-9_-]+)', data)
                chat_ids.update(urls)
                ids = re.findall(r'"(?:chatId|id|conversationId|cvid)"\s*:\s*"([a-zA-Z0-9_-]{15,40})"', data)
                chat_ids.update(ids)
        except:
            continue
    return [f"https://copilot.microsoft.com/chats/{cid}" for cid in sorted(chat_ids)]

def harvest_worker(args):
    url, profile_path = args
    from playwright.sync_api import sync_playwright
    from universal_harvester.agent.copilot_scraper import extract_messages_cdp

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, timeout=60000)
        page.wait_for_timeout(1200)

        messages = extract_messages_cdp(page)

        browser.close()

    return {
        "url": url,
        "messages": messages
    }

def harvest_parallel(urls, profile_path):
    workers = max(2, cpu_count() - 1)
    print(f"[AUTO] Using {workers} parallel workers")

    args = [(url, profile_path) for url in urls]

    with Pool(workers) as pool:
        results = pool.map(harvest_worker, args)

    return results