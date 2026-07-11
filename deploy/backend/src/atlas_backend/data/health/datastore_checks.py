"""Datastore health check contracts."""

from __future__ import annotations

from enum import StrEnum


class DatastoreComponentState(StrEnum):
    """Health state for a datastore component."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    NOT_CONFIGURED = "not_configured"
    UNAVAILABLE = "unavailable"


class DatastoreComponentHealth:
    """Health status for one datastore component."""

    def __init__(
        self,
        name: str,
        state: DatastoreComponentState,
        required: bool,
        message: str,
    ) -> None:
        self.name = name
        self.state = state
        self.required = required
        self.message = message

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "state": self.state.value,
            "required": self.required,
            "message": self.message,
        }


def check_postgres_health(database_url: str | None, enabled: bool) -> DatastoreComponentHealth:
    """Check PostgreSQL readiness status."""

    if not enabled or not database_url:
        return DatastoreComponentHealth(
            name="postgres",
            state=DatastoreComponentState.NOT_CONFIGURED,
            required=False,
            message="PostgreSQL is not configured.",
        )

    return DatastoreComponentHealth(
        name="postgres",
        state=DatastoreComponentState.HEALTHY,
        required=True,
        message="PostgreSQL connection configured.",
    )


def check_sqlite_health(database_path: str | None, enabled: bool) -> DatastoreComponentHealth:
    """Check SQLite readiness status."""

    if not enabled or not database_path:
        return DatastoreComponentHealth(
            name="sqlite",
            state=DatastoreComponentState.NOT_CONFIGURED,
            required=False,
            message="SQLite is not configured.",
        )

    return DatastoreComponentHealth(
        name="sqlite",
        state=DatastoreComponentState.HEALTHY,
        required=True,
        message="SQLite database path configured.",
    )


def check_redis_health(redis_url: str | None) -> DatastoreComponentHealth:
    """Check Redis readiness status."""

    if not redis_url:
        return DatastoreComponentHealth(
            name="redis",
            state=DatastoreComponentState.NOT_CONFIGURED,
            required=False,
            message="Redis is not configured (optional).",
        )

    return DatastoreComponentHealth(
        name="redis",
        state=DatastoreComponentState.HEALTHY,
        required=False,
        message="Redis connection configured (optional).",
    )


def check_qdrant_health(qdrant_url: str | None) -> DatastoreComponentHealth:
    """Check Qdrant readiness status."""

    if not qdrant_url:
        return DatastoreComponentHealth(
            name="qdrant",
            state=DatastoreComponentState.NOT_CONFIGURED,
            required=False,
            message="Qdrant is not configured (optional).",
        )

    return DatastoreComponentHealth(
        name="qdrant",
        state=DatastoreComponentState.HEALTHY,
        required=False,
        message="Qdrant connection configured (optional).",
    )


def check_neo4j_health(neo4j_url: str | None) -> DatastoreComponentHealth:
    """Check Neo4j readiness status."""

    if not neo4j_url:
        return DatastoreComponentHealth(
            name="neo4j",
            state=DatastoreComponentState.NOT_CONFIGURED,
            required=False,
            message="Neo4j is not configured (optional).",
        )

    return DatastoreComponentHealth(
        name="neo4j",
        state=DatastoreComponentState.HEALTHY,
        required=False,
        message="Neo4j connection configured (optional).",
    )
