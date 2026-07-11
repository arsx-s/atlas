"""Document indexing with vector search."""

from abc import ABC, abstractmethod
from uuid import UUID

from ..models import DocumentChunk


class DocumentIndexer(ABC):
    """Abstract document indexing interface."""

    @abstractmethod
    async def index_chunks(self, chunks: list[DocumentChunk], collection_name: str = "documents") -> bool:
        """Index document chunks with embeddings."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        collection_name: str = "documents",
        limit: int = 10,
    ) -> list[DocumentChunk]:
        """Search indexed chunks by semantic similarity."""
        pass

    @abstractmethod
    async def delete_document(self, document_id: UUID, collection_name: str = "documents") -> bool:
        """Delete all chunks for a document."""
        pass

    @abstractmethod
    async def get_document_chunks(
        self, document_id: UUID, collection_name: str = "documents"
    ) -> list[DocumentChunk]:
        """Retrieve all chunks for a document."""
        pass
