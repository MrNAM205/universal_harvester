# universal_harvester/agent/harvester.py
import socket
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

from universal_harvester.agent.detector import detect_page_type
from universal_harvester.agent.scraper import adaptive_scrape
from universal_harvester.agent.navigator import Navigator

def is_port_open(host: str = "127.0.0.1", port: int = 9222) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


class UniversalHarvester:
    def __init__(self, headed: bool = True, user_data_dir: Optional[str] = None):
        self.headed = headed
        self.user_data_dir = user_data_dir

    def _attach_page(self):
        raise RuntimeError("Harvester._attach_page() is deprecated in CDP/parallel mode.")

    def _detach_page(self):
        """Helper to clean up a standalone CDP attachment."""
        if hasattr(self, '_browser'): self._browser.close()
        if hasattr(self, '_pw'): self._pw.stop()

    def harvest(self, url: str) -> Dict[str, Any]:
        print("[HARVESTER DIAGNOSTICS] Checking port 9222...")
        if not is_port_open("localhost", 9222):
            print("\n❌ Remote debugging is NOT running.")
            print("➡️  You MUST launch Chrome manually first:")
            print('   chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\ChromeDebug"\n')
            return {"error": "Port 9222 not open. Launch Chrome with remote debugging."}

        print("[HARVESTER DIAGNOSTICS] Port 9222 open: YES")
        print(f"[HARVESTER DIAGNOSTICS] Profile path detected: {self.user_data_dir if self.user_data_dir else 'None'}")
        print("[HARVESTER] Attaching to existing Edge session via CDP...")

        with sync_playwright() as p:
            try:
                browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                # Use the existing context and the existing tab where Copilot is already open.
                # This prevents the Service Worker from blocking navigation.
                context = browser.contexts[0]
                page = context.pages[0]
                print("[HARVESTER DIAGNOSTICS] Attach attempt: SUCCESS")
                print(f"[HARVESTER DIAGNOSTICS] Browser version detected: {browser.version}")
            except Exception as e:
                print(f"[HARVESTER DIAGNOSTICS] Attach attempt: FAIL ({e})")
                raise

            print("[HARVESTER] Syncing with existing tab...")
            page.bring_to_front()
            page.wait_for_timeout(500)

            if "copilot.microsoft.com" in url:
                from universal_harvester.agent.copilot_scraper import harvest_all_chats, _extract_chat_messages, _log
                from universal_harvester.agent.chat_enhancer import format_transcript, embed_messages
                
                if page.url != url:
                    page.goto(url, wait_until="domcontentloaded")
                    page.wait_for_timeout(1000)

                clean_url = page.url.split("?")[0].rstrip("/")
                if "/chats/" in clean_url and not clean_url.endswith("/chats"):
                    _log("Single-chat export mode: Skipping sidebar enumeration.")
                    messages = _extract_chat_messages(page)
                    chat_id = clean_url.rsplit("/", 1)[-1]
                    result = {
                        "mode": "single_chat",
                        "source": "copilot.microsoft.com",
                        "chat_id": chat_id,
                        "url": clean_url,
                        "messages": messages,
                    }

                    # --- C: Add transcript ---
                    result["transcript_markdown"] = format_transcript(result)

                    # --- D: Add embeddings ---
                    result = embed_messages(result)
                else:
                    # ========================================================
                    # TRUE HYBRID HARVESTER: Merge & Deduplicate
                    # ========================================================
                    _log("Multi-chat true hybrid export mode initialized.")
                    
                    api_results = []
                    try:
                        from universal_harvester.agent.copilot_api import fetch_chat_list_via_api, fetch_chat_messages_via_api
                        _log("Attempting fast-path API extraction...")
                        api_chats = fetch_chat_list_via_api()
                        
                        for c in api_chats:
                            msgs = fetch_chat_messages_via_api(c["id"])
                            # Normalize the ID key so it matches UI structure
                            c["chat_id"] = c.get("id")
                            c["messages"] = msgs
                            api_results.append(c)
                            
                        mode = "multi_chat_api"
                        _log("API extraction fully successful.")
                    except Exception as api_err:
                        _log(f"API fast-path partial or total failure ({api_err}). Flagging for UI fallback...")
                        mode = "multi_chat_hybrid_fallback"

                    ui_chats = []
                    if mode == "multi_chat_hybrid_fallback":
                        _log("Executing UI scraper to fill gaps...")
                        ui_result = harvest_all_chats(page, url)
                        ui_chats = ui_result.get("chats", [])
                        
                    # --- Merge & Deduplicate Logic ---
                    merged_dict = {}
                    for c in api_results:
                        merged_dict[c.get("chat_id")] = c
                    for c in ui_chats:
                        cid = c.get("chat_id")
                        if cid and cid not in merged_dict:
                            merged_dict[cid] = c
                            
                    merged_chats = list(merged_dict.values())

                    result = {
                        "mode": mode,
                        "source": "copilot.microsoft.com",
                        "url": url,
                        "harvested_at": datetime.now(timezone.utc).isoformat(),
                        "chats": merged_chats
                    }
            else:
                navigator = Navigator(page)
                navigator.goto(url)
                analysis = detect_page_type(page)
                result = adaptive_scrape(page, analysis)

            # Cleanup: Do not close the user's existing tab if attached via CDP!
            browser.close()  # Disconnects CDP without killing your Chrome process

            return result
