"""Tesseract OCR provider stub."""

from pathlib import Path

from . import OCRProvider, OCRResult


class TesseractOCRProvider(OCRProvider):
    """Tesseract OCR provider. Requires system Tesseract installation."""

    async def ocr_image(self, image_data: bytes, language: str = "en") -> OCRResult:
        """Extract text from image using Tesseract."""
        raise NotImplementedError(
            "Tesseract OCR requires system installation and pytesseract. "
            "Install: pip install pytesseract"
        )

    async def ocr_file(self, file_path: Path, language: str = "en") -> OCRResult:
        """Extract text from file using Tesseract."""
        raise NotImplementedError

    async def health_check(self) -> bool:
        """Check Tesseract availability."""
        raise NotImplementedError


class CloudOCRProvider(OCRProvider):
    """Cloud OCR provider (Google Vision, Azure, AWS). Stubs for future integration."""

    async def ocr_image(self, image_data: bytes, language: str = "en") -> OCRResult:
        """Extract text from image using cloud OCR."""
        raise NotImplementedError("Cloud OCR requires API credentials and SDK")

    async def ocr_file(self, file_path: Path, language: str = "en") -> OCRResult:
        """Extract text from file using cloud OCR."""
        raise NotImplementedError

    async def health_check(self) -> bool:
        """Check cloud OCR service availability."""
        raise NotImplementedError
