"""DeepSeek client."""

from __future__ import annotations

from typing import AsyncIterator

from ._base import HttpClient, HttpClientConfig, approximate_tokens, flatten_messages
from ..providers.embedding import EmbeddingProvider
from ..providers.llm import LLMProvider


class DeepSeekLLMClient(LLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model_id: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com/v1",
        timeout_seconds: int = 60,
    ) -> None:
        self.model_id = model_id
        self._client = HttpClient(HttpClientConfig(base_url=base_url, api_key=api_key, timeout_seconds=timeout_seconds))

    async def generate(self, model: str, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int | None = None, system: str | None = None) -> str:
        response = await self._client.post("/chat/completions", {
            "model": model or self.model_id,
            "messages": flatten_messages(messages, system),
            "temperature": temperature,
            "max_tokens": max_tokens or 1024,
        })
        return response["choices"][0]["message"]["content"]

    async def stream(self, model: str, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int | None = None, system: str | None = None) -> AsyncIterator[str]:
        text = await self.generate(model, messages, temperature, max_tokens, system)
        for chunk in text.split():
            yield f"{chunk} "

    async def count_tokens(self, model: str, text: str) -> int:
        return approximate_tokens(text)

    async def health_check(self) -> bool:
        return await self._client.health_check("/models")


class DeepSeekEmbeddingClient(EmbeddingProvider):
    async def embed(self, model: str, text: str) -> list[float]:
        raise NotImplementedError("DeepSeek embedding APIs are not standardized across deployments.")

    async def embed_batch(self, model: str, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("DeepSeek embedding APIs are not standardized across deployments.")

    async def health_check(self) -> bool:
        return False
