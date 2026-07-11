"""Search result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class SearchResult:
    title: str
    url: str
    snippet: str = ""
    source: str = ""
    authors: list[str] = field(default_factory=list)
    published_at: str | None = None
    venue: str | None = None
    doi: str | None = None
    score: float = 0.0
    citations: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

