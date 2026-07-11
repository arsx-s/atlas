"""Local runtime API routes."""

from __future__ import annotations

from typing import Any

from atlas_backend.core.responses import create_success_response
from atlas_backend.local.cache import LocalCache
from atlas_backend.local.hardware import HardwareDetector
from atlas_backend.local.health import check_local_runtime_health
from atlas_backend.local.memory import LocalMemoryProvider
from atlas_backend.local.models import LocalModelRegistry


_cache = LocalCache()
_memory = LocalMemoryProvider()
_detector = HardwareDetector()
_registry = LocalModelRegistry()


def create_local_router() -> Any:
    from fastapi import APIRouter

    router = APIRouter(tags=["local"])

    @router.get("/local/models")
    async def list_models() -> Any:
        models = _registry.list_models()
        return create_success_response({"models": [m.model_dump(mode="json") for m in models]})

    @router.get("/local/hardware")
    async def get_hardware() -> Any:
        hw = _detector.detect()
        return create_success_response(hw.model_dump(mode="json") if hasattr(hw, "model_dump") else hw)

    @router.get("/local/health")
    async def local_health() -> Any:
        health = await check_local_runtime_health()
        return create_success_response(health.model_dump(mode="json") if hasattr(health, "model_dump") else health)

    @router.get("/local/cache")
    async def get_cache(key: str = "") -> Any:
        if key:
            value = _cache.get(key)
            return create_success_response({"key": key, "value": value, "hit": value is not None})
        return create_success_response({"status": "cache available", "size": _cache._cache.qsize() if hasattr(_cache._cache, "qsize") else "N/A"})

    return router
