"""Repository interface definitions for data access abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base interface for all repositories."""

    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    def read(self, entity_id: str) -> T | None:
        """Read an entity by ID."""
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID."""
        pass

    @abstractmethod
    def list(self, limit: int = 100, offset: int = 0) -> list[T]:
        """List entities with pagination."""
        pass


class UserRepository(ABC):
    """Interface for user persistence."""

    @abstractmethod
    def create_user(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new user."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        """Get a user by ID."""
        pass

    @abstractmethod
    def update_user(self, user_id: str, user_data: dict[str, Any]) -> dict[str, Any]:
        """Update a user."""
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        pass


class ProjectRepository(ABC):
    """Interface for project persistence."""

    @abstractmethod
    def create_project(self, project_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new project."""
        pass

    @abstractmethod
    def get_project_by_id(self, project_id: str) -> dict[str, Any] | None:
        """Get a project by ID."""
        pass

    @abstractmethod
    def list_user_projects(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """List projects for a user."""
        pass

    @abstractmethod
    def update_project(self, project_id: str, project_data: dict[str, Any]) -> dict[str, Any]:
        """Update a project."""
        pass

    @abstractmethod
    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        pass


class DocumentRepository(ABC):
    """Interface for document persistence."""

    @abstractmethod
    def create_document(self, document_data: dict[str, Any]) -> dict[str, Any]:
        """Create document metadata."""
        pass

    @abstractmethod
    def get_document_by_id(self, document_id: str) -> dict[str, Any] | None:
        """Get document metadata by ID."""
        pass

    @abstractmethod
    def list_project_documents(self, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """List documents in a project."""
        pass

    @abstractmethod
    def update_document(self, document_id: str, document_data: dict[str, Any]) -> dict[str, Any]:
        """Update document metadata."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> bool:
        """Delete document metadata."""
        pass


class LocalProfileRepository(ABC):
    """Interface for local profile persistence in SQLite."""

    @abstractmethod
    def create_local_profile(self, profile_data: dict[str, Any]) -> dict[str, Any]:
        """Create a local profile."""
        pass

    @abstractmethod
    def get_local_profile(self) -> dict[str, Any] | None:
        """Get the single local profile."""
        pass

    @abstractmethod
    def update_local_profile(self, profile_data: dict[str, Any]) -> dict[str, Any]:
        """Update the local profile."""
        pass


class LocalProjectRepository(ABC):
    """Interface for local project persistence in SQLite."""

    @abstractmethod
    def create_local_project(self, project_data: dict[str, Any]) -> dict[str, Any]:
        """Create a local project index."""
        pass

    @abstractmethod
    def get_local_project(self, project_id: str) -> dict[str, Any] | None:
        """Get a local project by ID."""
        pass

    @abstractmethod
    def list_local_projects(self, limit: int = 100) -> list[dict[str, Any]]:
        """List all local projects."""
        pass

    @abstractmethod
    def update_local_project(self, project_id: str, project_data: dict[str, Any]) -> dict[str, Any]:
        """Update a local project."""
        pass

    @abstractmethod
    def delete_local_project(self, project_id: str) -> bool:
        """Delete a local project."""
        pass


class SyncQueueRepository(ABC):
    """Interface for sync queue persistence in SQLite."""

    @abstractmethod
    def enqueue_sync(self, sync_item: dict[str, Any]) -> dict[str, Any]:
        """Add an item to the sync queue."""
        pass

    @abstractmethod
    def dequeue_sync(self, limit: int = 10) -> list[dict[str, Any]]:
        """Retrieve pending sync items."""
        pass

    @abstractmethod
    def mark_synced(self, sync_id: str) -> bool:
        """Mark a sync item as completed."""
        pass

    @abstractmethod
    def list_pending_syncs(self) -> list[dict[str, Any]]:
        """List all pending sync items."""
        pass
