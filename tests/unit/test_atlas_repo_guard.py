from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.diagnostics.atlas_repo_guard import (
    REQUIRED_DIRECTORIES,
    REQUIRED_FILES,
    validate_repository,
)


class AtlasRepoGuardTests(unittest.TestCase):
    def test_required_paths_are_declared(self) -> None:
        self.assertIn("README.md", REQUIRED_FILES)
        self.assertIn("ARCHITECTURE.md", REQUIRED_FILES)
        self.assertIn("apps/web", REQUIRED_DIRECTORIES)
        self.assertIn("backend", REQUIRED_DIRECTORIES)

    def test_current_repository_passes_validation(self) -> None:
        root = Path(__file__).resolve().parents[2]
        failures = validate_repository(root)
        self.assertEqual([], failures)

    def test_missing_items_are_reported(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            failures = validate_repository(Path(temporary_directory))
        self.assertTrue(failures)
        self.assertTrue(any("README.md" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
