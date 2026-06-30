# search_cli.py
import argparse
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="all_chats_auto.json", help="Harvested chats JSON file")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to show")
    args = parser.parse_args()

    print(f"Loading chats from {args.file}...")
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            chats = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {args.file}")
        return

    # Flatten messages with embeddings
    searchable_messages = []
    for chat in chats:
        if "messages" in chat:
            for msg in chat["messages"]:
                if "embedding" in msg and msg["embedding"]:
                    searchable_messages.append({
                        "chat_id": chat.get("chat_id", "Unknown"),
                        "url": chat.get("url", ""),
                        "role": msg.get("role", "unknown"),
                        "text": msg.get("text", ""),
                        "embedding": np.array(msg["embedding"])
                    })
    
    if not searchable_messages:
        print("No messages with embeddings found. Make sure your harvester generated them.")
        return

    print(f"Loaded {len(searchable_messages)} searchable messages.")
    print("Loading embedding model (this might take a few seconds)...")
    model_path = os.environ.get("EMBEDDING_MODEL_PATH", "C:/models/all-MiniLM-L6-v2")
    model = SentenceTransformer(model_path)
    print("Ready! Type your search query below (or 'exit' to quit).")

    while True:
        query = input("\n🔍 Search: ").strip()
        if query.lower() in ['exit', 'quit']:
            break
        if not query:
            continue

        query_vec = model.encode([query])[0]

        # Calculate scores
        scored_messages = []
        for msg in searchable_messages:
            score = cosine_similarity(query_vec, msg["embedding"])
            scored_messages.append((score, msg))

        # Sort by score descending
        scored_messages.sort(key=lambda x: x[0], reverse=True)

        print(f"\n--- Top {args.top_k} Results ---")
        for i, (score, msg) in enumerate(scored_messages[:args.top_k], 1):
            preview = msg['text'][:150].replace('\n', ' ') + ('...' if len(msg['text']) > 150 else '')
            print(f"\n{i}. [Score: {score:.4f}] Role: {msg['role'].upper()}")
            print(f"   Chat ID: {msg['chat_id']}")
            print(f"   URL: {msg['url']}")
            print(f"   Text: {preview}")

if __name__ == "__main__":
    main()