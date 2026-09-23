from app.ingestion.ocr.base import BaseOCREngine, OCRPageResult, OCRBox


class MockOCREngine(BaseOCREngine):
    """
    Simulated OCR engine used in automated test suites and environments where
    heavy deep learning OCR models are not installed.
    """

    def __init__(self, simulated_text: str = None):
        self.simulated_text = simulated_text

    @property
    def is_available(self) -> bool:
        return True

    def extract_text_from_pixmap(
        self, pixmap_bytes: bytes, page_number: int
    ) -> OCRPageResult:
        text = self.simulated_text or (
            f"[OCR Scanned Page {page_number}]\n"
            "ARTICLE I: DEFINITIONS & SCHEDULE OF PROPERTY\n"
            "Carpet area confirmed as 1,380 sq.ft subject to statutory adjustments."
        )
        boxes = [
            OCRBox(x0=50.0, y0=100.0, x1=500.0, y1=130.0, text=text[:50], confidence=0.94),
            OCRBox(x0=50.0, y0=140.0, x1=500.0, y1=180.0, text=text[50:], confidence=0.91),
        ]
        return OCRPageResult(
            page_number=page_number,
            raw_text=text,
            boxes=boxes,
            average_confidence=0.925,
            engine_name="mock-ocr",
        )
