# universal_harvester/utils/exporter.py
import os
import re
from typing import Dict, Any

def export_to_markdown(harvest_result: Dict[str, Any], output_dir: str = "exports"):
    """
    Converts a multi-chat harvest JSON payload into individual Markdown files.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    chats = harvest_result.get("chats", [])
    if not chats:
        print("[EXPORTER] No chats found to export.")
        return

    for chat in chats:
        raw_title = chat.get("title", "Untitled")
        # Sanitize the title for safe Windows filenames
        safe_title = re.sub(r'[\\/*?:"<>|]', "", raw_title).strip()
        chat_id = chat.get("chat_id", "unknown_id")
        
        filename = f"{safe_title}_{chat_id}.md"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {raw_title}\n\n")
            f.write(f"**Chat ID:** `{chat_id}`\n\n---\n\n")
            
            for msg in chat.get("messages", []):
                role = "🧑 **You**" if msg.get("role") == "user" else "🤖 **Copilot**"
                f.write(f"{role}:\n\n{msg.get('text', '')}\n\n---\n\n")
                
    print(f"[EXPORTER] Successfully exported {len(chats)} chats to the '{output_dir}' directory.")