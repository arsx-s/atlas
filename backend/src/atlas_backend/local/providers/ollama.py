"""Ollama integration for local LLM."""

from typing import AsyncIterator, Optional

from ...ai.providers.llm import LLMProvider


class OllamaLLMProvider(LLMProvider):
    """Ollama-based local LLM provider."""

    def __init__(self, base_url: str = "http://localhost:11434", model_id: str = "mistral"):
        self.base_url = base_url
        self.model_id = model_id

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from local model using Ollama."""
        raise NotImplementedError(
            "Ollama integration requires ollama-python client. "
            "Install: pip install ollama"
        )

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream response from local model using Ollama."""
        raise NotImplementedError("Ollama streaming requires ollama-python client")

    async def count_tokens(self, text: str) -> int:
        """Count tokens in text using Ollama."""
        # Local token counting (approximate)
        return len(text) // 4 + 1

    async def health_check(self) -> bool:
        """Check if Ollama is running."""
        raise NotImplementedError("Health check requires HTTP request to Ollama")
