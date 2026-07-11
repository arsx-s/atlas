"""SQLite session management for local mode."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

try:
    from sqlalchemy.orm import Session
except ImportError:  # pragma: no cover - exercised in dependency-constrained environments.
    from typing import Any as Session

from atlas_backend.data.sqlite.base import create_sqlite_session_factory


class SqliteSessionManager:
    """Manages SQLite session lifecycle for local mode."""

    def __init__(self, database_path: str | Path, echo: bool = False) -> None:
        self._database_path = Path(database_path)
        self._factory = create_sqlite_session_factory(database_path, echo=echo)

    def get_session(self) -> Session:
        """Get a new SQLite session."""
        return self._factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context manager for session lifecycle with automatic commit/rollback."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @property
    def database_path(self) -> Path:
        """Get the database file path."""
        return self._database_path
