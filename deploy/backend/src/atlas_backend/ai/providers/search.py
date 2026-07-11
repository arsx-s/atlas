"""Search provider interface."""

from abc import ABC, abstractmethod
from typing import Any


class SearchProvider(ABC):
    """Interface for search providers."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Search for query and return results."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider availability."""
        pass
