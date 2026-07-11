"""Project data models."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Project(BaseModel):
    """A project for organizing research and documents."""
    project_id: UUID = Field(..., description="Project ID")
    user_id: UUID = Field(..., description="Project owner")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    is_public: bool = Field(False, description="Public visibility")
    is_archived: bool = Field(False, description="Archived status")
    tags: list[str] = Field(default_factory=list, description="Project tags")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    document_count: int = Field(0, description="Count of documents in project")
    research_session_count: int = Field(0, description="Count of research sessions")


class Collection(BaseModel):
    """A collection of related documents within a project."""
    collection_id: UUID = Field(..., description="Collection ID")
    project_id: UUID = Field(..., description="Parent project")
    name: str = Field(..., description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    icon: Optional[str] = Field(None, description="Collection icon")
    color: Optional[str] = Field(None, description="Collection color (hex)")
    document_count: int = Field(0, description="Number of documents")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Folder(BaseModel):
    """A folder for hierarchical organization."""
    folder_id: UUID = Field(..., description="Folder ID")
    collection_id: UUID = Field(..., description="Parent collection")
    name: str = Field(..., description="Folder name")
    parent_folder_id: Optional[UUID] = Field(None, description="Parent folder ID (null for root)")
    document_count: int = Field(0, description="Total documents in folder and subfolders")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Tag(BaseModel):
    """A tag for categorizing documents and research."""
    tag_id: UUID = Field(..., description="Tag ID")
    project_id: UUID = Field(..., description="Project scope")
    name: str = Field(..., description="Tag name")
    color: Optional[str] = Field(None, description="Tag color (hex)")
    usage_count: int = Field(0, description="How many items tagged")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Note(BaseModel):
    """A note within a project."""
    note_id: UUID = Field(..., description="Note ID")
    project_id: UUID = Field(..., description="Project")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note markdown content")
    tags: list[UUID] = Field(default_factory=list, description="Applied tags")
    related_documents: list[UUID] = Field(default_factory=list, description="Linked documents")
    is_pinned: bool = Field(False, description="Pinned status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SavedResearch(BaseModel):
    """A saved research session within a project."""
    saved_research_id: UUID = Field(..., description="Saved research ID")
    project_id: UUID = Field(..., description="Project")
    research_session_id: UUID = Field(..., description="Research session reference")
    title: str = Field(..., description="Research title")
    summary: Optional[str] = Field(None, description="Research summary")
    keywords: list[str] = Field(default_factory=list, description="Keywords")
    tags: list[UUID] = Field(default_factory=list, description="Applied tags")
    is_starred: bool = Field(False, description="Star status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectTimeline(BaseModel):
    """Timeline of project events."""
    event_id: UUID = Field(..., description="Event ID")
    project_id: UUID = Field(..., description="Project")
    event_type: str = Field(..., description="document_added, research_created, note_updated, etc.")
    description: str = Field(..., description="Event description")
    related_entity_id: Optional[UUID] = Field(None, description="Related document/research/note ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
