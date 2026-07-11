"""Document data models."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, confloat


class DocumentFormat(str, Enum):
    """Supported document formats."""
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    TEXT = "text"


class DocumentChunk(BaseModel):
    """A chunk of a document with embeddings."""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: UUID = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk text content")
    page_number: Optional[int] = Field(None, description="Page number (for PDFs)")
    section: Optional[str] = Field(None, description="Section title")
    embedding: Optional[list[float]] = Field(None, description="Vector embedding")
    start_char: int = Field(..., description="Character offset in original document")
    end_char: int = Field(..., description="Character offset in original document")
    confidence_score: confloat(ge=0.0, le=1.0) = Field(1.0, description="OCR confidence (0.0-1.0)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentMetadata(BaseModel):
    """Document metadata."""
    document_id: UUID = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    file_format: DocumentFormat = Field(..., description="File format")
    file_size_bytes: int = Field(..., description="File size in bytes")
    page_count: Optional[int] = Field(None, description="Number of pages")
    author: Optional[str] = Field(None, description="Document author")
    created_date: Optional[datetime] = Field(None, description="Document creation date")
    modified_date: Optional[datetime] = Field(None, description="Last modification date")
    language: str = Field("en", description="Document language code")
    chunk_count: int = Field(0, description="Total chunks generated")
    indexed: bool = Field(False, description="Is document indexed")
    indexed_at: Optional[datetime] = Field(None, description="Index timestamp")
    has_images: bool = Field(False, description="Contains images")
    image_count: int = Field(0, description="Number of images")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentVersion(BaseModel):
    """Document version tracking."""
    version_id: str = Field(..., description="Version identifier")
    document_id: UUID = Field(..., description="Parent document ID")
    version_number: int = Field(..., description="Version sequence number")
    file_hash: str = Field(..., description="SHA256 hash of file")
    file_size_bytes: int = Field(..., description="File size")
    chunk_count: int = Field(..., description="Chunks in this version")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    indexed_at: Optional[datetime] = Field(None, description="Indexing completion time")
    status: str = Field("pending", description="Version status: pending, processing, indexed, failed")


class DocumentSourceHighlight(BaseModel):
    """Citation source highlighting."""
    chunk_id: str = Field(..., description="Chunk ID")
    citation_id: str = Field(..., description="Citation ID")
    highlighted_text: str = Field(..., description="Highlighted excerpt")
    context_before: Optional[str] = Field(None, description="Context before excerpt")
    context_after: Optional[str] = Field(None, description="Context after excerpt")
