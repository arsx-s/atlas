"""Tests for M6, M7, M8."""

import unittest
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pathlib import Path

# M6 Document Intelligence Tests
from atlas_backend.documents.models import (
    DocumentChunk,
    DocumentMetadata,
    DocumentVersion,
    DocumentFormat,
)
from atlas_backend.documents.parsers.base import DocumentParser
from atlas_backend.documents.parsers.markdown import MarkdownParser
from atlas_backend.documents.parsers.text import TextParser
from atlas_backend.documents.chunking.strategies import (
    SemanticChunkingStrategy,
    SlidingWindowChunkingStrategy,
)
from atlas_backend.documents.ocr import OCRProvider


# M7 Project Tests
from atlas_backend.projects.models import Project, Collection, Note, Tag, SavedResearch
from atlas_backend.projects.repositories import (
    ProjectRepository,
    CollectionRepository,
    NoteRepository,
    TagRepository,
)
from atlas_backend.projects.manager import ProjectManager


# M8 Local Intelligence Tests
from atlas_backend.local.models import LocalModel, LocalModelRegistry
from atlas_backend.local.hardware import HardwareDetector, GPUConfig, GPUType
from atlas_backend.local.providers.embedding import LocalEmbeddingProvider
from atlas_backend.local.providers.vector_index import LocalVectorIndex
from atlas_backend.local.cache import LocalCache
from atlas_backend.local.memory import LocalMemoryProvider, MemoryEntry
from atlas_backend.local.health import check_local_runtime_health


# ==================== M6 Tests ====================

class TestDocumentModels(unittest.IsolatedAsyncioTestCase):
    """Test document data models."""

    def test_document_chunk_creation(self):
        """Test creating a document chunk."""
        doc_id = uuid4()
        chunk = DocumentChunk(
            chunk_id="chunk-1",
            document_id=doc_id,
            content="Test content",
            start_char=0,
            end_char=12,
        )
        assert chunk.chunk_id == "chunk-1"
        assert chunk.document_id == doc_id
        assert chunk.confidence_score == 1.0

    def test_document_metadata_creation(self):
        """Test creating document metadata."""
        doc_id = uuid4()
        metadata = DocumentMetadata(
            document_id=doc_id,
            title="Test Doc",
            file_format=DocumentFormat.PDF,
            file_size_bytes=1024,
        )
        assert metadata.title == "Test Doc"
        assert metadata.file_format == DocumentFormat.PDF

    def test_document_version_tracking(self):
        """Test document version creation."""
        doc_id = uuid4()
        version = DocumentVersion(
            version_id="v1",
            document_id=doc_id,
            version_number=1,
            file_hash="abc123",
            file_size_bytes=1024,
            chunk_count=5,
            status="indexed",
        )
        assert version.version_number == 1
        assert version.status == "indexed"


class TestMarkdownParser(unittest.IsolatedAsyncioTestCase):
    """Test Markdown parser."""

    async def test_parse_markdown(self):
        """Test parsing markdown content."""
        parser = MarkdownParser()
        assert parser.supported_extension() == ".md"

    def test_extract_title_from_markdown(self):
        """Test extracting title from markdown."""
        parser = MarkdownParser()
        content = "# My Title\n\nSome content here."
        title = parser._extract_title(content)
        assert title == "My Title"


class TestChunkingStrategies(unittest.IsolatedAsyncioTestCase):
    """Test document chunking strategies."""

    async def test_semantic_chunking(self):
        """Test semantic chunking strategy."""
        strategy = SemanticChunkingStrategy(min_chunk_size=50, max_chunk_size=500)
        doc_id = uuid4()
        text = "First paragraph.\n\nSecond paragraph here."
        chunks = await strategy.chunk(text, str(doc_id))
        assert len(chunks) > 0
        assert chunks[0].document_id == doc_id

    async def test_sliding_window_chunking(self):
        """Test sliding window chunking strategy."""
        strategy = SlidingWindowChunkingStrategy(chunk_size=100, overlap=20)
        doc_id = uuid4()
        text = "A" * 200
        chunks = await strategy.chunk(text, str(doc_id))
        assert len(chunks) > 0


# ==================== M7 Tests ====================

