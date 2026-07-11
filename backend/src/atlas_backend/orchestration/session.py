"""Research session lifecycle management."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from atlas_backend.orchestration.models import ResearchSession, ResearchSessionStatus, Task, Evidence


class ResearchSessionManager:
    """Manages research session lifecycle."""

    def __init__(self) -> None:
        self._sessions: dict[str, ResearchSession] = {}

    def create_session(
        self,
        project_id: str,
        user_id: str,
        title: str,
        query: str,
        description: str | None = None,
        model: str = "gpt-4",
    ) -> ResearchSession:
        """Create a new research session."""
        session = ResearchSession(
            project_id=project_id,
            user_id=user_id,
            title=title,
            query=query,
            description=description,
            model_used=model,
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> ResearchSession | None:
        """Retrieve a research session."""
        return self._sessions.get(session_id)

    def update_session_status(self, session_id: str, status: ResearchSessionStatus) -> bool:
        """Update research session status."""
        session = self._sessions.get(session_id)
        if session is None:
            return False

        session.status = status
        if status == ResearchSessionStatus.RUNNING and session.started_at is None:
            session.started_at = datetime.now(timezone.utc)
        elif status in (ResearchSessionStatus.COMPLETED, ResearchSessionStatus.FAILED, ResearchSessionStatus.CANCELLED):
            session.completed_at = datetime.now(timezone.utc)

        return True

    def add_task(self, session_id: str, task: Task) -> bool:
        """Add a task to a research session."""
        session = self._sessions.get(session_id)
        if session is None:
            return False

        session.tasks.append(task)
        session.total_tasks += 1
        return True

    def add_evidence(self, session_id: str, evidence: Evidence) -> bool:
        """Add evidence to a research session."""
        session = self._sessions.get(session_id)
        if session is None:
            return False

        session.evidence.append(evidence)
        return True

    def mark_task_completed(self, session_id: str, task_id: str) -> bool:
        """Mark a task as completed."""
        session = self._sessions.get(session_id)
        if session is None:
            return False

        for task in session.tasks:
            if task.task_id == task_id:
                task.status = "completed"
                session.completed_tasks += 1
                return True

        return False

    def mark_task_failed(self, session_id: str, task_id: str, error_message: str) -> bool:
        """Mark a task as failed."""
        session = self._sessions.get(session_id)
        if session is None:
            return False

        for task in session.tasks:
            if task.task_id == task_id:
                task.status = "failed"
                task.error_message = error_message
                session.failed_tasks += 1
                return True

        return False

    def get_session_progress(self, session_id: str) -> dict[str, Any] | None:
        """Get progress metrics for a session."""
        session = self._sessions.get(session_id)
        if session is None:
            return None

        return {
            "total_tasks": session.total_tasks,
            "completed_tasks": session.completed_tasks,
            "failed_tasks": session.failed_tasks,
            "pending_tasks": session.total_tasks - session.completed_tasks - session.failed_tasks,
            "progress_percent": (session.completed_tasks / session.total_tasks * 100) if session.total_tasks > 0 else 0,
        }
