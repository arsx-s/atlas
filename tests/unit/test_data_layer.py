"""Unit tests for the data layer (Milestone 3)."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from atlas_backend.data.postgres.base import create_postgres_engine, create_postgres_session_factory
from atlas_backend.data.sqlite.base import create_sqlite_engine, create_sqlite_session_factory
from atlas_backend.data.sqlite.session import SqliteSessionManager
from atlas_backend.data.repositories.interfaces import (
    UserRepository,
    ProjectRepository,
    DocumentRepository,
    LocalProfileRepository,
    LocalProjectRepository,
    SyncQueueRepository,
)
from atlas_backend.data.providers import QdrantProvider, Neo4jProvider, RedisProvider, StorageProvider
from atlas_backend.data.health.datastore_checks import (
    check_postgres_health,
    check_sqlite_health,
    check_redis_health,
    check_qdrant_health,
    check_neo4j_health,
    DatastoreComponentState,
)
from atlas_backend.core.config import load_settings


class DataLayerTests(unittest.TestCase):
    """Test data layer contracts and abstractions."""

    def test_postgres_engine_creation_with_valid_url(self) -> None:
        """Verify PostgreSQL engine creation accepts database URL."""
        url = "postgresql://user:password@localhost/testdb"
        engine = create_postgres_engine(url)
        self.assertIsNotNone(engine)
        self.assertTrue("postgresql" in str(engine.url))

    def test_postgres_session_factory_creation(self) -> None:
        """Verify PostgreSQL session factory creation."""
        url = "postgresql://user:password@localhost/testdb"
        factory = create_postgres_session_factory(url)
        self.assertIsNotNone(factory)

    def test_sqlite_engine_creation_with_temporary_path(self) -> None:
        """Verify SQLite engine creation creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "subdir" / "test.db"
            engine = create_sqlite_engine(db_path)
            self.assertIsNotNone(engine)
            self.assertTrue(db_path.parent.exists())

    def test_sqlite_session_factory_creation(self) -> None:
        """Verify SQLite session factory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            factory = create_sqlite_session_factory(db_path)
            self.assertIsNotNone(factory)

    def test_sqlite_session_manager_initialization(self) -> None:
        """Verify SQLite session manager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            manager = SqliteSessionManager(db_path)
            self.assertEqual(manager.database_path, db_path)

    def test_sqlite_session_manager_get_session(self) -> None:
        """Verify SQLite session manager creates sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            manager = SqliteSessionManager(db_path)
            session = manager.get_session()
            self.assertIsNotNone(session)
            session.close()

    def test_repository_interfaces_are_abstract(self) -> None:
        """Verify repository interfaces cannot be instantiated."""
        with self.assertRaises(TypeError):
            UserRepository()

        with self.assertRaises(TypeError):
            ProjectRepository()

        with self.assertRaises(TypeError):
            DocumentRepository()

        with self.assertRaises(TypeError):
            LocalProfileRepository()

        with self.assertRaises(TypeError):
            LocalProjectRepository()

        with self.assertRaises(TypeError):
            SyncQueueRepository()

    def test_provider_interfaces_are_abstract(self) -> None:
        """Verify provider interfaces cannot be instantiated."""
        with self.assertRaises(TypeError):
            QdrantProvider()

        with self.assertRaises(TypeError):
            Neo4jProvider()

        with self.assertRaises(TypeError):
            RedisProvider()

        with self.assertRaises(TypeError):
            StorageProvider()

    def test_postgres_health_check_not_configured(self) -> None:
        """Verify PostgreSQL health check returns not_configured when disabled."""
        health = check_postgres_health(None, False)
        self.assertEqual(health.state, DatastoreComponentState.NOT_CONFIGURED)
        self.assertFalse(health.required)

    def test_postgres_health_check_configured(self) -> None:
        """Verify PostgreSQL health check returns healthy when configured."""
        health = check_postgres_health("postgresql://localhost/atlas", True)
        self.assertEqual(health.state, DatastoreComponentState.HEALTHY)
        self.assertTrue(health.required)

    def test_sqlite_health_check_not_configured(self) -> None:
        """Verify SQLite health check returns not_configured when disabled."""
        health = check_sqlite_health(None, False)
        self.assertEqual(health.state, DatastoreComponentState.NOT_CONFIGURED)
        self.assertFalse(health.required)

    def test_sqlite_health_check_configured(self) -> None:
        """Verify SQLite health check returns healthy when configured."""
        health = check_sqlite_health("/local/atlas.db", True)
        self.assertEqual(health.state, DatastoreComponentState.HEALTHY)
        self.assertTrue(health.required)

    def test_redis_health_check_not_configured(self) -> None:
        """Verify Redis health check returns not_configured when not set."""
        health = check_redis_health(None)
        self.assertEqual(health.state, DatastoreComponentState.NOT_CONFIGURED)
        self.assertFalse(health.required)

    def test_redis_health_check_configured(self) -> None:
        """Verify Redis health check returns healthy when configured."""
        health = check_redis_health("redis://localhost:6379")
        self.assertEqual(health.state, DatastoreComponentState.HEALTHY)
        self.assertFalse(health.required)

    def test_qdrant_health_check_not_configured(self) -> None:
        """Verify Qdrant health check returns not_configured when not set."""
        health = check_qdrant_health(None)
        self.assertEqual(health.state, DatastoreComponentState.NOT_CONFIGURED)
        self.assertFalse(health.required)

    def test_qdrant_health_check_configured(self) -> None:
        """Verify Qdrant health check returns healthy when configured."""
        health = check_qdrant_health("http://localhost:6333")
        self.assertEqual(health.state, DatastoreComponentState.HEALTHY)
        self.assertFalse(health.required)

    def test_neo4j_health_check_not_configured(self) -> None:
        """Verify Neo4j health check returns not_configured when not set."""
        health = check_neo4j_health(None)
        self.assertEqual(health.state, DatastoreComponentState.NOT_CONFIGURED)
        self.assertFalse(health.required)

    def test_neo4j_health_check_configured(self) -> None:
        """Verify Neo4j health check returns healthy when configured."""
        health = check_neo4j_health("neo4j://localhost:7687")
        self.assertEqual(health.state, DatastoreComponentState.HEALTHY)
        self.assertFalse(health.required)

    def test_settings_load_with_datastore_configuration(self) -> None:
        """Verify settings load and store datastore configuration."""
        settings = load_settings(
            {
                "ATLAS_ENV": "test",
                "DATABASE_URL": "postgresql://localhost/atlas",
                "ATLAS_SQLITE_PATH": "/local/atlas.db",
                "REDIS_URL": "redis://localhost:6379",
                "QDRANT_URL": "http://localhost:6333",
                "NEO4J_URL": "neo4j://localhost:7687",
                "ATLAS_STORAGE_TYPE": "s3",
                "AWS_S3_BUCKET": "atlas-bucket",
            }
        )

        self.assertEqual(settings.database_url, "postgresql://localhost/atlas")
        self.assertEqual(settings.sqlite_path, "/local/atlas.db")
        self.assertEqual(settings.redis_url, "redis://localhost:6379")
        self.assertEqual(settings.qdrant_url, "http://localhost:6333")
        self.assertEqual(settings.neo4j_url, "neo4j://localhost:7687")
        self.assertEqual(settings.storage_type, "s3")
        self.assertEqual(settings.s3_bucket, "atlas-bucket")

    def test_settings_load_with_optional_datastore_configuration(self) -> None:
        """Verify settings load with empty datastore configuration."""
        settings = load_settings({"ATLAS_ENV": "test"})

        self.assertIsNone(settings.database_url)
        self.assertIsNone(settings.sqlite_path)
        self.assertIsNone(settings.redis_url)
        self.assertIsNone(settings.qdrant_url)
        self.assertIsNone(settings.neo4j_url)


if __name__ == "__main__":
    unittest.main()
