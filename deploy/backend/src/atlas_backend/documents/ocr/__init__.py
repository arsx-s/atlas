"""OCR provider abstraction."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, confloat


class OCRResult(BaseModel):
    """OCR result from provider."""
    text: str
    confidence: confloat(ge=0.0, le=1.0)
    languages_detected: list[str] = Field(default_factory=list)
    raw_output: dict = Field(default_factory=dict)


class OCRProvider(ABC):
    """Abstract OCR provider interface."""

    @abstractmethod
    async def ocr_image(self, image_data: bytes, language: str = "en") -> OCRResult:
        """Extract text from image using OCR."""
        pass

    @abstractmethod
    async def ocr_file(self, file_path: Path, language: str = "en") -> OCRResult:
        """Extract text from file with OCR."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check OCR provider availability."""
        pass