class TestProjectModels(unittest.IsolatedAsyncioTestCase):
    """Test project data models."""

    def test_project_creation(self):
        """Test creating a project."""
        user_id = uuid4()
        project = Project(
            project_id=uuid4(),
            user_id=user_id,
            name="Test Project",
            description="A test project",
        )
        assert project.name == "Test Project"
        assert project.user_id == user_id

    def test_collection_creation(self):
        """Test creating a collection."""
        collection = Collection(
            collection_id=uuid4(),
            project_id=uuid4(),
            name="Test Collection",
        )
        assert collection.name == "Test Collection"

    def test_note_creation(self):
        """Test creating a note."""
        note = Note(
            note_id=uuid4(),
            project_id=uuid4(),
            title="Test Note",
            content="# Markdown content",
        )
        assert note.title == "Test Note"

    def test_tag_creation(self):
        """Test creating a tag."""
        tag = Tag(
            tag_id=uuid4(),
            project_id=uuid4(),
            name="important",
        )
        assert tag.name == "important"

    def test_saved_research_creation(self):
        """Test saving research to project."""
        research = SavedResearch(
            saved_research_id=uuid4(),
            project_id=uuid4(),
            research_session_id=uuid4(),
            title="Research Summary",
        )
        assert research.title == "Research Summary"


# ==================== M8 Tests ====================

class TestLocalModels(unittest.IsolatedAsyncioTestCase):
    """Test local model registry."""

    def test_get_local_model(self):
        """Test retrieving a local model."""
        model = LocalModelRegistry.get_model("mistral-7b")
        assert model is not None
        assert model.model_id == "mistral-7b"

    def test_list_llm_models(self):
        """Test listing LLM models."""
        models = LocalModelRegistry.list_llm_models()
        assert len(models) > 0
        assert all(m.type == "llm" for m in models)

    def test_list_embedding_models(self):
        """Test listing embedding models."""
        models = LocalModelRegistry.list_embedding_models()
        assert len(models) > 0
        assert all(m.type == "embedding" for m in models)


class TestHardwareDetection(unittest.IsolatedAsyncioTestCase):
    """Test GPU and hardware detection."""

    async def test_detect_cpu_cores(self):
        """Test CPU core detection."""
        cores = await HardwareDetector.detect_cpu_cores()
        assert cores > 0

    async def test_detect_ram_available(self):
        """Test RAM detection."""
        ram_gb = await HardwareDetector.detect_ram_available_gb()
        assert ram_gb > 0

    def test_gpu_config_creation(self):
        """Test GPU configuration."""
        gpu_config = GPUConfig(
            available=True,
            gpu_type=GPUType.NVIDIA,
            device_name="NVIDIA RTX 4090",
            total_memory_gb=24,
        )
        assert gpu_config.available is True
        assert gpu_config.gpu_type == GPUType.NVIDIA


class TestLocalVectorIndex(unittest.IsolatedAsyncioTestCase):
    """Test local vector indexing."""

    async def test_index_chunks(self):
        """Test indexing chunks locally."""
        index = LocalVectorIndex()
        doc_id = uuid4()
        chunks = [
            DocumentChunk(
                chunk_id="chunk-1",
                document_id=doc_id,
                content="Content 1",
                start_char=0,
                end_char=9,
            ),
            DocumentChunk(
                chunk_id="chunk-2",
                document_id=doc_id,
                content="Content 2",
                start_char=10,
                end_char=19,
            ),
        ]
        result = await index.index_chunks(chunks)
        assert result is True

    async def test_search_local_index(self):
        """Test searching local index."""
        index = LocalVectorIndex()
        doc_id = uuid4()
        chunk = DocumentChunk(
            chunk_id="chunk-1",
            document_id=doc_id,
            content="Test content",
            start_char=0,
            end_char=12,
        )
        await index.index_chunks([chunk])
        results = await index.search("test")
        assert len(results) > 0

    async def test_delete_document(self):
        """Test deleting a document from index."""
        index = LocalVectorIndex()
        doc_id = uuid4()
        chunk = DocumentChunk(
            chunk_id="chunk-1",
            document_id=doc_id,
            content="Test",
            start_char=0,
            end_char=4,
        )
        await index.index_chunks([chunk])
        result = await index.delete_document(doc_id)
        assert result is True


