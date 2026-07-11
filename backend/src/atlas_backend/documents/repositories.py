"""Document repository for PostgreSQL."""

from typing import Optional
from uuid import UUID

from ...documents.models import DocumentMetadata, DocumentChunk, DocumentVersion


class PostgresDocumentRepository:
    """PostgreSQL document repository."""

    def __init__(self, session):
        self.session = session

    async def save_document(self, metadata: DocumentMetadata) -> UUID:
        """Save document metadata."""
        raise NotImplementedError("ORM model mapping required")

    async def get_document(self, document_id: UUID) -> Optional[DocumentMetadata]:
        """Get document metadata."""
        raise NotImplementedError("ORM model mapping required")

    async def save_chunks(self, chunks: list[DocumentChunk]) -> bool:
        """Save document chunks."""
        raise NotImplementedError("ORM model mapping required")

    async def get_chunks(self, document_id: UUID) -> list[DocumentChunk]:
        """Get document chunks."""
        raise NotImplementedError("ORM model mapping required")

    async def save_version(self, version: DocumentVersion) -> str:
        """Save document version."""
        raise NotImplementedError("ORM model mapping required")
