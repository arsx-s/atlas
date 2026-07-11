"""Sync routes."""

from __future__ import annotations

from typing import Any

from atlas_backend.core.responses import create_success_response
from atlas_backend.persistence import AtlasLocalStore
from atlas_backend.sync.service import SyncService


def create_sync_router(settings: Any) -> Any:
    try:
        from fastapi import APIRouter
    except ImportError as error:
        raise RuntimeError("FastAPI is required to create Atlas API routers.") from error

    store = AtlasLocalStore(settings.sqlite_path or "atlas-local.db")
    service = SyncService(store)
    router = APIRouter(tags=["sync"])

    @router.get("/sync/pending")
    async def pending() -> Any:
        return create_success_response({"items": service.list_pending()})

    @router.post("/sync/enqueue")
    async def enqueue(payload: dict[str, Any]) -> Any:
        record = service.enqueue(
            entity_type=payload["entity_type"],
            entity_id=payload["entity_id"],
            operation=payload.get("operation", "upsert"),
            payload=payload.get("payload", {}),
        )
        return create_success_response(record)

    return router
