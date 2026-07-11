"""Project manager orchestrating project operations."""

from typing import Optional
from uuid import UUID

from .models import Project, Collection, Note, SavedResearch, Tag
from .repositories import (
    ProjectRepository,
    CollectionRepository,
    NoteRepository,
    SavedResearchRepository,
    TagRepository,
    TimelineRepository,
)


class ProjectManager:
    """Manages project lifecycle and operations."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        collection_repo: CollectionRepository,
        note_repo: NoteRepository,
        saved_research_repo: SavedResearchRepository,
        tag_repo: TagRepository,
        timeline_repo: TimelineRepository,
    ):
        self.project_repo = project_repo
        self.collection_repo = collection_repo
        self.note_repo = note_repo
        self.saved_research_repo = saved_research_repo
        self.tag_repo = tag_repo
        self.timeline_repo = timeline_repo

    async def create_project(self, name: str, user_id: UUID, description: Optional[str] = None) -> Project:
        """Create a new project."""
        project = Project(
            project_id=UUID('00000000-0000-0000-0000-000000000000'),  # Will be assigned
            user_id=user_id,
            name=name,
            description=description,
        )
        project_id = await self.project_repo.create_project(project)
        project.project_id = project_id
        return project

    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project details."""
        return await self.project_repo.get_project(project_id)

    async def list_user_projects(self, user_id: UUID) -> list[Project]:
        """List all projects for a user."""
        return await self.project_repo.list_projects(user_id)

    async def save_research_to_project(
        self,
        project_id: UUID,
        research_session_id: UUID,
        title: str,
        summary: Optional[str] = None,
    ) -> SavedResearch:
        """Link a research session to a project."""
        research = SavedResearch(
            saved_research_id=UUID('00000000-0000-0000-0000-000000000000'),
            project_id=project_id,
            research_session_id=research_session_id,
            title=title,
            summary=summary,
        )
        research_id = await self.saved_research_repo.create_saved_research(research)
        research.saved_research_id = research_id
        return research

    async def create_note(
        self,
        project_id: UUID,
        title: str,
        content: str,
    ) -> Note:
        """Create a note in a project."""
        note = Note(
            note_id=UUID('00000000-0000-0000-0000-000000000000'),
            project_id=project_id,
            title=title,
            content=content,
        )
        note_id = await self.note_repo.create_note(note)
        note.note_id = note_id
        return note

    async def add_tag(self, project_id: UUID, tag_name: str) -> Tag:
        """Add a tag to a project."""
        tag = Tag(
            tag_id=UUID('00000000-0000-0000-0000-000000000000'),
            project_id=project_id,
            name=tag_name,
        )
        tag_id = await self.tag_repo.create_tag(tag)
        tag.tag_id = tag_id
        return tag

    async def get_project_timeline(self, project_id: UUID, limit: int = 50) -> list:
        """Get project activity timeline."""
        return await self.timeline_repo.get_timeline(project_id, limit)
