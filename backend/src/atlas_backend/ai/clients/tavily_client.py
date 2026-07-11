"""Tavily search client."""

from __future__ import annotations

from ._base import HttpClient, HttpClientConfig
from ..providers.search import SearchProvider


class TavilySearchClient(SearchProvider):
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.tavily.com", timeout_seconds: int = 60) -> None:
        self._client = HttpClient(HttpClientConfig(base_url=base_url, api_key=api_key, timeout_seconds=timeout_seconds))

    async def search(self, query: str, max_results: int = 10) -> list[dict]:
        response = await self._client.post("/search", {"query": query, "max_results": max_results, "include_answer": False, "include_raw_content": True})
        return response.get("results", [])

    async def health_check(self) -> bool:
        return await self._client.health_check("/search")
