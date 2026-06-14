# run_auto.py — API-only Copilot Harvester with parallel fetching

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from universal_harvester.agent.copilot_api import (
    fetch_chat_list_via_api,
    fetch_chat_messages_via_api
)


def export_to_json(results: List[Dict[str, Any]], output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[AUTO] Exported {len(results)} chats to {output_file}")


def _fetch_single_chat(chat: Dict[str, Any]) -> Dict[str, Any]:
    """
    Worker function for a single chat: fetch messages and return a normalized record.
    """
    cid = chat.get("id") or chat.get("conversationId") or chat.get("chatId")
    title = chat.get("title") or chat.get("name") or "Untitled"

    if not cid:
        raise RuntimeError(f"Chat entry missing id: {chat}")

    print(f"[AUTO] Fetching messages for: {title} ({cid})")

    time.sleep(0.1)
    messages = fetch_chat_messages_via_api(cid)

    return {
        "id": cid,
        "title": title,
        "type": chat.get("type"),
        "hasUnreadMessages": chat.get("hasUnreadMessages"),
        "group": chat.get("group"),
        "updatedAt": chat.get("updatedAt"),
        "continuedAt": chat.get("continuedAt"),
        "isPinned": chat.get("isPinned"),
        "messages": messages,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--export",
        default="all_chats_api.json",
        help="Output JSON file for harvested chats",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Maximum number of parallel workers for message fetching",
    )
    args = parser.parse_args()

    print("[AUTO] Fetching chat list via API…")
    chat_list = fetch_chat_list_via_api()
    print(f"[AUTO] Found {len(chat_list)} chats via API")

    results: List[Dict[str, Any]] = []

    # Parallel fetching of messages
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        future_to_chat = {
            executor.submit(_fetch_single_chat, chat): chat for chat in chat_list
        }

        for i, future in enumerate(as_completed(future_to_chat), start=1):
            chat = future_to_chat[future]
            title = chat.get("title") or chat.get("name") or "Untitled"
            cid = chat.get("id") or chat.get("conversationId") or chat.get("chatId")

            try:
                record = future.result()
                results.append(record)
                print(f"[AUTO] ({i}/{len(chat_list)}) Completed: {title} ({cid})")
            except Exception as e:
                print(
                    f"[AUTO] ({i}/{len(chat_list)}) ERROR for {title} ({cid}): {e}"
                )

    export_to_json(results, args.export)

if __name__ == "__main__":
    main()
