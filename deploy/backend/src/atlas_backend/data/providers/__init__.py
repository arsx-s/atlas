"""Provider interface definitions for external services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class QdrantProvider(ABC):
    """Interface for Qdrant vector database access."""

    @abstractmethod
    def create_collection(self, collection_name: str, vector_size: int) -> bool:
        """Create a vector collection."""
        pass

    @abstractmethod
    def upsert_vectors(self, collection_name: str, points: list[dict[str, Any]]) -> bool:
        """Upsert vectors into a collection."""
        pass

    @abstractmethod
    def search_vectors(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors."""
        pass

    @abstractmethod
    def delete_vectors(self, collection_name: str, point_ids: list[int]) -> bool:
        """Delete vectors from a collection."""
        pass


class Neo4jProvider(ABC):
    """Interface for Neo4j graph database access."""

    @abstractmethod
    def execute_query(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a Cypher query."""
        pass

    @abstractmethod
    def create_node(self, label: str, properties: dict[str, Any]) -> dict[str, Any]:
        """Create a graph node."""
        pass

    @abstractmethod
    def create_relationship(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: str,
        properties: dict[str, Any] | None = None,
    ) -> bool:
        """Create a relationship between nodes."""
        pass

    @abstractmethod
    def delete_node(self, node_id: str) -> bool:
        """Delete a node."""
        pass


class RedisProvider(ABC):
    """Interface for Redis cache and session storage."""

    @abstractmethod
    def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Set a key-value pair."""
        pass

    @abstractmethod
    def get(self, key: str) -> str | None:
        """Get a value by key."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a key."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        pass

    @abstractmethod
    def incr(self, key: str) -> int:
        """Increment a counter."""
        pass

    @abstractmethod
    def lpush(self, key: str, values: list[str]) -> int:
        """Push values to a list."""
        pass

    @abstractmethod
    def lpop(self, key: str, count: int = 1) -> list[str]:
        """Pop values from a list."""
        pass


class StorageProvider(ABC):
    """Interface for object storage (filesystem or S3-compatible)."""

    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload a file to storage."""
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download a file from storage."""
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """Delete a file from storage."""
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> list[str]:
        """List files in storage."""
        pass

    @abstractmethod
    def get_download_url(self, remote_path: str, expires_in: int = 3600) -> str:
        """Get a time-limited download URL."""
        pass

    @abstractmethod
    def get_upload_url(self, remote_path: str, expires_in: int = 3600) -> str:
        """Get a time-limited upload URL."""
        pass
