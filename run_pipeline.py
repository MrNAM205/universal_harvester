# run_pipeline.py — Minimal Chat Harvester
import sys

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
from universal_harvester.agent.auth_manager import ensure_authenticated
from universal_harvester.agent.copilot_api import (
    fetch_chat_list_via_api,
    fetch_chat_messages_via_api,
)
from db import init_db, save_conversation, save_message
import asyncio

async def harvest_all_chats():
    print("[HARVEST] Initializing SQLite database...")
    init_db()

    print("[HARVEST] Fetching conversation list...")
    conversations = fetch_chat_list_via_api()

    print(f"[HARVEST] Found {len(conversations)} conversations.")

    for conv in conversations:
        if not conv:
            continue
            
        conv_id = conv.get("id") or conv.get("conversationId") or conv.get("chatId")
        if not conv_id:
            continue
            
        title = conv.get("title") or conv.get("name") or "Untitled"
        created_at = conv.get("created_at", 0)

        print(f"[HARVEST] Harvesting conversation {conv_id} ({title})")

        # Save conversation metadata
        save_conversation(conv_id, title, created_at)

        # Fetch full history
        try:
            api_messages = fetch_chat_messages_via_api(conv_id)
        except Exception as e:
            print(f"    [X] Failed to fetch history: {e}")
            continue

        msg_index = 0
        for msg in api_messages:
            msg_id = msg.get("id", "")
            role = msg.get("role", "unknown")
            content = msg.get("text", "")
            timestamp = msg.get("createdAt", 0)

            save_message(msg_id, conv_id, role, content, timestamp, msg_index)
            msg_index += 1

        print(f"[HARVEST] Saved {msg_index} messages for {conv_id}")

    print("[HARVEST] Complete.")

async def main():
    print("=======================================================")
    print("*** UNIVERSAL HARVESTER (MINIMAL MODE) STARTING ***")
    print("=======================================================\n")
    
    print("[PIPELINE] Ensuring authentication is valid...")
    await ensure_authenticated()
    
    await harvest_all_chats()

if __name__ == "__main__":
    asyncio.run(main())
