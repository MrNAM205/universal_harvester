# universal_harvester/agent/topic_clusterer.py
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict
from typing import List, Dict, Any

class TopicClusterer:
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)

    def cluster_chats(self, chat_embeddings: List[np.ndarray], chat_metadata: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        if not chat_embeddings:
            return {}
            
        X = np.array(chat_embeddings)
        labels = self.kmeans.fit_predict(X)

        clusters = defaultdict(list)
        for label, meta in zip(labels, chat_metadata):
            clusters[int(label)].append(meta)

        return dict(clusters)