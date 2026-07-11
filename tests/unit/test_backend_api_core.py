from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from atlas_backend.core.config import AtlasEnvironment, AtlasRuntimeMode, load_settings
from atlas_backend.core.errors import AtlasErrorCode, AtlasException, map_exception_to_error_response
from atlas_backend.core.health import ComponentState, ServiceState, build_readiness_report
from atlas_backend.core.responses import create_success_response
from atlas_backend.core.security import (
    Permission,
    PrincipalKind,
    RequestPrincipal,
    require_cloud_user,
    require_permission,
)
from atlas_backend.api.app import create_app


class BackendApiCoreTests(unittest.TestCase):
    def test_settings_load_from_environment_mapping(self) -> None:
        settings = load_settings(
            {
                "ATLAS_ENV": "test",
                "ATLAS_RUNTIME_MODE": "local",
                "ATLAS_API_BASE_PATH": "/api/v1",
                "ATLAS_LOCAL_MODE_ENABLED": "true",
                "ATLAS_CLOUD_SYNC_ENABLED": "false",
                "ATLAS_LOG_LEVEL": "warning",
                "ATLAS_CORS_ALLOWED_ORIGINS": "http://localhost:5173,https://atlas.example",
            }
        )

        self.assertEqual(AtlasEnvironment.TEST, settings.environment)
        self.assertEqual(AtlasRuntimeMode.LOCAL, settings.runtime_mode)
        self.assertEqual(("http://localhost:5173", "https://atlas.example"), settings.cors_allowed_origins)
        self.assertTrue(settings.local_mode_enabled)
        self.assertFalse(settings.cloud_sync_enabled)
        self.assertEqual("warning", settings.log_level)

    def test_success_response_uses_standard_envelope(self) -> None:
        response = create_success_response({"status": "ok"}, meta={"request_id": "test-request"})

        self.assertTrue(response.success)
        self.assertEqual({"status": "ok"}, response.data)
        self.assertEqual("test-request", response.meta["request_id"])
        self.assertIsNotNone(response.timestamp.tzinfo)

    def test_error_response_mapping_uses_standard_envelope(self) -> None:
        exception = AtlasException(
            AtlasErrorCode.VALIDATION_ERROR,
            "Invalid request.",
            details={"field": "query"},
        )

        response = map_exception_to_error_response(exception)

        self.assertFalse(response.success)
        self.assertEqual(422, response.code)
        self.assertEqual("Invalid request.", response.error)
        self.assertEqual({"field": "query"}, response.details)

    def test_readiness_report_marks_cloud_sync_as_optional_when_disabled(self) -> None:
        settings = load_settings({"ATLAS_ENV": "test", "ATLAS_CLOUD_SYNC_ENABLED": "false"})

        report = build_readiness_report(settings)
        components = {component.name: component for component in report.components}

        self.assertEqual(ServiceState.HEALTHY, report.status)
        self.assertEqual(ComponentState.HEALTHY, components["api"].state)
        self.assertEqual(ComponentState.HEALTHY, components["local_mode"].state)
        self.assertEqual(ComponentState.NOT_CONFIGURED, components["cloud_sync"].state)
        self.assertFalse(components["cloud_sync"].required)

    def test_cloud_user_requirement_rejects_local_device(self) -> None:
        principal = RequestPrincipal(
            principal_id="device-profile",
            kind=PrincipalKind.LOCAL_DEVICE,
            device_id="device-1",
        )

        with self.assertRaises(AtlasException) as context:
            require_cloud_user(principal)

        self.assertEqual(AtlasErrorCode.UNAUTHORIZED, context.exception.code)

    def test_permission_requirement_rejects_missing_permission(self) -> None:
        principal = RequestPrincipal(
            principal_id="user-1",
            kind=PrincipalKind.CLOUD_USER,
            permissions=frozenset({Permission.READ_SELF}),
        )

        with self.assertRaises(AtlasException) as context:
            require_permission(principal, Permission.RUN_RESEARCH)

        self.assertEqual(AtlasErrorCode.FORBIDDEN, context.exception.code)

    def test_app_factory_creates_app_with_settings(self) -> None:
        app = create_app(load_settings({"ATLAS_ENV": "test", "ATLAS_API_BASE_PATH": "/api/v1"}))
        self.assertIsNotNone(app)
        self.assertTrue(hasattr(app, "routes"))
        self.assertGreater(len(app.routes), 0)


if __name__ == "__main__":
    unittest.main()
