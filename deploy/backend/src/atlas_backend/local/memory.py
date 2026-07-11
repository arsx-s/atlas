"""Local memory provider for conversation history and context."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class MemoryEntry(BaseModel):
    """A memory entry from conversation."""
    entry_id: str
    session_id: UUID
    content: str
    role: str  # user, assistant, system
    timestamp: datetime
    tags: list[str] = []


class LocalMemoryProvider:
    """Stores conversation memory locally."""

    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.memory = {}  # session_id -> [entries]

    async def add_memory(self, entry: MemoryEntry) -> str:
        """Add memory entry to session."""
        session_id = entry.session_id
        if session_id not in self.memory:
            self.memory[session_id] = []

        self.memory[session_id].append(entry)

        if len(self.memory[session_id]) > self.max_entries:
            self.memory[session_id].pop(0)

        return entry.entry_id

    async def get_session_memory(self, session_id: UUID, limit: int = 50) -> list[MemoryEntry]:
        """Get conversation history for session."""
        if session_id not in self.memory:
            return []

        entries = self.memory[session_id]
        return entries[-limit:]

    async def search_memory(self, session_id: UUID, query: str) -> list[MemoryEntry]:
        """Search memory entries."""
        if session_id not in self.memory:
            return []

        query_lower = query.lower()
        return [e for e in self.memory[session_id] if query_lower in e.content.lower()]

    async def clear_session_memory(self, session_id: UUID) -> None:
        """Clear all memory for a session."""
        self.memory.pop(session_id, None)
