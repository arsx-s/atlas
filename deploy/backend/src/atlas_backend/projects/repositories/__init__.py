"""Project repository interfaces."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..models import (
    Collection,
    Folder,
    Note,
    Project,
    SavedResearch,
    Tag,
    ProjectTimeline,
)


class ProjectRepository(ABC):
    """Repository for project persistence."""

    @abstractmethod
    async def create_project(self, project: Project) -> UUID:
        """Create a new project."""
        pass

    @abstractmethod
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Retrieve a project by ID."""
        pass

    @abstractmethod
    async def list_projects(self, user_id: UUID) -> list[Project]:
        """List all projects for a user."""
        pass

    @abstractmethod
    async def update_project(self, project: Project) -> bool:
        """Update project metadata."""
        pass

    @abstractmethod
    async def delete_project(self, project_id: UUID) -> bool:
        """Delete a project and all contents."""
        pass


class CollectionRepository(ABC):
    """Repository for collection persistence."""

    @abstractmethod
    async def create_collection(self, collection: Collection) -> UUID:
        """Create a collection."""
        pass

    @abstractmethod
    async def get_collection(self, collection_id: UUID) -> Optional[Collection]:
        """Retrieve a collection."""
        pass

    @abstractmethod
    async def list_collections(self, project_id: UUID) -> list[Collection]:
        """List collections in a project."""
        pass

    @abstractmethod
    async def update_collection(self, collection: Collection) -> bool:
        """Update collection metadata."""
        pass

    @abstractmethod
    async def delete_collection(self, collection_id: UUID) -> bool:
        """Delete a collection."""
        pass


class NoteRepository(ABC):
    """Repository for note persistence."""

    @abstractmethod
    async def create_note(self, note: Note) -> UUID:
        """Create a note."""
        pass

    @abstractmethod
    async def get_note(self, note_id: UUID) -> Optional[Note]:
        """Retrieve a note."""
        pass

    @abstractmethod
    async def list_notes(self, project_id: UUID) -> list[Note]:
        """List notes in a project."""
        pass

    @abstractmethod
    async def update_note(self, note: Note) -> bool:
        """Update note content."""
        pass

    @abstractmethod
    async def delete_note(self, note_id: UUID) -> bool:
        """Delete a note."""
        pass


class TagRepository(ABC):
    """Repository for tag persistence."""

    @abstractmethod
    async def create_tag(self, tag: Tag) -> UUID:
        """Create a tag."""
        pass

    @abstractmethod
    async def list_tags(self, project_id: UUID) -> list[Tag]:
        """List tags in a project."""
        pass

    @abstractmethod
    async def update_tag(self, tag: Tag) -> bool:
        """Update tag metadata."""
        pass

    @abstractmethod
    async def delete_tag(self, tag_id: UUID) -> bool:
        """Delete a tag."""
        pass


class SavedResearchRepository(ABC):
    """Repository for saved research persistence."""

    @abstractmethod
    async def create_saved_research(self, research: SavedResearch) -> UUID:
        """Save a research session to a project."""
        pass

    @abstractmethod
    async def get_saved_research(self, saved_research_id: UUID) -> Optional[SavedResearch]:
        """Retrieve saved research."""
        pass

    @abstractmethod
    async def list_saved_research(self, project_id: UUID) -> list[SavedResearch]:
        """List all saved research in a project."""
        pass

    @abstractmethod
    async def delete_saved_research(self, saved_research_id: UUID) -> bool:
        """Delete saved research."""
        pass


class TimelineRepository(ABC):
    """Repository for project timeline events."""

    @abstractmethod
    async def record_event(self, event: ProjectTimeline) -> UUID:
        """Record a project event."""
        pass

    @abstractmethod
    async def get_timeline(self, project_id: UUID, limit: int = 50) -> list[ProjectTimeline]:
        """Get project timeline (most recent first)."""
        pass
