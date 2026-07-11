"""Google Gemini client."""

from __future__ import annotations

from typing import AsyncIterator

from ._base import HttpClient, HttpClientConfig, approximate_tokens, flatten_messages
from ..providers.embedding import EmbeddingProvider
from ..providers.llm import LLMProvider


class GoogleLLMClient(LLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model_id: str = "gemini-2.0-flash",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout_seconds: int = 60,
    ) -> None:
        self.model_id = model_id
        self._client = HttpClient(HttpClientConfig(base_url=base_url, api_key=api_key, timeout_seconds=timeout_seconds))

    async def generate(self, model: str, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int | None = None, system: str | None = None) -> str:
        payload = {
            "contents": [
                {"role": message["role"], "parts": [{"text": message["content"]}]}
                for message in flatten_messages(messages, system)
            ],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens or 1024},
        }
        response = await self._client.post(f"/models/{model or self.model_id}:generateContent", payload)
        return "".join(candidate.get("text", "") for candidate in response.get("candidates", []) for candidate in [candidate.get("content", {}).get("parts", [{}])[0]])

    async def stream(self, model: str, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int | None = None, system: str | None = None) -> AsyncIterator[str]:
        text = await self.generate(model, messages, temperature, max_tokens, system)
        for chunk in text.split():
            yield f"{chunk} "

    async def count_tokens(self, model: str, text: str) -> int:
        return approximate_tokens(text)

    async def health_check(self) -> bool:
        return await self._client.health_check("/models")


class GoogleEmbeddingClient(EmbeddingProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model_id: str = "text-embedding-004",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout_seconds: int = 60,
    ) -> None:
        self.model_id = model_id
        self._client = HttpClient(HttpClientConfig(base_url=base_url, api_key=api_key, timeout_seconds=timeout_seconds))

    async def embed(self, model: str, text: str) -> list[float]:
        response = await self._client.post(f"/models/{model or self.model_id}:embedContent", {"content": {"parts": [{"text": text}]}})
        return list(response.get("embedding", {}).get("values", []))

    async def embed_batch(self, model: str, texts: list[str]) -> list[list[float]]:
        return [await self.embed(model, text) for text in texts]

    async def health_check(self) -> bool:
        return await self._client.health_check("/models")
