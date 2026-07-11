"""Markdown document parser."""

from pathlib import Path

from .base import DocumentParser, ParsedContent


class MarkdownParser(DocumentParser):
    """Parse Markdown documents."""

    async def parse(self, file_path: Path) -> ParsedContent:
        """Parse Markdown file."""
        content = file_path.read_text(encoding="utf-8")
        title = self._extract_title(content)
        return ParsedContent(text=content, title=title, metadata={"format": "markdown"})

    def supported_extension(self) -> str:
        return ".md"

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown (first H1 heading)."""
        for line in content.split("\n"):
            if line.startswith("# "):
                return line[2:].strip()
        return None
