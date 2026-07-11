"""Filesystem-backed storage provider."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from atlas_backend.data.providers import StorageProvider


class StorageProviderImpl(StorageProvider):
    """Concrete storage provider implementation using the local filesystem."""

    def __init__(self, root_directory: str | None = None) -> None:
        self.root_directory = Path(root_directory or os.environ.get("ATLAS_STORAGE_ROOT", Path.cwd() / "atlas-storage"))
        self.root_directory.mkdir(parents=True, exist_ok=True)

    def _resolve(self, remote_path: str) -> Path:
        path = (self.root_directory / remote_path.lstrip("/")).resolve()
        if self.root_directory not in path.parents and path != self.root_directory:
            raise ValueError("Remote path escapes storage root.")
        return path

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        source = Path(local_path)
        if not source.is_file():
            return False
        destination = self._resolve(remote_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return True

    def download_file(self, remote_path: str, local_path: str) -> bool:
        source = self._resolve(remote_path)
        if not source.is_file():
            return False
        destination = Path(local_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return True

    def delete_file(self, remote_path: str) -> bool:
        target = self._resolve(remote_path)
        if not target.exists():
            return False
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        return True

    def list_files(self, prefix: str = "") -> list:
        files: list[str] = []
        prefix_path = self._resolve(prefix) if prefix else self.root_directory
        if not prefix_path.exists():
            return files
        for path in prefix_path.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(self.root_directory)).replace("\\", "/"))
        return sorted(files)

    def get_download_url(self, remote_path: str, expires_in: int = 3600) -> str:
        return f"file://{self._resolve(remote_path)}?expires_in={expires_in}"

    def get_upload_url(self, remote_path: str, expires_in: int = 3600) -> str:
        return f"file://{self._resolve(remote_path)}?expires_in={expires_in}"
