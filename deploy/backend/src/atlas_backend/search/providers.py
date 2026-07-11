"""Search provider adapters."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any
from urllib import parse, request

from .models import SearchResult


class SearchProviderAdapter(ABC):
    id: str

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        raise NotImplementedError

    async def health_check(self) -> bool:
        return True


class JsonSearchProvider(SearchProviderAdapter):
    def __init__(self, provider_id: str, base_url: str, api_key: str | None = None, headers: dict[str, str] | None = None, timeout_seconds: int = 30) -> None:
        self.id = provider_id
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = headers or {}
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", **self.headers}
        if self.api_key and "Authorization" not in headers and "X-Subscription-Token" not in headers:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        query = f"?{parse.urlencode(params)}" if params else ""
        req = request.Request(f"{self.base_url}{path}{query}", headers=self._headers(), method="GET")
        return await self._execute(req)

    async def _execute(self, req: request.Request) -> dict[str, Any]:
        import asyncio

        def _call() -> dict[str, Any]:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}

        return await asyncio.to_thread(_call)


class TavilySearchProvider(JsonSearchProvider):
    def __init__(self, api_key: str | None = None) -> None:
        super().__init__("tavily", "https://api.tavily.com", api_key=api_key)

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        data = await self._get("/search", {"query": query, "max_results": max_results, "include_raw_content": True})
        return [_normalize_result(item, "tavily") for item in data.get("results", [])]


class BraveSearchProvider(JsonSearchProvider):
    def __init__(self, api_key: str | None = None) -> None:
        super().__init__("brave", "https://api.search.brave.com/res/v1", api_key=api_key, headers={"X-Subscription-Token": api_key or ""})

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        data = await self._get("/web/search", {"q": query, "count": max_results})
        return [_normalize_result(item, "brave") for item in data.get("web", {}).get("results", [])]


class GoogleCSESearchProvider(JsonSearchProvider):
    def __init__(self, api_key: str | None = None, cx: str | None = None) -> None:
        super().__init__("google_cse", "https://www.googleapis.com/customsearch/v1", api_key=api_key)
        self.cx = cx

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        data = await self._get("", {"key": self.api_key or "", "cx": self.cx or "", "q": query, "num": max_results})
        return [_normalize_result(item, "google_cse") for item in data.get("items", [])]


class BingSearchProvider(JsonSearchProvider):
    def __init__(self, api_key: str | None = None) -> None:
        super().__init__("bing", "https://api.bing.microsoft.com/v7.0", api_key=api_key, headers={"Ocp-Apim-Subscription-Key": api_key or ""})

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        data = await self._get("/search", {"q": query, "count": max_results})
        return [_normalize_result(item, "bing") for item in data.get("webPages", {}).get("value", [])]


class CrossrefSearchProvider(JsonSearchProvider):
    def __init__(self) -> None:
        super().__init__("crossref", "https://api.crossref.org")

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        data = await self._get("/works", {"query": query, "rows": max_results})
        return [_normalize_result(item, "crossref") for item in data.get("message", {}).get("items", [])]


class SemanticScholarSearchProvider(JsonSearchProvider):
    def __init__(self) -> None:
        super().__init__("semantic_scholar", "https://api.semanticscholar.org/graph/v1")

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        data = await self._get("/paper/search", {"query": query, "limit": max_results, "fields": "title,url,abstract,authors,year,venue,citationCount,externalIds"})
        return [_normalize_result(item, "semantic_scholar") for item in data.get("data", [])]


class ArxivSearchProvider(JsonSearchProvider):
    def __init__(self) -> None:
        super().__init__("arxiv", "https://export.arxiv.org/api")

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        data = await self._get("/query", {"search_query": query, "start": 0, "max_results": max_results})
        return [_normalize_result({"title": "arXiv result", "url": "https://arxiv.org", "summary": str(data)}, "arxiv")]


class PubMedSearchProvider(JsonSearchProvider):
    def __init__(self) -> None:
        super().__init__("pubmed", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils")

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        data = await self._get("/esearch.fcgi", {"db": "pubmed", "term": query, "retmode": "json", "retmax": max_results})
        ids = data.get("esearchresult", {}).get("idlist", [])
        return [_normalize_result({"title": f"PubMed article {article_id}", "url": f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/"}, "pubmed") for article_id in ids]


class CourtListenerSearchProvider(JsonSearchProvider):
    def __init__(self) -> None:
        super().__init__("courtlistener", "https://www.courtlistener.com/api/rest/v3")

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        data = await self._get("/search", {"q": query})
        return [_normalize_result(item, "courtlistener") for item in data.get("results", [])[:max_results]]


def _normalize_result(item: dict[str, Any], source: str) -> SearchResult:
    title = item.get("title") or item.get("name") or item.get("paperTitle") or item.get("articleTitle") or "Untitled result"
    url = item.get("url") or item.get("link") or item.get("doi") or ""
    if url and url.startswith("doi:"):
        url = f"https://doi.org/{url[4:]}"
    snippet = item.get("snippet") or item.get("abstract") or item.get("summary") or item.get("content") or ""
    doi = item.get("doi") or item.get("externalIds", {}).get("DOI")
    authors = []
    for author in item.get("authors", []):
        if isinstance(author, dict):
            name = author.get("name") or author.get("family")
            if name:
                authors.append(name)
        elif isinstance(author, str):
            authors.append(author)
    published_at = str(item.get("publishedAt") or item.get("year") or item.get("created") or item.get("published") or "") or None
    citations = item.get("citationCount") or item.get("cited_by_count")
    return SearchResult(
        title=title,
        url=url,
        snippet=snippet,
        source=source,
        authors=authors,
        published_at=published_at,
        venue=item.get("venue"),
        doi=doi,
        citations=citations,
        metadata=item,
    )

