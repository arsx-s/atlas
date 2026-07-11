"""FastAPI application factory for Atlas."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from atlas_backend import __version__
from atlas_backend.api.v1.auth import create_auth_router
from atlas_backend.api.v1.documents import create_document_router
from atlas_backend.api.v1.health import create_health_router
from atlas_backend.api.v1.local import create_local_router
from atlas_backend.api.v1.projects import create_project_router
from atlas_backend.api.v1.research_sessions import create_research_router
from atlas_backend.api.v1.search import create_search_router
from atlas_backend.api.v1.sync import create_sync_router
from atlas_backend.api.v1.export import create_export_router
from atlas_backend.api.v1.monitoring import create_monitoring_router
from atlas_backend.core.config import AtlasSettings, load_settings
from atlas_backend.core.errors import AtlasException, map_exception_to_error_response
from atlas_backend.core.logging import configure_logging
from atlas_backend.persistence import AtlasLocalStore


def create_app(settings: AtlasSettings | None = None) -> Any:
    fastapi = _load_fastapi()
    selected_settings = settings or load_settings()

    configure_logging(selected_settings.log_level)

    app = fastapi.FastAPI(
        title=selected_settings.app_name,
        version=__version__,
        docs_url=f"{selected_settings.api_base_path}/docs",
        redoc_url=f"{selected_settings.api_base_path}/redoc",
        openapi_url=f"{selected_settings.api_base_path}/openapi.json",
    )

    app.state.settings = selected_settings

    origins = selected_settings.cors_allowed_origins or (
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "app://.",
    )

    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if selected_settings.rate_limit_enabled:
        try:
            from slowapi import _rate_limit_exceeded_handler
            from slowapi.errors import RateLimitExceeded
            from slowapi.middleware import SlowAPIMiddleware
            from slowapi import Limiter
            from slowapi.util import get_remote_address

            limiter = Limiter(
                key_func=get_remote_address,
                default_limits=["100/hour"],
                enabled=True,
            )
            app.state.limiter = limiter
            app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
            app.add_middleware(SlowAPIMiddleware)
        except ImportError:
            pass

    store = AtlasLocalStore(selected_settings.sqlite_path or "atlas-local.db")
    app.state.store = store

    @app.middleware("http")
    async def add_security_headers(request: Any, call_next: Callable[[Any], Any]) -> Any:
        import time
        start = time.perf_counter()
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        response.headers.setdefault("X-Response-Time-Ms", str(round((time.perf_counter() - start) * 1000, 1)))
        return response

    @app.exception_handler(AtlasException)
    async def handle_atlas_exception(_request: Any, exception: AtlasException) -> Any:
        payload = map_exception_to_error_response(exception)
        return fastapi.responses.JSONResponse(
            status_code=exception.status_code,
            content=payload.model_dump(mode="json"),
        )

    prefix = selected_settings.api_base_path
    app.include_router(create_health_router(selected_settings), prefix=prefix)
    app.include_router(create_research_router(selected_settings, store), prefix=prefix)
    app.include_router(create_auth_router(selected_settings, store), prefix=prefix)
    app.include_router(create_sync_router(selected_settings), prefix=prefix)
    app.include_router(create_search_router(selected_settings), prefix=prefix)
    app.include_router(create_project_router(selected_settings, store), prefix=prefix)
    app.include_router(create_document_router(selected_settings, store), prefix=prefix)
    app.include_router(create_local_router(), prefix=prefix)
    app.include_router(create_export_router(store), prefix=prefix)
    app.include_router(create_monitoring_router(), prefix=prefix)

    return app


def _load_fastapi() -> Any:
    try:
        import fastapi
    except ImportError as error:
        message = (
            "FastAPI is required to create the Atlas backend application. "
            "Install backend dependencies before starting the API server."
        )
        raise RuntimeError(message) from error
    return fastapi
