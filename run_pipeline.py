# run_pipeline.py — Unified Universal Harvester Pipeline

import argparse
import asyncio
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Import our dynamically generated modules
from universal_harvester.agent.endpoint_detection import detect_all_endpoints
from universal_harvester.agent.sidebar_autoscroll import SidebarAutoScroller
from universal_harvester.agent.sidebar_dom_extraction import SidebarDOMExtractor
from universal_harvester.agent.completeness_verification import CompletenessVerifier
from universal_harvester.agent.ui_chat_scroll import UIChatScroller
from universal_harvester.agent.merge_engine import merge_messages
from universal_harvester.agent.topic_aggregator import TopicAggregator
from universal_harvester.agent.chat_enhancer import embed_messages

# Import the hardened API clients
from universal_harvester.agent.copilot_api import (
    fetch_chat_list_via_api,
    fetch_chat_messages_via_api,
)

load_dotenv()
PROFILE = os.environ.get("CHROME_PROFILE_PATH", r"C:\Users\Sir\AppData\Local\Google\Chrome\User Data\Default")


def export_to_json(results: List[Dict[str, Any]], output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[PIPELINE] Exported {len(results)} fully harvested chats to {output_file}")


def run_topic_processing(file_path: str = "all_chats_verified.json"):
    print("\n[PIPELINE] Step 6: Running topic embedding + clustering...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            chats = json.load(f)

        aggregator = TopicAggregator(n_clusters=5)
        topics = aggregator.process_and_group(chats)

        print(f"  -> Saving topic groups to topics.json...")
        with open("topics.json", "w", encoding="utf-8") as f:
            json.dump(topics, f, indent=2, ensure_ascii=False)

        print("  -> Topic processing complete.")
        for name, group in topics.items():
            print(f"     - {name}: {len(group)} chats")
    except Exception as e:
        print(f"  [X] Topic processing failed: {e}")

async def main() -> None:
    parser = argparse.ArgumentParser(description="Universal Harvester - Unified Pipeline")
    parser.add_argument(
        "--export",
        default="all_chats_verified.json",
        help="Output JSON file for harvested chats",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Maximum number of parallel workers for message fetching",
    )
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="Enable diagnostic mode to print detailed authentication failure reasons",
    )
    args = parser.parse_args()

    print("\n=======================================================")
    print("⭐ UNIVERSAL HARVESTER PIPELINE STARTING ⭐")
    print("=======================================================\n")

    # STEP 1: Endpoint Detection
    print("[PIPELINE] Step 1: Analyzing captured auth logs...")
    endpoint_profile = detect_all_endpoints()
    print(endpoint_profile.summary())

    # STEP 2: Browser UI Automation
    print("\n[PIPELINE] Step 2: Automating Copilot UI & DOM Extraction...")
    sidebar_chats = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(PROFILE, headless=False)
        page = await browser.new_page()
        print("  -> Loading Copilot UI...")
        await page.goto("https://copilot.microsoft.com", timeout=60000)
        await page.wait_for_timeout(5000)

        print("  -> Triggering Auto-Scroll to force deep archives to load...")
        scroller = SidebarAutoScroller(page)
        scroll_result = await scroller.scroll_until_complete()
        print(f"  -> Scroll finalized after {scroll_result['iterations']} iterations.")

        print("  -> Scraping Sidebar DOM as a secondary source of truth...")
        extractor = SidebarDOMExtractor(page)
        sidebar_chats = await extractor.extract_visible_chats()
        print(f"  -> Extracted {len(sidebar_chats)} chats natively from DOM.")

        # STEP 3: API Initialization 
        print("\n[PIPELINE] Step 3: Engaging Primary API Harvester...")
        try:
            api_chat_list = fetch_chat_list_via_api()
            print(f"  -> Retrieved {len(api_chat_list)} active conversation headers via API.")
        except RuntimeError as e:
            print(f"  [X] API Harvesting Failed: {e}")
            await browser.close()
            return

        results: List[Dict[str, Any]] = []
        api_ids = [c.get("id") for c in api_chat_list if c]
        sidebar_titles = [c["title"] for c in sidebar_chats]

        # STEP 4: Dual-Channel Harvesting & Merging
        print(f"\n[PIPELINE] Step 4: UI Scrolling and API Merging in Progress...")
        
        
        for i, chat in enumerate(api_chat_list, start=1):
            title = chat.get("title") or chat.get("name") or "Untitled"
            cid = chat.get("id") or chat.get("conversationId") or chat.get("chatId")
            
            print(f"  -> [{i}/{len(api_chat_list)}] Harvesting: {title} ({cid})")
            ui_messages = [] # Disabled: API works perfectly and DOM shifted
                
            try:
                api_messages = fetch_chat_messages_via_api(cid)
            except Exception as e:
                print(f"    [X] API Harvest Failed: {e}")
                api_messages = []
                
            final_messages = merge_messages(api_messages, ui_messages)
            
            chat_obj = {"id": cid, "title": title, "messages": final_messages}
            try:
                chat_obj = embed_messages(chat_obj)
            except Exception as e:
                print(f"    [X] Embedding Failed: {e}")
            results.append(chat_obj)
            print(f"    [✓] Merged {len(ui_messages)} UI msgs & {len(api_messages)} API msgs into {len(final_messages)} total.")
            
        # Safely shutdown browser once complete
        await browser.close()

    export_to_json(results, args.export)

    # STEP 5: Completeness Verification
    print("\n[PIPELINE] Step 5: Generating Verification Report...")
    harvested_ids = [c["id"] for c in results]
    report = CompletenessVerifier.verify(
        api_chat_ids=api_ids,
        harvested_chat_ids=harvested_ids,
        sidebar_titles=sidebar_titles,
        endpoint_profile=endpoint_profile.to_dict(),
    )
    print("\n" + report.summary())

    # STEP 6: Topic Processing
    run_topic_processing(args.export)

if __name__ == "__main__":
    asyncio.run(main())
