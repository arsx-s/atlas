"""Search orchestration and ranking."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import asdict
from time import time
from typing import Any

from .models import SearchResult
from .providers import (
    ArxivSearchProvider,
    BraveSearchProvider,
    BingSearchProvider,
    CourtListenerSearchProvider,
    CrossrefSearchProvider,
    GoogleCSESearchProvider,
    PubMedSearchProvider,
    SemanticScholarSearchProvider,
    TavilySearchProvider,
)


class SearchService:
    def __init__(self, providers: list[Any] | None = None, cache_ttl_seconds: int = 300) -> None:
        self.providers = providers or [
            TavilySearchProvider(),
            BraveSearchProvider(),
            GoogleCSESearchProvider(),
            BingSearchProvider(),
            CrossrefSearchProvider(),
            SemanticScholarSearchProvider(),
            ArxivSearchProvider(),
            PubMedSearchProvider(),
            CourtListenerSearchProvider(),
        ]
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: dict[str, tuple[float, list[SearchResult]]] = {}

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        cache_key = hashlib.sha256(query.strip().lower().encode("utf-8")).hexdigest()
        cached = self._cache.get(cache_key)
        if cached and cached[0] > time():
            return cached[1][:max_results]

        tasks = [provider.search(query, max_results=max_results) for provider in self.providers]
        collected = await asyncio.gather(*tasks, return_exceptions=True)
        results: list[SearchResult] = []
        for response in collected:
            if isinstance(response, Exception):
                continue
            results.extend(response)

        deduped = self._dedupe(results)
        ranked = sorted(deduped, key=self._score, reverse=True)[:max_results]
        self._cache[cache_key] = (time() + self.cache_ttl_seconds, ranked)
        return ranked

    def _dedupe(self, results: list[SearchResult]) -> list[SearchResult]:
        seen: set[str] = set()
        deduped: list[SearchResult] = []
        for result in results:
            key = (result.doi or result.url or result.title).strip().lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(result)
        return deduped

    def _score(self, result: SearchResult) -> float:
        score = 0.0
        if result.doi:
            score += 3.0
        if result.citations:
            score += min(result.citations / 100.0, 2.0)
        if result.authors:
            score += 0.4
        if result.published_at:
            score += 0.2
        score += min(len(result.snippet) / 500.0, 1.0)
        return score

    def to_dicts(self, results: list[SearchResult]) -> list[dict[str, Any]]:
        return [asdict(result) for result in results]

