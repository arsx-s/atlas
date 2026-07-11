"""PostgreSQL repository implementations."""

from typing import Optional
from uuid import UUID

try:
    from sqlalchemy.orm import Session
except ImportError:  # pragma: no cover - exercised in dependency-constrained environments.
    from typing import Any as Session

from ...projects.models import Project, Collection, Note, Tag, SavedResearch, ProjectTimeline
from ...projects.repositories import (
    ProjectRepository,
    CollectionRepository,
    NoteRepository,
    TagRepository,
    SavedResearchRepository,
    TimelineRepository,
)


class PostgresProjectRepository(ProjectRepository):
    """PostgreSQL project repository."""

    def __init__(self, session: Session):
        self.session = session

    async def create_project(self, project: Project) -> UUID:
        """Create project."""
        raise NotImplementedError("ORM model mapping required")

    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project."""
        raise NotImplementedError("ORM model mapping required")

    async def list_projects(self, user_id: UUID) -> list[Project]:
        """List projects."""
        raise NotImplementedError("ORM model mapping required")

    async def update_project(self, project: Project) -> bool:
        """Update project."""
        raise NotImplementedError("ORM model mapping required")

    async def delete_project(self, project_id: UUID) -> bool:
        """Delete project."""
        raise NotImplementedError("ORM model mapping required")


class PostgresCollectionRepository(CollectionRepository):
    """PostgreSQL collection repository."""

    def __init__(self, session: Session):
        self.session = session

    async def create_collection(self, collection: Collection) -> UUID:
        raise NotImplementedError("ORM model mapping required")

    async def get_collection(self, collection_id: UUID) -> Optional[Collection]:
        raise NotImplementedError("ORM model mapping required")

    async def list_collections(self, project_id: UUID) -> list[Collection]:
        raise NotImplementedError("ORM model mapping required")

    async def update_collection(self, collection: Collection) -> bool:
        raise NotImplementedError("ORM model mapping required")

    async def delete_collection(self, collection_id: UUID) -> bool:
        raise NotImplementedError("ORM model mapping required")


class PostgresNoteRepository(NoteRepository):
    """PostgreSQL note repository."""

    def __init__(self, session: Session):
        self.session = session

    async def create_note(self, note: Note) -> UUID:
        raise NotImplementedError("ORM model mapping required")

    async def get_note(self, note_id: UUID) -> Optional[Note]:
        raise NotImplementedError("ORM model mapping required")

    async def list_notes(self, project_id: UUID) -> list[Note]:
        raise NotImplementedError("ORM model mapping required")

    async def update_note(self, note: Note) -> bool:
        raise NotImplementedError("ORM model mapping required")

    async def delete_note(self, note_id: UUID) -> bool:
        raise NotImplementedError("ORM model mapping required")


class PostgresTagRepository(TagRepository):
    """PostgreSQL tag repository."""

    def __init__(self, session: Session):
        self.session = session

    async def create_tag(self, tag: Tag) -> UUID:
        raise NotImplementedError("ORM model mapping required")

    async def list_tags(self, project_id: UUID) -> list[Tag]:
        raise NotImplementedError("ORM model mapping required")

    async def update_tag(self, tag: Tag) -> bool:
        raise NotImplementedError("ORM model mapping required")

    async def delete_tag(self, tag_id: UUID) -> bool:
        raise NotImplementedError("ORM model mapping required")


class PostgresSavedResearchRepository(SavedResearchRepository):
    """PostgreSQL saved research repository."""

    def __init__(self, session: Session):
        self.session = session

    async def create_saved_research(self, research: SavedResearch) -> UUID:
        raise NotImplementedError("ORM model mapping required")

    async def get_saved_research(self, saved_research_id: UUID) -> Optional[SavedResearch]:
        raise NotImplementedError("ORM model mapping required")

    async def list_saved_research(self, project_id: UUID) -> list[SavedResearch]:
        raise NotImplementedError("ORM model mapping required")

    async def delete_saved_research(self, saved_research_id: UUID) -> bool:
        raise NotImplementedError("ORM model mapping required")


class PostgresTimelineRepository(TimelineRepository):
    """PostgreSQL timeline repository."""

    def __init__(self, session: Session):
        self.session = session

    async def record_event(self, event: ProjectTimeline) -> UUID:
        raise NotImplementedError("ORM model mapping required")

    async def get_timeline(self, project_id: UUID, limit: int = 50) -> list[ProjectTimeline]:
        raise NotImplementedError("ORM model mapping required")
