# universal_harvester/agent/merge_engine.py

from typing import List, Dict, Any

def merge_messages(api_messages: List[Dict[str, Any]], ui_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merges API and UI messages. Prioritizes UI for text completeness
    and attempts to graft timestamps from matching API messages.
    """
    if not ui_messages:
        return api_messages
    if not api_messages:
        return ui_messages
        
    merged = []
    api_idx = 0
    
    for ui_msg in ui_messages:
        ui_text = ui_msg.get("text", "").strip()
        matched_api = None
        
        # Scan a sliding window of API messages to find a match
        for i in range(api_idx, min(api_idx + 6, len(api_messages))):
            api_text = api_messages[i].get("text", "").strip()
            # Basic match heuristics
            if api_text in ui_text or ui_text in api_text or len(set(ui_text.split()) & set(api_text.split())) > 6:
                matched_api = api_messages[i]
                api_idx = i + 1
                break
        
        new_msg = ui_msg.copy()
        if matched_api:
            new_msg["createdAt"] = matched_api.get("createdAt", "")
            new_msg["api_id"] = matched_api.get("id", "")
            
        merged.append(new_msg)
        
    return merged