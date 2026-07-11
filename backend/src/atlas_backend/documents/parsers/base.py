"""Base document parser interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class ParsedContent(BaseModel):
    """Parsed document content."""
    text: str
    title: Optional[str] = None
    author: Optional[str] = None
    pages: Optional[int] = None
    metadata: dict = {}
    images: list[bytes] = []


class DocumentParser(ABC):
    """Abstract document parser interface."""

    @abstractmethod
    async def parse(self, file_path: Path) -> ParsedContent:
        """Parse document file and extract content."""
        pass

    @abstractmethod
    def supported_extension(self) -> str:
        """Get file extension this parser supports."""
        pass

    async def validate_file(self, file_path: Path) -> bool:
        """Validate file is readable and not corrupted."""
        if not file_path.exists():
            return False
        if file_path.stat().st_size == 0:
            return False
        return True
