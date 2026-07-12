"""Document ingestion pipeline."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from .models import DocumentFormat, DocumentMetadata, DocumentVersion
from .parsers import DocumentParser


class DocumentIngestionPipeline:
    """Orchestrates document ingestion: parsing, chunking, indexing, versioning."""

    def __init__(self, parser: DocumentParser, chunking_strategy, indexer, embedding_provider):
        self.parser = parser
        self.chunking_strategy = chunking_strategy
        self.indexer = indexer
        self.embedding_provider = embedding_provider

    async def ingest(
        self,
        file_path: Path,
        title: Optional[str] = None,
        collection_name: str = "documents",
    ) -> tuple[DocumentMetadata, DocumentVersion]:
        """Ingest document: parse, chunk, embed, index, and track version."""
        # Validate file
        if not await self.parser.validate_file(file_path):
            raise ValueError(f"Invalid or missing file: {file_path}")

        # Parse content
        parsed = await self.parser.parse(file_path)

        # Create document metadata
        document_id = uuid4()
        metadata = DocumentMetadata(
            document_id=document_id,
            title=title or parsed.title or file_path.stem,
            file_format=self._get_format(file_path),
            file_size_bytes=file_path.stat().st_size,
            author=parsed.metadata.get("author"),
            created_date=parsed.metadata.get("created_date"),
            modified_date=parsed.metadata.get("modified_date"),
            page_count=parsed.metadata.get("pages"),
            has_images=len(parsed.images) > 0,
            image_count=len(parsed.images),
        )

        # Chunk document
        chunks = await self.chunking_strategy.chunk(parsed.text, str(document_id))

        # Generate embeddings for chunks
        for chunk in chunks:
            embedding = await self.embedding_provider.embed(chunk.content)
            chunk.embedding = embedding

        # Index chunks
        await self.indexer.index_chunks(chunks, collection_name)

        # Create version record
        version = DocumentVersion(
            version_id=f"{document_id}:v1",
            document_id=document_id,
            version_number=1,
            file_hash=self._compute_file_hash(file_path),
            file_size_bytes=file_path.stat().st_size,
            chunk_count=len(chunks),
            indexed_at=datetime.now(timezone.utc),
            status="indexed",
        )

        # Update metadata
        metadata.chunk_count = len(chunks)
        metadata.indexed = True
        metadata.indexed_at = datetime.now(timezone.utc)

        return metadata, version

    def _get_format(self, file_path: Path) -> DocumentFormat:
        """Determine document format from extension."""
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return DocumentFormat.PDF
        elif ext == ".docx":
            return DocumentFormat.DOCX
        elif ext == ".md":
            return DocumentFormat.MARKDOWN
        else:
            return DocumentFormat.TEXT

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file."""
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
