"""Settings API routes."""

from __future__ import annotations

from typing import Any

from atlas_backend.core.errors import AtlasErrorCode, AtlasException
from atlas_backend.core.responses import create_success_response
from atlas_backend.persistence import AtlasLocalStore


def create_settings_router(store: AtlasLocalStore) -> Any:
    try:
        from fastapi import APIRouter
    except ImportError as error:
        raise RuntimeError("FastAPI is required to create Atlas API routers.") from error

    router = APIRouter(tags=["settings"])

    @router.get("/settings")
    async def get_settings() -> Any:
        settings = store.get_all_settings()
        return create_success_response(settings)

    @router.post("/settings")
    async def set_setting(payload: dict[str, Any]) -> Any:
        key = payload.get("key", "").strip()
        value = payload.get("value", "")
        if not key:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "Setting key is required.")
        store.set_setting(key, value)
        return create_success_response({"key": key, "value": value})

    return router
