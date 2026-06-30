import os
import requests
import numpy as np

class TopicEmbedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_name}"
        self.api_key = os.environ.get("HF_API_KEY")
        
        if not self.api_key:
            print("[WARNING] HF_API_KEY not found in environment. Please add it to your .env file.")
            
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def embed(self, texts):
        if not self.api_key:
            raise ValueError("HF_API_KEY is not set. The Hugging Face API requires authentication.")

        if isinstance(texts, str):
            texts = [texts]

        # Use wait_for_model=True to ensure the inference API spins up the model if it's cold
        response = requests.post(
            self.api_url, 
            headers=self.headers, 
            json={"inputs": texts, "options": {"wait_for_model": True}}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API error: {response.status_code} - {response.text}")
            
        embeddings = np.array(response.json())
        
        # Normalize embeddings just like sentence-transformers does by default
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0] = 1
        embeddings = embeddings / norms

        return embeddings