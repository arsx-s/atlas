"""Search routes."""

from __future__ import annotations

from typing import Any

from atlas_backend.core.responses import create_success_response
from atlas_backend.search.service import SearchService


def create_search_router(settings: Any) -> Any:
    try:
        from fastapi import APIRouter
    except ImportError as error:
        raise RuntimeError("FastAPI is required to create Atlas API routers.") from error

    service = SearchService()
    router = APIRouter(tags=["search"])

    @router.get("/search")
    async def search(query: str, limit: int = 10) -> Any:
        results = await service.search(query, max_results=limit)
        return create_success_response({"results": service.to_dicts(results)})

    return router
