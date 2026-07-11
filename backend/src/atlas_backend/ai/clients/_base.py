"""Shared provider helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, AsyncIterator

from urllib import parse, request


def approximate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def flatten_messages(messages: list[dict[str, str]], system: str | None = None) -> list[dict[str, str]]:
    combined = []
    if system:
        combined.append({"role": "system", "content": system})
    combined.extend({"role": message["role"], "content": message["content"]} for message in messages)
    return combined


@dataclass(slots=True)
class HttpClientConfig:
    base_url: str
    api_key: str | None
    timeout_seconds: int = 60
    extra_headers: dict[str, str] | None = None


class HttpClient:
    def __init__(self, config: HttpClientConfig) -> None:
        self.config = config

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        if self.config.extra_headers:
            headers.update(self.config.extra_headers)
        return headers

    async def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(f"{self.config.base_url.rstrip('/')}{path}", data=data, headers=self._headers(), method="POST")
        return await self._execute(req)

    async def get(self, path: str) -> dict[str, Any]:
        req = request.Request(f"{self.config.base_url.rstrip('/')}{path}", headers=self._headers(), method="GET")
        return await self._execute(req)

    async def health_check(self, path: str = "/models") -> bool:
        try:
            await self.get(path)
            return True
        except Exception:
            return False

    async def stream_text(self, text: str) -> AsyncIterator[str]:
        for word in text.split():
            yield f"{word} "

    async def _execute(self, req: request.Request) -> dict[str, Any]:
        def _call() -> dict[str, Any]:
            with request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))

        import asyncio

        return await asyncio.to_thread(_call)
