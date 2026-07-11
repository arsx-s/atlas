from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


REQUIRED_FILES: tuple[str, ...] = (
    "README.md",
    "ARCHITECTURE.md",
    "SECURITY.md",
    ".env.example",
    ".gitignore",
    "package.json",
    "Dockerfile.backend",
    "Dockerfile.frontend",
    "docker-compose.yml",
    "docker-compose.prod.yml",
)

REQUIRED_DIRECTORIES: tuple[str, ...] = (
    "apps/web",
    "backend",
)

FORBIDDEN_ENV_VALUES: tuple[str, ...] = (
    "sk-",
    "real-secret",
    "production-secret",
    "password123",
)


def validate_repository(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.is_file():
            failures.append(f"Missing required file: {relative_path}")

    for relative_path in REQUIRED_DIRECTORIES:
        path = root / relative_path
        if not path.is_dir():
            failures.append(f"Missing required directory: {relative_path}")

    failures.extend(_validate_environment_example(root))
    failures.extend(_validate_package_manifest(root))

    return failures


def _validate_environment_example(root: Path) -> list[str]:
    environment_path = root / ".env.example"
    if not environment_path.is_file():
        return []

    content = environment_path.read_text(encoding="utf-8")
    failures: list[str] = []

    for forbidden_value in FORBIDDEN_ENV_VALUES:
        if forbidden_value in content:
            failures.append(f"Forbidden secret-like value found in .env.example: {forbidden_value}")

    return failures


def _validate_package_manifest(root: Path) -> list[str]:
    package_path = root / "package.json"
    if not package_path.is_file():
        return []

    try:
        manifest = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"package.json is invalid JSON: {error}"]

    failures: list[str] = []
    if manifest.get("private") is not True:
        failures.append("package.json must be private for the monorepo root")

    workspaces = manifest.get("workspaces")
    if not isinstance(workspaces, list) or "apps/*" not in workspaces:
        failures.append("package.json must define apps/* workspace")

    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate the Atlas repository structure.")
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Atlas repository root. Defaults to the current working directory.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    failures = validate_repository(root)

    if failures:
        print("Atlas verification failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Atlas verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
