"""OpenAI LLM and embedding client implementation."""

from typing import AsyncIterator

from ...ai.providers.llm import LLMProvider
from ...ai.providers.embedding import EmbeddingProvider


class OpenAILLMClient(LLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(self, api_key: str, model_id: str = "gpt-4-turbo"):
        self.api_key = api_key
        self.model_id = model_id
        self.client = None

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from OpenAI."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        # Requires: from openai import AsyncOpenAI
        raise NotImplementedError("Requires openai>=1.0.0 SDK")

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream response from OpenAI."""
        raise NotImplementedError("Requires openai>=1.0.0 SDK")

    async def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model_id)
            return len(encoding.encode(text))
        except Exception:
            return len(text) // 4 + 1

    async def health_check(self) -> bool:
        """Check OpenAI API availability."""
        raise NotImplementedError("Requires HTTP request to OpenAI")


class OpenAIEmbeddingClient(EmbeddingProvider):
    """OpenAI embedding provider implementation."""

    def __init__(self, api_key: str, model_id: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model_id = model_id
        self.embedding_dimension = 1536

    async def embed(self, text: str) -> list[float]:
        """Generate embedding from OpenAI."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        # Requires: from openai import AsyncOpenAI
        raise NotImplementedError("Requires openai>=1.0.0 SDK")

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            embedding = await self.embed(text)
            embeddings.append(embedding)
        return embeddings

    async def health_check(self) -> bool:
        """Check OpenAI API availability."""
        raise NotImplementedError("Requires HTTP request to OpenAI")
