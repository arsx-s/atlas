"""Anthropic Claude client."""

from __future__ import annotations

from typing import AsyncIterator

from ._base import HttpClient, HttpClientConfig, approximate_tokens, flatten_messages
from ..providers.embedding import EmbeddingProvider
from ..providers.llm import LLMProvider


class AnthropicLLMClient(LLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model_id: str = "claude-3-sonnet-20240229",
        base_url: str = "https://api.anthropic.com/v1",
        timeout_seconds: int = 60,
    ) -> None:
        self.model_id = model_id
        self._client = HttpClient(HttpClientConfig(base_url=base_url, api_key=api_key, timeout_seconds=timeout_seconds, extra_headers={"anthropic-version": "2023-06-01"}))

    async def generate(self, model: str, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int | None = None, system: str | None = None) -> str:
        response = await self._client.post("/messages", {
            "model": model or self.model_id,
            "messages": flatten_messages(messages, system),
            "temperature": temperature,
            "max_tokens": max_tokens or 1024,
        })
        return "".join(block.get("text", "") for block in response.get("content", []))

    async def stream(self, model: str, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int | None = None, system: str | None = None) -> AsyncIterator[str]:
        text = await self.generate(model, messages, temperature, max_tokens, system)
        for chunk in text.split():
            yield f"{chunk} "

    async def count_tokens(self, model: str, text: str) -> int:
        return approximate_tokens(text)

    async def health_check(self) -> bool:
        return await self._client.health_check("/models")


class AnthropicEmbeddingClient(EmbeddingProvider):
    async def embed(self, model: str, text: str) -> list[float]:
        raise NotImplementedError("Anthropic embeddings are not a native Anthropic feature.")

    async def embed_batch(self, model: str, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("Anthropic embeddings are not a native Anthropic feature.")

    async def health_check(self) -> bool:
        return False
