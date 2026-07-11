"""LLM provider interface."""

from abc import ABC, abstractmethod
from typing import AsyncIterator


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
