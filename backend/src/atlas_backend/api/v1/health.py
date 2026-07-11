"""Health and readiness routes for Atlas API v1."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from atlas_backend.core.config import AtlasSettings
from atlas_backend.core.health import build_liveness_report, build_readiness_report
from atlas_backend.core.responses import create_success_response


def create_health_router(settings: AtlasSettings) -> Any:
    """Create the v1 health router."""

    try:
        from fastapi import APIRouter
    except ImportError as error:
        message = "FastAPI is required to create Atlas API routers."
        raise RuntimeError(message) from error

    router = APIRouter(tags=["system"])

    @router.get("/health")
    async def health() -> Any:
        report = build_liveness_report(settings)
        data = report.model_dump()
        db_path = Path(settings.sqlite_path)
        data["first_run"] = not db_path.exists()
        return create_success_response(data)

    @router.get("/ready")
    async def ready() -> Any:
        return create_success_response(build_readiness_report(settings))

    return router
