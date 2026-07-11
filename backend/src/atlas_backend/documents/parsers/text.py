"""Plain text document parser."""

from pathlib import Path

from .base import DocumentParser, ParsedContent


class TextParser(DocumentParser):
    """Parse plain text documents."""

    async def parse(self, file_path: Path) -> ParsedContent:
        """Parse text file."""
        content = file_path.read_text(encoding="utf-8")
        return ParsedContent(text=content, metadata={"format": "text"})

    def supported_extension(self) -> str:
        return ".txt"
