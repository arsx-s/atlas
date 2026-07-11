"""Local embedding provider."""

from ...ai.providers.embedding import EmbeddingProvider


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local embedding provider using sentence-transformers or similar."""

    def __init__(self, model_id: str = "nomic-embed-text"):
        self.model_id = model_id
        self.model = None

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for text locally."""
        raise NotImplementedError(
            "Local embeddings require sentence-transformers. "
            "Install: pip install sentence-transformers"
        )

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts locally."""
        embeddings = []
        for text in texts:
            embedding = await self.embed(text)
            embeddings.append(embedding)
        return embeddings

    async def health_check(self) -> bool:
        """Check if embedding model is loaded."""
        return self.model is not None
