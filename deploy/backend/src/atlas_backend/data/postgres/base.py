"""PostgreSQL base configuration and session management."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from sqlalchemy import create_engine, event
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import declarative_base, sessionmaker, Session
    from sqlalchemy.pool import NullPool, QueuePool
    SQLALCHEMY_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised in dependency-constrained environments.
    create_engine = None  # type: ignore[assignment]
    event = None  # type: ignore[assignment]
    Engine = Any  # type: ignore[assignment]
    Session = Any  # type: ignore[assignment]
    QueuePool = object  # type: ignore[assignment]
    NullPool = object  # type: ignore[assignment]
    SQLALCHEMY_AVAILABLE = False

    def declarative_base() -> type:
        return object

    @dataclass(slots=True)
    class _FallbackEngine:
        url: str
        echo: bool = False

        def dispose(self) -> None:
            return None

    class _FallbackSession:
        def commit(self) -> None:
            return None

        def rollback(self) -> None:
            return None

        def close(self) -> None:
            return None

    class _FallbackSessionFactory:
        def __init__(self, engine: _FallbackEngine) -> None:
            self.engine = engine

        def __call__(self) -> _FallbackSession:
            return _FallbackSession()

    def sessionmaker(*, bind: Any, expire_on_commit: bool = False) -> _FallbackSessionFactory:
        del expire_on_commit
        return _FallbackSessionFactory(bind)

Base = declarative_base()


def create_postgres_engine(
    database_url: str,
    echo: bool = False,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_pre_ping: bool = True,
) -> Engine:
    """Create a PostgreSQL SQLAlchemy engine with connection pooling."""

    if not SQLALCHEMY_AVAILABLE:
        return _FallbackEngine(url=database_url, echo=echo)

    engine = create_engine(
        database_url,
        echo=echo,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
    )

    return engine


def create_postgres_session_factory(
    database_url: str,
    echo: bool = False,
    pool_size: int = 10,
) -> sessionmaker[Session]:
    """Create a PostgreSQL session factory."""

    engine = create_postgres_engine(
        database_url,
        echo=echo,
        pool_size=pool_size,
    )
    return sessionmaker(bind=engine, expire_on_commit=False)
