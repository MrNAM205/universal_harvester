class Embedder:
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

class SimpleEmbedder(Embedder):
    def embed(self, text: str) -> list[float]:
        # placeholder: deterministic hash -> vector
        return [hash(text) % 997 / 997.0]
