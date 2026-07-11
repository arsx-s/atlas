"""DOCX document parser using python-docx."""

from pathlib import Path

from .base import DocumentParser, ParsedContent


class DOCXParser(DocumentParser):
    """Parse DOCX documents using python-docx."""

    async def parse(self, file_path: Path) -> ParsedContent:
        from docx import Document as DocxDocument
        doc = DocxDocument(str(file_path))
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        full_text = "\n\n".join(paragraphs)
        title = ""
        author = ""
        if doc.core_properties:
            title = doc.core_properties.title or file_path.stem
            author = doc.core_properties.author or ""
        return ParsedContent(
            text=full_text,
            title=title,
            author=author,
            pages=len(doc.sections),
            metadata={"format": "docx", "author": author, "title": title},
        )

    def supported_extension(self) -> str:
        return ".docx"
