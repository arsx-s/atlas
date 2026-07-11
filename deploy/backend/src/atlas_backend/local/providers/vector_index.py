"""Local vector indexing (in-process)."""

from typing import Optional
from uuid import UUID

from ...documents.indexing import DocumentIndexer
from ...documents.models import DocumentChunk


class LocalVectorIndex(DocumentIndexer):
    """In-process vector index for local mode."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = {}  # collection_name -> {document_id -> [chunks]}

    async def index_chunks(self, chunks: list[DocumentChunk], collection_name: str = "documents") -> bool:
        """Index chunks in local memory."""
        if collection_name not in self.index:
            self.index[collection_name] = {}

        for chunk in chunks:
            doc_id = str(chunk.document_id)
            if doc_id not in self.index[collection_name]:
                self.index[collection_name][doc_id] = []
            self.index[collection_name][doc_id].append(chunk)

        return True

    async def search(
        self,
        query: str,
        collection_name: str = "documents",
        limit: int = 10,
    ) -> list[DocumentChunk]:
        """Search indexed chunks (naive implementation - returns all)."""
        if collection_name not in self.index:
            return []

        results = []
        for doc_chunks in self.index[collection_name].values():
            results.extend(doc_chunks)

        return results[:limit]

    async def delete_document(self, document_id: UUID, collection_name: str = "documents") -> bool:
        """Delete all chunks for a document."""
        if collection_name in self.index:
            self.index[collection_name].pop(str(document_id), None)
        return True

    async def get_document_chunks(
        self, document_id: UUID, collection_name: str = "documents"
    ) -> list[DocumentChunk]:
        """Retrieve all chunks for a document."""
        if collection_name not in self.index:
            return []
        return self.index[collection_name].get(str(document_id), [])
