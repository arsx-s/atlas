"""AI provider interface abstractions."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class LLMProvider(ABC):
    """Interface for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system: str | None = None,
    ) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    async def stream(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream text generation."""
        pass

    @abstractmethod
    async def count_tokens(self, model: str, text: str) -> int:
        """Count tokens in text."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider availability."""
        pass


class EmbeddingProvider(ABC):
    """Interface for embedding providers."""

    @abstractmethod
    async def embed(self, model: str, text: str) -> list[float]:
        """Generate embedding for text."""
        pass

    @abstractmethod
    async def embed_batch(self, model: str, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider availability."""
        pass


class SearchProvider(ABC):
    """Interface for search providers."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Search for query and return results."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider availability."""
        pass
