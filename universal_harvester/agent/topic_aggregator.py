# universal_harvester/agent/topic_aggregator.py
import re
from collections import Counter
from typing import List, Dict, Any
from universal_harvester.agent.topic_embeddings import TopicEmbedder
from universal_harvester.agent.topic_clusterer import TopicClusterer

class TopicAggregator:
    def __init__(self, n_clusters: int = 5):
        self.embedder = TopicEmbedder()
        self.clusterer = TopicClusterer(n_clusters=n_clusters)

    def _generate_cluster_name(self, cluster_id: int, chats: List[Dict[str, Any]]) -> str:
        """Generates a readable name based on the most common title keywords."""
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "for", "with", "about", 
                      "as", "by", "to", "of", "at", "from", "chat", "untitled", "is", "it", 
                      "this", "that", "how", "what", "why", "can", "i", "you", "my", "are", "do"}
        
        words = []
        for chat in chats:
            title = chat.get("title", "")
            tokens = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
            words.extend([w for w in tokens if w not in stop_words])
            
        if not words:
            return f"Topic Group {cluster_id + 1}"
            
        most_common = Counter(words).most_common(3)
        if most_common:
            label = ", ".join([w[0].title() for w in most_common])
            return f"{label} (Cluster {cluster_id + 1})"
        
        return f"Topic Group {cluster_id + 1}"

    def process_and_group(self, chats: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        chat_embeddings = []
        chat_metadata = []

        for chat in chats:
            emb = self.embedder.embed_chat(chat)
            if emb is not None:
                chat_embeddings.append(emb)
                chat_metadata.append({
                    "chat_id": chat.get("chat_id", chat.get("id", "Unknown")),
                    "url": chat.get("url", ""),
                    "title": chat.get("title", "Unknown"),
                    "messages_count": len(chat.get("messages", []))
                })

        if not chat_embeddings:
            return {}

        raw_clusters = self.clusterer.cluster_chats(chat_embeddings, chat_metadata)
        
        # Map raw cluster IDs to generated readable names
        return {self._generate_cluster_name(k, v): v for k, v in raw_clusters.items()}