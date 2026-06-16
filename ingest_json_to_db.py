import json
from pathlib import Path
from universal_harvester.registry import init_db, upsert_chat, upsert_message

JSON_FILE = Path(__file__).parent / "all_chats_verified.json"

def process_messages(chat_id: str, messages: list):
    count = 0
    for msg in messages:
        msg_id = msg.get("id")
        if not msg_id:
            continue
            
        role = msg.get("author", {}).get("type", "unknown")
        created_at = msg.get("createdAt", "")
        
        # Copilot messages are deeply nested
        content_parts = msg.get("content", [])
        text_content = ""
        for part in content_parts:
            if part.get("type") == "text":
                text_content += part.get("text", "") + "\n"
        
        if text_content.strip():
            upsert_message(msg_id, chat_id, role, text_content.strip(), created_at)
            count += 1
            
    return count

def ingest_json():
    print(f"[INGEST] Initializing DB schema...")
    init_db()
    
    if not JSON_FILE.exists():
        print(f"[INGEST] ERROR: Could not find {JSON_FILE}")
        return
        
    print(f"[INGEST] Loading JSON data from {JSON_FILE.name}...")
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[INGEST] ERROR loading JSON: {e}")
        return
        
    total_chats = len(data)
    print(f"[INGEST] Found {total_chats} chats in JSON.")
    
    chats_added = 0
    messages_added = 0
    
    for i, chat in enumerate(data, start=1):
        chat_id = chat.get("id")
        title = chat.get("title", f"Chat {chat_id}")
        
        if not chat_id:
            continue
            
        messages = chat.get("messages", [])
        harvested = 1 if len(messages) > 0 else 0
        
        upsert_chat(chat_id, title, source="api_json", harvested=harvested)
        chats_added += 1
        
        if messages:
            msg_count = process_messages(chat_id, messages)
            messages_added += msg_count
            
        if i % 10 == 0 or i == total_chats:
            print(f"[INGEST] Processed {i}/{total_chats} chats...")

    print("-" * 40)
    print(f"[INGEST] COMPLETE.")
    print(f"[INGEST] Total Chats Updated: {chats_added}")
    print(f"[INGEST] Total Messages Updated: {messages_added}")
    print("-" * 40)

if __name__ == "__main__":
    ingest_json()
