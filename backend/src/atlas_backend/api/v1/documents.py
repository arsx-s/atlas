"""Document API routes with file upload."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from atlas_backend.core.errors import AtlasErrorCode, AtlasException
from atlas_backend.core.responses import create_success_response
from atlas_backend.documents.chunking.strategies import SemanticChunkingStrategy
from atlas_backend.documents.parsers import DocumentParser
from atlas_backend.documents.parsers.pdf import PDFParser
from atlas_backend.documents.parsers.docx import DOCXParser
from atlas_backend.documents.parsers.markdown import MarkdownParser
from atlas_backend.documents.parsers.text import TextParser
from atlas_backend.persistence import AtlasLocalStore


def _get_upload_dir(settings: Any) -> Path:
    base = Path(settings.documents_storage_path or "atlas_uploads")
    upload_dir = base / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _get_parser(filename: str) -> DocumentParser:
    ext = Path(filename).suffix.lower()
    parsers = {".pdf": PDFParser(), ".docx": DOCXParser(), ".md": MarkdownParser(), ".txt": TextParser()}
    parser = parsers.get(ext)
    if not parser:
        raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, f"Unsupported file format: {ext}")
    return parser


def create_document_router(settings: Any, store: AtlasLocalStore) -> Any:
    from fastapi import APIRouter, UploadFile, File, Form

    router = APIRouter(tags=["documents"])

    @router.post("/projects/{project_id}/documents/ingest")
    async def ingest_document(
        project_id: str,
        file: UploadFile = File(...),
        title: str = Form(""),
    ) -> Any:
        project = store.get_project(project_id)
        if not project:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Project '{project_id}' not found.")

        if not file.filename:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "No file provided.")

        content = await file.read()
        max_size = settings.max_document_size_mb * 1024 * 1024
        if len(content) > max_size:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR,
                                 f"File exceeds {settings.max_document_size_mb}MB limit.")

        upload_dir = _get_upload_dir(settings)
        doc_id = str(uuid4())
        ext = Path(file.filename).suffix.lower()
        safe_name = f"{doc_id}{ext}"
        file_path = upload_dir / safe_name
        file_path.write_bytes(content)

        parser = _get_parser(file.filename)
        parsed = await parser.parse(file_path)
        doc_title = title or parsed.title or file.filename

        chunker = SemanticChunkingStrategy(
            min_chunk_size=settings.chunk_min_size,
            max_chunk_size=settings.chunk_max_size,
        )
        chunks = await chunker.chunk(parsed.text, doc_id)

        doc_record = {
            "document_id": doc_id,
            "project_id": project_id,
            "title": doc_title,
            "file_name": file.filename,
            "file_format": ext.lstrip("."),
            "file_size_bytes": len(content),
            "storage_path": str(file_path),
            "page_count": parsed.pages or 0,
            "author": parsed.author or "",
            "chunk_count": len(chunks),
            "indexed": 1,
        }
        store.create_document(doc_record)

        chunk_records = []
        for c in chunks:
            chunk_records.append({
                "chunk_id": c.chunk_id,
                "document_id": doc_id,
                "content": c.content,
                "page_number": c.page_number,
                "section": c.section or "",
                "start_char": c.start_char,
                "end_char": c.end_char,
                "embedding": None,
            })
        if chunk_records:
            store.save_chunks(chunk_records)

        store.record_timeline_event({
            "event_id": str(uuid4()),
            "project_id": project_id,
            "event_type": "document_uploaded",
            "description": f"Document '{doc_title}' uploaded ({len(content)} bytes, {len(chunks)} chunks)",
        })

        return create_success_response({
            "document_id": doc_id,
            "title": doc_title,
            "chunk_count": len(chunks),
            "page_count": parsed.pages or 0,
        })

    @router.get("/projects/{project_id}/documents")
    async def list_documents(project_id: str) -> Any:
        docs = store.list_documents(project_id)
        return create_success_response({"documents": docs})

    @router.get("/documents/{document_id}")
    async def get_document(document_id: str) -> Any:
        doc = store.get_document(document_id)
        if not doc:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Document '{document_id}' not found.")
        return create_success_response(doc)

    @router.delete("/documents/{document_id}")
    async def delete_document(document_id: str) -> Any:
        doc = store.get_document(document_id)
        if not doc:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Document '{document_id}' not found.")
        path = Path(doc["storage_path"])
        if path.exists():
            path.unlink()
        store.delete_document(document_id)
        return create_success_response({"deleted": True})

    @router.get("/documents/{document_id}/chunks")
    async def list_document_chunks(document_id: str) -> Any:
        doc = store.get_document(document_id)
        if not doc:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Document '{document_id}' not found.")
        with store._connect() as conn:
            rows = conn.execute(
                "SELECT chunk_id, content, page_number, section, start_char, end_char FROM document_chunks WHERE document_id = ? ORDER BY start_char",
                (document_id,)).fetchall()
            chunks = [dict(r) for r in rows]
        return create_success_response({"chunks": chunks})

    @router.post("/documents/{document_id}/query")
    async def query_document(document_id: str, payload: dict[str, Any]) -> Any:
        question = payload.get("question", "").strip()
        if not question:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "Question is required.")
        doc = store.get_document(document_id)
        if not doc:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Document '{document_id}' not found.")
        return create_success_response({
            "answer": f"Document Q&A is available when an AI provider is configured.",
            "document_id": document_id,
            "question": question,
        })

    @router.get("/projects/{project_id}/documents/search")
    async def search_documents(project_id: str, query: str = "", limit: int = 10) -> Any:
        docs = store.list_documents(project_id)
        if query:
            q = query.lower()
            docs = [d for d in docs if q in d["title"].lower()]
        return create_success_response({"documents": docs[:limit]})

    return router
