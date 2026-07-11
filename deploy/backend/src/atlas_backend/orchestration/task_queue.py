"""Task queue and distribution."""

from __future__ import annotations

from collections import deque
from typing import Any

from atlas_backend.orchestration.models import Task, TaskStatus


class TaskQueue:
    """Manages task queue and distribution."""

    def __init__(self) -> None:
        self._queues: dict[str, deque[Task]] = {}
        self._assigned_tasks: dict[str, Task] = {}

    def enqueue_task(self, session_id: str, task: Task) -> None:
        """Add a task to the queue."""
        if session_id not in self._queues:
            self._queues[session_id] = deque()
        self._queues[session_id].append(task)

    def dequeue_task(self, session_id: str) -> Task | None:
        """Get next task from queue."""
        if session_id not in self._queues or len(self._queues[session_id]) == 0:
            return None
        return self._queues[session_id].popleft()

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent."""
        for queue in self._queues.values():
            for task in queue:
                if task.task_id == task_id:
                    task.status = TaskStatus.ASSIGNED
                    task.agent_id = agent_id
                    self._assigned_tasks[task_id] = task
                    return True
        return False

    def get_assigned_task(self, task_id: str) -> Task | None:
        """Get an assigned task."""
        return self._assigned_tasks.get(task_id)

    def get_pending_tasks(self, session_id: str) -> list[Task]:
        """Get all pending tasks for a session."""
        if session_id not in self._queues:
            return []
        return list(self._queues[session_id])

    def get_queue_length(self, session_id: str) -> int:
        """Get the number of pending tasks in a session."""
        if session_id not in self._queues:
            return 0
        return len(self._queues[session_id])
