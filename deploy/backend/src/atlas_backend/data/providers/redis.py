"""Local Redis-compatible provider."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from atlas_backend.data.providers import RedisProvider


class RedisProviderImpl(RedisProvider):
    """Concrete Redis provider implementation backed by in-memory state."""

    def __init__(self) -> None:
        self._values: dict[str, tuple[str, float | None]] = {}
        self._lists: dict[str, deque[str]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _expired(self, expires_at: float | None) -> bool:
        return expires_at is not None and time.time() > expires_at

    def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        with self._lock:
            expires_at = time.time() + ttl if ttl else None
            self._values[key] = (value, expires_at)
        return True

    def get(self, key: str) -> str | None:
        with self._lock:
            record = self._values.get(key)
            if record is None:
                return None
            value, expires_at = record
            if self._expired(expires_at):
                self._values.pop(key, None)
                return None
            return value

    def delete(self, key: str) -> bool:
        with self._lock:
            existed = key in self._values or key in self._lists
            self._values.pop(key, None)
            self._lists.pop(key, None)
        return existed

    def exists(self, key: str) -> bool:
        return self.get(key) is not None or key in self._lists

    def incr(self, key: str) -> int:
        current = int(self.get(key) or "0") + 1
        self.set(key, str(current))
        return current

    def lpush(self, key: str, values: list) -> int:
        with self._lock:
            for value in values:
                self._lists[key].appendleft(str(value))
            return len(self._lists[key])

    def lpop(self, key: str, count: int = 1) -> list:
        popped: list[str] = []
        with self._lock:
            queue = self._lists[key]
            for _ in range(min(count, len(queue))):
                popped.append(queue.popleft())
        return popped
