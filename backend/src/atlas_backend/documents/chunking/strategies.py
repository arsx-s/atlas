"""Document chunking implementations."""

from abc import ABC, abstractmethod
from typing import Optional

from ..models import DocumentChunk


class ChunkingStrategy(ABC):
    """Abstract document chunking strategy."""

    @abstractmethod
    async def chunk(self, text: str, document_id: str, metadata: dict = None) -> list[DocumentChunk]:
        """Split document into chunks."""
        pass

    def _create_chunk(
        self, 
        chunk_id: str,
        document_id: str,
        content: str,
        start_char: int,
        end_char: int,
        page_number: Optional[int] = None,
        section: Optional[str] = None,
    ) -> DocumentChunk:
        """Create a DocumentChunk."""
        return DocumentChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            content=content,
            page_number=page_number,
            section=section,
            start_char=start_char,
            end_char=end_char,
        )


class SemanticChunkingStrategy(ChunkingStrategy):
    """Chunk by semantic boundaries (paragraphs, sections)."""

    def __init__(self, min_chunk_size: int = 100, max_chunk_size: int = 2000):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    async def chunk(self, text: str, document_id: str, metadata: dict = None) -> list[DocumentChunk]:
        """Split text by paragraphs and sections."""
        chunks = []
        chunk_id = 0
        current_pos = 0

        for paragraph in text.split("\n\n"):
            if not paragraph.strip():
                continue

            if len(paragraph) > self.max_chunk_size:
                for sub_chunk in self._split_large_paragraph(paragraph):
                    chunk_id_str = f"{document_id}:{chunk_id}"
                    chunk = self._create_chunk(
                        chunk_id_str,
                        document_id,
                        sub_chunk,
                        current_pos,
                        current_pos + len(sub_chunk),
                    )
                    chunks.append(chunk)
                    chunk_id += 1
            else:
                chunk_id_str = f"{document_id}:{chunk_id}"
                chunk = self._create_chunk(
                    chunk_id_str,
                    document_id,
                    paragraph,
                    current_pos,
                    current_pos + len(paragraph),
                )
                chunks.append(chunk)
                chunk_id += 1

            current_pos += len(paragraph) + 2

        return chunks

    def _split_large_paragraph(self, text: str, overlap: int = 50) -> list[str]:
        """Split oversized paragraph with overlap."""
        chunks = []
        for i in range(0, len(text), self.max_chunk_size - overlap):
            chunks.append(text[i : i + self.max_chunk_size])
        return chunks


class SlidingWindowChunkingStrategy(ChunkingStrategy):
    """Chunk with sliding window (fixed size, overlapping)."""

    def __init__(self, chunk_size: int = 1024, overlap: int = 256):
        self.chunk_size = chunk_size
        self.overlap = overlap

    async def chunk(self, text: str, document_id: str, metadata: dict = None) -> list[DocumentChunk]:
        """Split text using sliding window."""
        chunks = []
        chunk_id = 0
        step = self.chunk_size - self.overlap

        for i in range(0, len(text), step):
            chunk_text = text[i : i + self.chunk_size]
            if len(chunk_text) < self.chunk_size // 2:
                break

            chunk_id_str = f"{document_id}:{chunk_id}"
            chunk = self._create_chunk(
                chunk_id_str,
                document_id,
                chunk_text,
                i,
                i + len(chunk_text),
            )
            chunks.append(chunk)
            chunk_id += 1

        return chunks
