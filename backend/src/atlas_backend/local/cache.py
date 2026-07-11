"""Local cache abstraction."""

from typing import Any, Optional
import asyncio


class LocalCache:
    """Simple in-process cache for local mode."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}

    async def set(self, key: str, value: Any) -> None:
        """Set cache value."""
        if len(self.cache) >= self.max_size:
            # Remove least recently used
            oldest_key = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest_key]
            del self.access_times[oldest_key]

        self.cache[key] = value
        self.access_times[key] = asyncio.get_event_loop().time()

    async def get(self, key: str) -> Optional[Any]:
        """Get cache value."""
        if key not in self.cache:
            return None

        self.access_times[key] = asyncio.get_event_loop().time()
        return self.cache[key]

    async def delete(self, key: str) -> None:
        """Delete cache entry."""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)

    async def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
        self.access_times.clear()

    async def size(self) -> int:
        """Get cache size."""
        return len(self.cache)
