"""Document Q&A interface."""

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class DocumentQAQuery(BaseModel):
    """Query for document Q&A."""
    question: str
    context_limit: int = 3
    search_depth: str = "standard"  # standard, deep, comprehensive


class DocumentQAResponse(BaseModel):
    """Response from document Q&A."""
    answer: str
    confidence_score: float
    sources: list[str]
    relevant_chunks: list[str]


class DocumentQAInterface(ABC):
    """Document Q&A interface for querying document context."""

    @abstractmethod
    async def query(
        self,
        document_id: str,
        query: DocumentQAQuery,
        collection_name: str = "documents",
    ) -> DocumentQAResponse:
        """Query document with AI context awareness."""
        pass

    @abstractmethod
    async def extract_citations(
        self,
        document_id: str,
        query: str,
        limit: int = 5,
    ) -> list[dict]:
        """Extract citations from document for a query."""
        pass
