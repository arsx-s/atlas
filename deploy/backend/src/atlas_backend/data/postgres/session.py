"""PostgreSQL session management."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

try:
    from sqlalchemy.orm import Session
except ImportError:  # pragma: no cover - exercised in dependency-constrained environments.
    from typing import Any as Session

from atlas_backend.data.postgres.base import create_postgres_session_factory


class PostgresSessionManager:
    """Manages PostgreSQL session lifecycle."""

    def __init__(self, database_url: str, echo: bool = False) -> None:
        self._factory = create_postgres_session_factory(database_url, echo=echo)

    def get_session(self) -> Session:
        """Get a new PostgreSQL session."""
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
