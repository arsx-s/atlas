"""PDF document parser using pdfplumber."""

from pathlib import Path

from .base import DocumentParser, ParsedContent


class PDFParser(DocumentParser):
    """Parse PDF documents using pdfplumber."""

    async def parse(self, file_path: Path) -> ParsedContent:
        import pdfplumber
        text_parts = []
        metadata = {}
        page_count = 0
        with pdfplumber.open(str(file_path)) as pdf:
            page_count = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                text_parts.append(text)
            if pdf.metadata:
                metadata = {
                    "author": pdf.metadata.get("Author", ""),
                    "title": pdf.metadata.get("Title", ""),
                    "subject": pdf.metadata.get("Subject", ""),
                    "pages": page_count,
                }
        full_text = "\n\n".join(text_parts)
        title = metadata.get("title") or file_path.stem
        return ParsedContent(
            text=full_text,
            title=title,
            author=metadata.get("author"),
            pages=page_count,
            metadata=metadata,
        )

    def supported_extension(self) -> str:
        return ".pdf"
