"""DuckDuckGo search client."""

from __future__ import annotations

from urllib.parse import quote_plus

from ._base import HttpClient, HttpClientConfig
from ..providers.search import SearchProvider


class DuckDuckGoSearchClient(SearchProvider):
    def __init__(self, base_url: str = "https://html.duckduckgo.com/html", timeout_seconds: int = 30) -> None:
        self._client = HttpClient(HttpClientConfig(base_url=base_url, api_key=None, timeout_seconds=timeout_seconds))

    async def search(self, query: str, max_results: int = 10) -> list[dict]:
        response = await self._client.get(f"/?q={quote_plus(query)}")
        return [{"title": "DuckDuckGo result", "url": response.get("url", ""), "snippet": response.get("content", "")}][:max_results]

    async def health_check(self) -> bool:
        return await self._client.health_check("/")
