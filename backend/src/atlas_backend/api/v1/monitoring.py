"""Monitoring and metrics routes for Atlas API."""

from __future__ import annotations

from typing import Any


def create_monitoring_router() -> Any:
    try:
        from fastapi import APIRouter
    except ImportError as error:
        raise RuntimeError("FastAPI is required.") from error

    router = APIRouter(tags=["monitoring"])

    @router.get("/monitoring/ping")
    async def ping() -> dict[str, str]:
        return {"ping": "pong"}

    @router.get("/monitoring/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return router
