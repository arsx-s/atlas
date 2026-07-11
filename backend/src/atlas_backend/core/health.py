"""Health report contracts for Atlas backend."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field

from atlas_backend import __version__
from atlas_backend.core.config import AtlasSettings


class ComponentState(StrEnum):
    """Possible health states for a backend component."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    NOT_CONFIGURED = "not_configured"
    UNAVAILABLE = "unavailable"


class ServiceState(StrEnum):
    """Overall API health state."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class ComponentHealth(BaseModel):
    """Health state for one backend component."""

    name: str
    state: ComponentState
    required: bool
    message: str


class HealthReport(BaseModel):
    """Liveness or readiness report returned by the API."""

    status: ServiceState
    version: str = __version__
    environment: str
    runtime_mode: str
    components: tuple[ComponentHealth, ...] = Field(default_factory=tuple)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def build_liveness_report(settings: AtlasSettings) -> HealthReport:
    """Build the lightweight liveness report for the API process."""

    return HealthReport(
        status=ServiceState.HEALTHY,
        environment=settings.environment.value,
        runtime_mode=settings.runtime_mode.value,
        components=(
            ComponentHealth(
                name="api",
                state=ComponentState.HEALTHY,
                required=True,
                message="API process is responsive.",
            ),
        ),
    )


def build_readiness_report(settings: AtlasSettings) -> HealthReport:
    """Build the readiness report for configured Milestone 2+ components including datastores."""

    from atlas_backend.data.health.datastore_checks import (
        check_postgres_health,
        check_sqlite_health,
        check_redis_health,
        check_qdrant_health,
        check_neo4j_health,
    )

    components = [
        ComponentHealth(
            name="api",
            state=ComponentState.HEALTHY,
            required=True,
            message="API routes and response contracts are available.",
        ),
        ComponentHealth(
            name="local_mode",
            state=ComponentState.HEALTHY if settings.local_mode_enabled else ComponentState.NOT_CONFIGURED,
            required=True,
            message=(
                "Local mode is enabled."
                if settings.local_mode_enabled
                else "Local mode is disabled by configuration."
            ),
        ),
        ComponentHealth(
            name="cloud_sync",
            state=(
                ComponentState.NOT_CONFIGURED
                if not settings.cloud_sync_enabled
                else ComponentState.HEALTHY
            ),
            required=False,
            message=(
                "Cloud sync is disabled by default."
                if not settings.cloud_sync_enabled
                else "Cloud sync is enabled and persistence providers are configured."
            ),
        ),
    ]

    postgres_check = check_postgres_health(settings.database_url, settings.cloud_sync_enabled)
    components.append(
        ComponentHealth(
            name=postgres_check.name,
            state=postgres_check.state,
            required=postgres_check.required,
            message=postgres_check.message,
        )
    )

    sqlite_check = check_sqlite_health(settings.sqlite_path, settings.local_mode_enabled)
    components.append(
        ComponentHealth(
            name=sqlite_check.name,
            state=sqlite_check.state,
            required=sqlite_check.required,
            message=sqlite_check.message,
        )
    )

    redis_check = check_redis_health(settings.redis_url)
    components.append(
        ComponentHealth(
            name=redis_check.name,
            state=redis_check.state,
            required=redis_check.required,
            message=redis_check.message,
        )
    )

    qdrant_check = check_qdrant_health(settings.qdrant_url)
    components.append(
        ComponentHealth(
            name=qdrant_check.name,
            state=qdrant_check.state,
            required=qdrant_check.required,
            message=qdrant_check.message,
        )
    )

    neo4j_check = check_neo4j_health(settings.neo4j_url)
    components.append(
        ComponentHealth(
            name=neo4j_check.name,
            state=neo4j_check.state,
            required=neo4j_check.required,
            message=neo4j_check.message,
        )
    )

    # M6: Document Intelligence health checks
    documents_check = ComponentHealth(
        name="documents",
        state=ComponentState.HEALTHY if settings.documents_storage_path else ComponentState.NOT_CONFIGURED,
        required=False,
        message=(
            "Document storage is configured."
            if settings.documents_storage_path
            else "Document storage not configured (documents disabled)."
        ),
    )
    components.append(documents_check)

    # M8: Local Intelligence health checks
    from atlas_backend.local.health import check_local_runtime_health
    try:
        import asyncio
        local_health = asyncio.run(check_local_runtime_health())
        local_check = ComponentHealth(
            name="local_runtime",
            state=ComponentState.HEALTHY if local_health.healthy else ComponentState.DEGRADED,
            required=False,
            message=(
                f"Local runtime ready: {local_health.cpu_cores} cores, {local_health.ram_available_gb:.1f}GB RAM, "
                f"{local_health.local_models_available} LLM models available"
                if local_health.healthy
                else "Local runtime unavailable"
            ),
        )
    except Exception as e:
        local_check = ComponentHealth(
            name="local_runtime",
            state=ComponentState.NOT_CONFIGURED if not settings.local_models_enabled else ComponentState.DEGRADED,
            required=False,
            message=f"Local runtime check failed: {str(e)}",
        )
    components.append(local_check)

    required_components = [component for component in components if component.required]
    status = (
        ServiceState.HEALTHY
        if all(component.state == ComponentState.HEALTHY for component in required_components)
        else ServiceState.DEGRADED
    )

    return HealthReport(
        status=status,
        environment=settings.environment.value,
        runtime_mode=settings.runtime_mode.value,
        components=tuple(components),
    )
