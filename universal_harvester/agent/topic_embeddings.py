# universal_harvester/agent/topic_embeddings.py
import os
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class TopicEmbedder:
    def __init__(self):
        model_path = os.environ.get("EMBEDDING_MODEL_PATH", "C:/models/all-MiniLM-L6-v2")
        self.model = SentenceTransformer(model_path)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Embed a list of text strings into vectors."""
        if not texts:
            return np.array([])
        return self.model.encode(texts, convert_to_numpy=True)
        
    def embed_chat(self, chat: Dict[str, Any]) -> np.ndarray:
        """Generates a single average embedding for an entire chat."""
        texts = [msg.get("text", "") for msg in chat.get("messages", []) if msg.get("text")]
        if not texts:
            return None
        embeddings = self.embed_texts(texts)
        # Average the embeddings of all messages to represent the whole chat
        return np.mean(embeddings, axis=0)