class TestLocalCache(unittest.IsolatedAsyncioTestCase):
    """Test local caching."""

    async def test_set_and_get_cache(self):
        """Test setting and getting cache values."""
        cache = LocalCache(max_size=100)
        await cache.set("key1", "value1")
        value = await cache.get("key1")
        assert value == "value1"

    async def test_cache_miss(self):
        """Test cache miss."""
        cache = LocalCache()
        value = await cache.get("nonexistent")
        assert value is None

    async def test_cache_delete(self):
        """Test deleting from cache."""
        cache = LocalCache()
        await cache.set("key1", "value1")
        await cache.delete("key1")
        value = await cache.get("key1")
        assert value is None

    async def test_cache_clear(self):
        """Test clearing cache."""
        cache = LocalCache()
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.clear()
        size = await cache.size()
        assert size == 0


class TestLocalMemory(unittest.IsolatedAsyncioTestCase):
    """Test local memory provider."""

    async def test_add_memory(self):
        """Test adding memory entries."""
        memory = LocalMemoryProvider()
        session_id = uuid4()
        entry = MemoryEntry(
            entry_id="entry-1",
            session_id=session_id,
            content="Test memory",
            role="user",
            timestamp=datetime.now(timezone.utc),
        )
        entry_id = await memory.add_memory(entry)
        assert entry_id == "entry-1"

    async def test_get_session_memory(self):
        """Test retrieving session memory."""
        memory = LocalMemoryProvider()
        session_id = uuid4()
        entry = MemoryEntry(
            entry_id="entry-1",
            session_id=session_id,
            content="Test",
            role="user",
            timestamp=datetime.now(timezone.utc),
        )
        await memory.add_memory(entry)
        entries = await memory.get_session_memory(session_id)
        assert len(entries) == 1

    async def test_search_memory(self):
        """Test searching memory."""
        memory = LocalMemoryProvider()
        session_id = uuid4()
        entry = MemoryEntry(
            entry_id="entry-1",
            session_id=session_id,
            content="Important memory",
            role="user",
            timestamp=datetime.now(timezone.utc),
        )
        await memory.add_memory(entry)
        results = await memory.search_memory(session_id, "important")
        assert len(results) == 1

    async def test_clear_session_memory(self):
        """Test clearing session memory."""
        memory = LocalMemoryProvider()
        session_id = uuid4()
        entry = MemoryEntry(
            entry_id="entry-1",
            session_id=session_id,
            content="Test",
            role="user",
            timestamp=datetime.now(timezone.utc),
        )
        await memory.add_memory(entry)
        await memory.clear_session_memory(session_id)
        entries = await memory.get_session_memory(session_id)
        assert len(entries) == 0


class TestLocalRuntimeHealth(unittest.IsolatedAsyncioTestCase):
    """Test local runtime health checks."""

    async def test_runtime_health_check(self):
        """Test checking local runtime health."""
        health = await check_local_runtime_health()
        assert health.healthy is not None
        assert health.cpu_cores >= 0
        assert health.ram_available_gb >= 0


class TestIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests across M6-M8."""

    async def test_document_chunking_pipeline(self):
        """Test complete document chunking pipeline."""
        strategy = SemanticChunkingStrategy()
        doc_id = uuid4()
        text = "First section.\n\nSecond section.\n\nThird section."
        chunks = await strategy.chunk(text, str(doc_id))
        assert len(chunks) > 0
        assert all(c.document_id == doc_id for c in chunks)

    async def test_local_index_with_chunks(self):
        """Test indexing chunks with local vector index."""
        index = LocalVectorIndex()
        chunks = [
            DocumentChunk(
                chunk_id=f"chunk-{i}",
                document_id=uuid4(),
                content=f"Content {i}",
                start_char=i * 10,
                end_char=(i + 1) * 10,
            )
            for i in range(3)
        ]
        result = await index.index_chunks(chunks)
        assert result is True

    def test_project_and_research_linking(self):
        """Test linking research to projects."""
        project_id = uuid4()
        research_session_id = uuid4()
        saved_research = SavedResearch(
            saved_research_id=uuid4(),
            project_id=project_id,
            research_session_id=research_session_id,
            title="Important Research",
        )
        assert saved_research.project_id == project_id
        assert saved_research.research_session_id == research_session_id
