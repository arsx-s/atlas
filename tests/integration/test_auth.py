"""Integration tests for auth and export API endpoints."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import gc
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from atlas_backend.core.config import load_settings
from atlas_backend.api.app import create_app


class AuthIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.db_path = self.tmpdir / "atlas.db"
        self.settings = load_settings({
            "ATLAS_ENV": "test",
            "ATLAS_SQLITE_PATH": str(self.db_path),
            "ATLAS_JWT_SECRET": "test-secret-for-integration-tests",
            "ATLAS_RATE_LIMIT_ENABLED": "false",
        })
        self.app = create_app(self.settings)

    def tearDown(self):
        gc.collect()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _client(self):
        from fastapi.testclient import TestClient
        return TestClient(self.app)

    def test_health_endpoint(self):
        client = self._client()
        resp = client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("data", data)
        self.assertEqual(data["data"]["status"], "healthy")

    def test_register_and_login(self):
        client = self._client()
        register_resp = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "display_name": "Test User",
        })
        self.assertEqual(register_resp.status_code, 200)
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
        })
        self.assertEqual(login_resp.status_code, 200)
        login_data = login_resp.json()
        self.assertIn("access_token", login_data["data"])

    def test_register_duplicate_email(self):
        client = self._client()
        client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "password": "SecurePass123!",
        })
        resp = client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "password": "AnotherPass456!",
        })
        self.assertEqual(resp.status_code, 409)

    def test_login_wrong_password(self):
        client = self._client()
        client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "password": "CorrectPass1!",
        })
        resp = client.post("/api/v1/auth/login", json={
            "email": "user@example.com",
            "password": "WrongPass1!",
        })
        self.assertEqual(resp.status_code, 401)

    def test_auth_me_with_token(self):
        client = self._client()
        client.post("/api/v1/auth/register", json={
            "email": "me@example.com",
            "password": "TestPass123!",
            "display_name": "Me",
        })
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "me@example.com",
            "password": "TestPass123!",
        })
        token = login_resp.json()["data"]["access_token"]
        me_resp = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        self.assertEqual(me_resp.status_code, 200)
        me_data = me_resp.json()["data"]
        self.assertTrue(me_data["authenticated"])
        self.assertEqual(me_data["email"], "me@example.com")

    def test_auth_me_anonymous(self):
        client = self._client()
        resp = client.get("/api/v1/auth/me")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["data"]["authenticated"])

    def test_auth_me_invalid_token(self):
        client = self._client()
        resp = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid-token-here",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["data"]["authenticated"])


class ExportIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.db_path = self.tmpdir / "atlas.db"
        self.settings = load_settings({
            "ATLAS_ENV": "test",
            "ATLAS_SQLITE_PATH": str(self.db_path),
            "ATLAS_RATE_LIMIT_ENABLED": "false",
        })
        self.app = create_app(self.settings)

    def tearDown(self):
        gc.collect()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _client(self):
        from fastapi.testclient import TestClient
        return TestClient(self.app)

    def _create_session_with_report(self, client):
        proj_resp = client.post("/api/v1/projects", json={
            "name": "Test Project",
            "user_id": "test-user",
        })
        proj_id = proj_resp.json()["data"]["project"]["project_id"]
        session_resp = client.post("/api/v1/research-sessions", json={
            "project_id": proj_id,
            "title": "Test Research",
            "query": "What is the meaning of life?",
            "user_id": "test-user",
        })
        session_id = session_resp.json()["data"]["session_id"]
        client.post(f"/api/v1/research-sessions/{session_id}/chat", json={
            "message": "Tell me about life",
        })
        return session_id

    def test_export_markdown(self):
        client = self._client()
        session_id = self._create_session_with_report(client)
        resp = client.get(f"/api/v1/export/{session_id}/markdown")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/markdown", resp.headers["content-type"])
        self.assertIn("atlas-report-", resp.headers["content-disposition"])

    def test_export_json(self):
        client = self._client()
        session_id = self._create_session_with_report(client)
        resp = client.get(f"/api/v1/export/{session_id}/json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("json", resp.headers["content-type"])

    def test_export_missing_session(self):
        client = self._client()
        resp = client.get("/api/v1/export/nonexistent/markdown")
        self.assertEqual(resp.status_code, 404)

    def test_export_markdown_has_content(self):
        client = self._client()
        session_id = self._create_session_with_report(client)
        resp = client.get(f"/api/v1/export/{session_id}/markdown")
        body = resp.text
        self.assertIn("Test Research", body)
        self.assertIn("What is the meaning of life?", body)


class MonitoringIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.settings = load_settings({
            "ATLAS_ENV": "test",
            "ATLAS_SQLITE_PATH": ":memory:",
            "ATLAS_RATE_LIMIT_ENABLED": "false",
        })
        self.app = create_app(self.settings)

    def _client(self):
        from fastapi.testclient import TestClient
        return TestClient(self.app)

    def test_ping(self):
        resp = self._client().get("/api/v1/monitoring/ping")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"ping": "pong"})

    def test_healthz(self):
        resp = self._client().get("/api/v1/monitoring/healthz")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
