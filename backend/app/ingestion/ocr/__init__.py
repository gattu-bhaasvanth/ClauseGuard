from app.ingestion.ocr.base import BaseOCREngine, OCRPageResult, OCRBox
from app.ingestion.ocr.paddle_engine import PaddleOCREngine
from app.ingestion.ocr.mock_engine import MockOCREngine


def get_ocr_engine(engine_name: str = "paddleocr") -> BaseOCREngine:
    """Factory retrieving the configured OCR engine."""
    name = (engine_name or "").lower()
    if name == "mock":
        return MockOCREngine()
    elif name == "paddleocr":
        engine = PaddleOCREngine()
        if engine.is_available:
            return engine
        return MockOCREngine()
    return MockOCREngine()


__all__ = ["BaseOCREngine", "OCRPageResult", "OCRBox", "PaddleOCREngine", "MockOCREngine", "get_ocr_engine"]
