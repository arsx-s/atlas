from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import shutil
import gc
import unittest

ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from atlas_backend.core.config import load_settings
from atlas_backend.persistence import AtlasLocalStore
from atlas_backend.auth.service import AuthService
from atlas_backend.sync.service import SyncService
from atlas_backend.search.service import SearchService
from atlas_backend.search.models import SearchResult


class AuthSyncTests(unittest.TestCase):
    def test_auth_registration_and_login(self) -> None:
        tmpdir = Path(tempfile.mkdtemp())
        try:
            settings = load_settings({"ATLAS_ENV": "test", "ATLAS_SQLITE_PATH": str(tmpdir / "atlas.db")})
            store = AtlasLocalStore(settings.sqlite_path)
            service = AuthService(settings, store)
            user = service.register_user("test@example.com", "strong-password", "Test User")
            self.assertEqual(user["email"], "test@example.com")
            verified = service.verify_credentials("test@example.com", "strong-password")
            self.assertIsNotNone(verified)
            tokens = service.issue_tokens(verified)
            self.assertTrue(tokens.access_token)
            self.assertTrue(tokens.refresh_token)
        finally:
            gc.collect()
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_sync_queue_round_trip(self) -> None:
        tmpdir = Path(tempfile.mkdtemp())
        try:
            settings = load_settings({"ATLAS_ENV": "test", "ATLAS_SQLITE_PATH": str(tmpdir / "atlas.db")})
            store = AtlasLocalStore(settings.sqlite_path)
            service = SyncService(store)
            record = service.enqueue("project", "proj-1", "upsert", {"name": "Atlas"})
            pending = service.list_pending()
            self.assertEqual(len(pending), 1)
            self.assertEqual(pending[0]["sync_id"], record["sync_id"])
        finally:
            gc.collect()
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_search_service_ranks_and_dedupes(self) -> None:
        class Provider:
            async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
                return [
                    SearchResult(title="Alpha", url="https://example.com/a", source="one", doi="10.1/a", citations=10),
                    SearchResult(title="Alpha duplicate", url="https://example.com/a", source="two", doi="10.1/a", citations=1),
                ]

        service = SearchService(providers=[Provider()])
        results = self._run(service.search("alpha"))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Alpha")

    def _run(self, coroutine):
        import asyncio

        return asyncio.run(coroutine)


if __name__ == "__main__":
    unittest.main()
