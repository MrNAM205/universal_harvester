# universal_harvester/agent/chat_enhancer.py
from universal_harvester.agent.topic_embeddings import TopicEmbedder
import os
from dotenv import load_dotenv

load_dotenv()

# Load once, reuse everywhere
try:
    _model = TopicEmbedder()
except Exception as e:
    print(f"[WARNING] TopicEmbedder init failed: {e}")
    _model = None

def format_transcript(chat_json):
    """Return a clean Markdown transcript string."""
    lines = []
    chat_id = chat_json.get('id', chat_json.get('chat_id', 'Unknown'))
    lines.append(f"# Chat Transcript — {chat_id}")
    if 'url' in chat_json:
        lines.append(f"Source: {chat_json['url']}")
    lines.append("")

    for msg in chat_json.get("messages", []):
        # Handle different message formats
        role = "USER"
        if "author" in msg and isinstance(msg["author"], dict):
            role = "USER" if msg["author"].get("type") == "human" else "ASSISTANT"
        elif "role" in msg:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"

        text = ""
        if "text" in msg:
            text = msg["text"]
        elif "content" in msg and isinstance(msg["content"], list) and len(msg["content"]) > 0:
            text = msg["content"][0].get("text", "")

        if not isinstance(text, str):
            text = str(text)

        lines.append(f"## {role}")
        lines.append(text.strip())
        lines.append("")

    return "\n".join(lines)

def embed_messages(chat_json):
    """Add embeddings to each message."""
    texts = []
    for m in chat_json.get("messages", []):
        if "text" in m:
            text_val = m["text"]
        elif "content" in m and isinstance(m["content"], list) and len(m["content"]) > 0:
            text_val = m["content"][0].get("text", "")
        else:
            text_val = ""
            
        if not isinstance(text_val, str):
            text_val = str(text_val)
        texts.append(text_val)
            
    if _model is None:
        return chat_json
        
    vectors = _model.embed(texts)

    for msg, vec in zip(chat_json.get("messages", []), vectors):
        msg["embedding"] = vec.tolist()

    return chat_json
