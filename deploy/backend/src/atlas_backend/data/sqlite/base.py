"""SQLite base configuration and session management."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from sqlalchemy import create_engine, event
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import declarative_base, sessionmaker, Session
    from sqlalchemy.pool import StaticPool
    SQLALCHEMY_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised in dependency-constrained environments.
    create_engine = None  # type: ignore[assignment]
    event = None  # type: ignore[assignment]
    Engine = Any  # type: ignore[assignment]
    Session = Any  # type: ignore[assignment]
    StaticPool = object  # type: ignore[assignment]
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


def create_sqlite_engine(
    database_path: str | Path,
    echo: bool = False,
    timeout: int = 20,
) -> Engine:
    """Create a SQLite SQLAlchemy engine with foreign key support."""

    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    database_url = f"sqlite:///{path.as_posix()}"

    if not SQLALCHEMY_AVAILABLE:
        return _FallbackEngine(url=database_url, echo=echo)

    engine = create_engine(
        database_url,
        echo=echo,
        connect_args={"timeout": timeout},
        poolclass=StaticPool,
    )

    if SQLALCHEMY_AVAILABLE:
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_conn, _connection_record):
            """Enable foreign keys for SQLite."""
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def create_sqlite_session_factory(
    database_path: str | Path,
    echo: bool = False,
) -> sessionmaker[Session]:
    """Create a SQLite session factory."""

    engine = create_sqlite_engine(database_path, echo=echo)
    return sessionmaker(bind=engine, expire_on_commit=False)
