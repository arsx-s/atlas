"""SQLite repository implementations for local mode."""

from typing import Optional
from uuid import UUID

from ...projects.models import Project, Collection, Note, Tag, SavedResearch, ProjectTimeline
from ...projects.repositories import (
    ProjectRepository,
    CollectionRepository,
    NoteRepository,
    TagRepository,
    SavedResearchRepository,
    TimelineRepository,
)


class SqliteProjectRepository(ProjectRepository):
    """SQLite project repository for local mode."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_project(self, project: Project) -> UUID:
        raise NotImplementedError("SQLite schema mapping required")

    async def get_project(self, project_id: UUID) -> Optional[Project]:
        raise NotImplementedError("SQLite schema mapping required")

    async def list_projects(self, user_id: UUID) -> list[Project]:
        raise NotImplementedError("SQLite schema mapping required")

    async def update_project(self, project: Project) -> bool:
        raise NotImplementedError("SQLite schema mapping required")

    async def delete_project(self, project_id: UUID) -> bool:
        raise NotImplementedError("SQLite schema mapping required")


class SqliteCollectionRepository(CollectionRepository):
    """SQLite collection repository."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_collection(self, collection: Collection) -> UUID:
        raise NotImplementedError("SQLite schema mapping required")

    async def get_collection(self, collection_id: UUID) -> Optional[Collection]:
        raise NotImplementedError("SQLite schema mapping required")

    async def list_collections(self, project_id: UUID) -> list[Collection]:
        raise NotImplementedError("SQLite schema mapping required")

    async def update_collection(self, collection: Collection) -> bool:
        raise NotImplementedError("SQLite schema mapping required")

    async def delete_collection(self, collection_id: UUID) -> bool:
        raise NotImplementedError("SQLite schema mapping required")


class SqliteNoteRepository(NoteRepository):
    """SQLite note repository."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_note(self, note: Note) -> UUID:
        raise NotImplementedError("SQLite schema mapping required")

    async def get_note(self, note_id: UUID) -> Optional[Note]:
        raise NotImplementedError("SQLite schema mapping required")

    async def list_notes(self, project_id: UUID) -> list[Note]:
        raise NotImplementedError("SQLite schema mapping required")

    async def update_note(self, note: Note) -> bool:
        raise NotImplementedError("SQLite schema mapping required")

    async def delete_note(self, note_id: UUID) -> bool:
        raise NotImplementedError("SQLite schema mapping required")


class SqliteTagRepository(TagRepository):
    """SQLite tag repository."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_tag(self, tag: Tag) -> UUID:
        raise NotImplementedError("SQLite schema mapping required")

    async def list_tags(self, project_id: UUID) -> list[Tag]:
        raise NotImplementedError("SQLite schema mapping required")

    async def update_tag(self, tag: Tag) -> bool:
        raise NotImplementedError("SQLite schema mapping required")

    async def delete_tag(self, tag_id: UUID) -> bool:
        raise NotImplementedError("SQLite schema mapping required")


class SqliteSavedResearchRepository(SavedResearchRepository):
    """SQLite saved research repository."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_saved_research(self, research: SavedResearch) -> UUID:
        raise NotImplementedError("SQLite schema mapping required")

    async def get_saved_research(self, saved_research_id: UUID) -> Optional[SavedResearch]:
        raise NotImplementedError("SQLite schema mapping required")

    async def list_saved_research(self, project_id: UUID) -> list[SavedResearch]:
        raise NotImplementedError("SQLite schema mapping required")

    async def delete_saved_research(self, saved_research_id: UUID) -> bool:
        raise NotImplementedError("SQLite schema mapping required")


class SqliteTimelineRepository(TimelineRepository):
    """SQLite timeline repository."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def record_event(self, event: ProjectTimeline) -> UUID:
        raise NotImplementedError("SQLite schema mapping required")

    async def get_timeline(self, project_id: UUID, limit: int = 50) -> list[ProjectTimeline]:
        raise NotImplementedError("SQLite schema mapping required")
