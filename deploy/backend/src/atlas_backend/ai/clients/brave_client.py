"""Brave Search client."""

from __future__ import annotations

from ._base import HttpClient, HttpClientConfig
from ..providers.search import SearchProvider


class BraveSearchClient(SearchProvider):
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.search.brave.com/res/v1", timeout_seconds: int = 60) -> None:
        self._client = HttpClient(HttpClientConfig(base_url=base_url, api_key=api_key, timeout_seconds=timeout_seconds, extra_headers={"X-Subscription-Token": api_key or ""}))

    async def search(self, query: str, max_results: int = 10) -> list[dict]:
        response = await self._client.get(f"/web/search?q={query}&count={max_results}")
        return response.get("web", {}).get("results", [])

    async def health_check(self) -> bool:
        return await self._client.health_check("/web/search?q=test&count=1")
