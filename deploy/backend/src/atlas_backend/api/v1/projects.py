"""Project API routes."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from atlas_backend.core.errors import AtlasErrorCode, AtlasException
from atlas_backend.core.responses import create_success_response
from atlas_backend.persistence import AtlasLocalStore


def create_project_router(settings: Any, store: AtlasLocalStore) -> Any:
    from fastapi import APIRouter

    router = APIRouter(tags=["projects"])

    @router.post("/projects")
    async def create_project(payload: dict[str, Any]) -> Any:
        name = payload.get("name", "").strip()
        if not name:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "Project name is required.")
        user_id = payload.get("user_id", "local-user")
        project = {
            "project_id": str(uuid4()),
            "user_id": user_id,
            "name": name,
            "description": payload.get("description", ""),
            "tags": payload.get("tags", []),
        }
        store.create_project(project)
        store.record_timeline_event({
            "event_id": str(uuid4()),
            "project_id": project["project_id"],
            "event_type": "project_created",
            "description": f"Project '{name}' created",
        })
        return create_success_response(project)

    @router.get("/projects/{project_id}")
    async def get_project(project_id: str) -> Any:
        project = store.get_project(project_id)
        if not project:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Project '{project_id}' not found.")
        return create_success_response(project)

    @router.get("/projects")
    async def list_projects(user_id: str = "local-user") -> Any:
        projects = store.list_projects(user_id)
        return create_success_response({"projects": projects})

    @router.put("/projects/{project_id}")
    async def update_project(project_id: str, payload: dict[str, Any]) -> Any:
        existing = store.get_project(project_id)
        if not existing:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Project '{project_id}' not found.")
        store.update_project(project_id, payload)
        updated = store.get_project(project_id)
        return create_success_response(updated)

    @router.delete("/projects/{project_id}")
    async def delete_project(project_id: str) -> Any:
        if not store.delete_project(project_id):
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Project '{project_id}' not found.")
        return create_success_response({"deleted": True})

    @router.post("/projects/{project_id}/notes")
    async def create_note(project_id: str, payload: dict[str, Any]) -> Any:
        project = store.get_project(project_id)
        if not project:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Project '{project_id}' not found.")
        note = {
            "note_id": str(uuid4()),
            "project_id": project_id,
            "title": payload.get("title", "Untitled"),
            "content": payload.get("content", ""),
            "tags": payload.get("tags", []),
            "is_pinned": payload.get("is_pinned", False),
        }
        store.create_note(note)
        return create_success_response(note)

    @router.get("/projects/{project_id}/notes")
    async def list_notes(project_id: str) -> Any:
        notes = store.list_notes(project_id)
        return create_success_response({"notes": notes})

    @router.post("/projects/{project_id}/research")
    async def save_research(project_id: str, payload: dict[str, Any]) -> Any:
        project = store.get_project(project_id)
        if not project:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Project '{project_id}' not found.")
        saved = {
            "saved_research_id": str(uuid4()),
            "project_id": project_id,
            "research_session_id": payload.get("research_session_id", ""),
            "title": payload.get("title", "Untitled Research"),
            "summary": payload.get("summary", ""),
        }
        store.save_research(saved)
        return create_success_response(saved)

    @router.get("/projects/{project_id}/research")
    async def list_saved_research(project_id: str) -> Any:
        items = store.list_saved_research(project_id)
        return create_success_response({"saved_research": items})

    @router.get("/projects/{project_id}/timeline")
    async def get_timeline(project_id: str, limit: int = 50) -> Any:
        events = store.get_timeline(project_id, limit)
        return create_success_response({"events": events})

    @router.get("/projects/{project_id}/search")
    async def search_project(project_id: str, query: str = "") -> Any:
        project = store.get_project(project_id)
        if not project:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Project '{project_id}' not found.")
        notes = store.list_notes(project_id)
        docs = store.list_documents(project_id)
        results = []
        q = query.lower()
        for n in notes:
            if q in n["title"].lower() or q in n["content"].lower():
                results.append({"type": "note", "id": n["note_id"], "title": n["title"]})
        for d in docs:
            if q in d["title"].lower():
                results.append({"type": "document", "id": d["document_id"], "title": d["title"]})
        return create_success_response({"results": results})

    return router
