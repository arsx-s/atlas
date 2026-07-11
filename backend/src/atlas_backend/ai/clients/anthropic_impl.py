"""Anthropic Claude LLM client implementation."""

from typing import AsyncIterator

from ...ai.providers.llm import LLMProvider


class AnthropicLLMClientImpl(LLMProvider):
    """Anthropic Claude LLM provider implementation."""

    def __init__(self, api_key: str, model_id: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model_id = model_id
        self.client = None

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from Claude."""
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        # Requires: from anthropic import AsyncAnthropic
        raise NotImplementedError("Requires anthropic SDK")

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream response from Claude."""
        raise NotImplementedError("Requires anthropic SDK")

    async def count_tokens(self, text: str) -> int:
        """Count tokens (approximate)."""
        return len(text) // 4 + 1

    async def health_check(self) -> bool:
        """Check Anthropic API availability."""
        raise NotImplementedError("Requires HTTP request to Anthropic")
