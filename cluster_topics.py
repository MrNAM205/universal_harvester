# cluster_topics.py
import argparse
import json
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="all_chats_auto.json", help="Harvested chats JSON file")
    parser.add_argument("--clusters", type=int, default=5, help="Number of topics to group into")
    args = parser.parse_args()

    print(f"Loading chats from {args.file}...")
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            chats = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {args.file}")
        return
    except json.JSONDecodeError:
        print(f"Error: {args.file} contains invalid JSON.")
        return

    chat_embeddings = []
    chat_metadata = []

    for chat in chats:
        if "messages" in chat and len(chat["messages"]) > 0:
            embeddings = [msg["embedding"] for msg in chat["messages"] if "embedding" in msg and msg["embedding"]]
            if embeddings:
                # Average the embeddings of all messages to represent the whole chat
                chat_vec = np.mean(embeddings, axis=0)
                chat_embeddings.append(chat_vec)
                chat_metadata.append({
                    "chat_id": chat.get("chat_id", "Unknown"),
                    "url": chat.get("url", ""),
                    "title": chat.get("title", chat.get("chat_id", "Unknown")),
                    "messages_count": len(chat["messages"])
                })

    if not chat_embeddings:
        print("No embeddings found in the data.")
        return

    print(f"Loaded {len(chat_embeddings)} chats. Clustering into {args.clusters} topics...")
    X = np.array(chat_embeddings)
    kmeans = KMeans(n_clusters=args.clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    clusters = defaultdict(list)
    for label, meta in zip(labels, chat_metadata):
        clusters[label].append(meta)

    for cluster_id in range(args.clusters):
        print(f"\n📂 CLUSTER {cluster_id + 1} ({len(clusters[cluster_id])} chats)")
        for meta in clusters[cluster_id][:5]:
            print(f"   - {meta['title']} ({meta['messages_count']} msgs) | URL: {meta['url']}")
        if len(clusters[cluster_id]) > 5:
            print(f"   ... and {len(clusters[cluster_id]) - 5} more.")

    with open("clustered_chats.json", "w", encoding="utf-8") as f:
        json.dump({f"Cluster_{k+1}": v for k, v in clusters.items()}, f, indent=2)

if __name__ == "__main__":
    main()