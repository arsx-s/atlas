"""Local Ollama client."""

from __future__ import annotations

from typing import AsyncIterator

from ._base import HttpClient, HttpClientConfig, approximate_tokens, flatten_messages
from ..providers.embedding import EmbeddingProvider
from ..providers.llm import LLMProvider


class LocalLLMClient(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model_id: str = "mistral-7b", timeout_seconds: int = 120) -> None:
        self.model_id = model_id
        self._client = HttpClient(HttpClientConfig(base_url=base_url, api_key=None, timeout_seconds=timeout_seconds))

    async def generate(self, model: str, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int | None = None, system: str | None = None) -> str:
        response = await self._client.post("/api/chat", {"model": model or self.model_id, "messages": flatten_messages(messages, system), "stream": False, "options": {"temperature": temperature, "num_predict": max_tokens or 1024}})
        return response.get("message", {}).get("content", "")

    async def stream(self, model: str, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int | None = None, system: str | None = None) -> AsyncIterator[str]:
        text = await self.generate(model, messages, temperature, max_tokens, system)
        for chunk in text.split():
            yield f"{chunk} "

    async def count_tokens(self, model: str, text: str) -> int:
        return approximate_tokens(text)

    async def health_check(self) -> bool:
        return await self._client.health_check("/api/tags")


class LocalEmbeddingClient(EmbeddingProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model_id: str = "nomic-embed-text", timeout_seconds: int = 120) -> None:
        self.model_id = model_id
        self._client = HttpClient(HttpClientConfig(base_url=base_url, api_key=None, timeout_seconds=timeout_seconds))

    async def embed(self, model: str, text: str) -> list[float]:
        response = await self._client.post("/api/embeddings", {"model": model or self.model_id, "prompt": text})
        return list(response.get("embedding", []))

    async def embed_batch(self, model: str, texts: list[str]) -> list[list[float]]:
        return [await self.embed(model, text) for text in texts]

    async def health_check(self) -> bool:
        return await self._client.health_check("/api/tags")
