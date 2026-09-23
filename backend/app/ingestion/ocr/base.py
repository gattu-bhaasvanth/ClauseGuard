from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class OCRBox:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    confidence: float


@dataclass
class OCRPageResult:
    page_number: int
    raw_text: str
    boxes: List[OCRBox] = field(default_factory=list)
    average_confidence: float = 0.0
    engine_name: str = "base"


class BaseOCREngine(ABC):
    """Abstract interface for pluggable OCR engines (PaddleOCR, Tesseract, etc.)."""

    @abstractmethod
    def extract_text_from_pixmap(
        self, pixmap_bytes: bytes, page_number: int
    ) -> OCRPageResult:
        """Process image bytes and return extracted text with bounding boxes."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the OCR engine dependencies and weights are installed."""
        pass
