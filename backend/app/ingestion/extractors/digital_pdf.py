from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
from app.ingestion.extractors.density_checker import PageDensityChecker, PageScanAssessment
from app.ingestion.ocr.base import BaseOCREngine, OCRPageResult
from app.ingestion.normalizer import DocumentNormalizer


@dataclass
class ExtractedPageData:
    page_number: int
    raw_text: str
    normalized_text: str
    is_scanned: bool
    ocr_applied: bool
    layout_boxes: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    width: float = 0.0
    height: float = 0.0


@dataclass
class PDFExtractionResult:
    total_pages: int
    scanned_pages_count: int
    pages: List[ExtractedPageData]
    ocr_engine_used: Optional[str] = None


class DigitalPDFExtractor:
    """
    High-performance PDF extractor utilizing PyMuPDF (fitz) with automated
    density inspection and OCR fallback for scanned pages.
    """

    def __init__(
        self,
        ocr_engine: Optional[BaseOCREngine] = None,
        density_checker: Optional[PageDensityChecker] = None,
        normalizer: Optional[DocumentNormalizer] = None,
    ):
        self.ocr_engine = ocr_engine
        self.density_checker = density_checker or PageDensityChecker()
        self.normalizer = normalizer or DocumentNormalizer()

    def extract_document(self, file_path: Path) -> PDFExtractionResult:
        doc = fitz.open(str(file_path))
        extracted_pages: List[ExtractedPageData] = []
        scanned_count = 0
        engine_name_used = None

        try:
            for page in doc:
                page_num = page.number + 1
                assessment = self.density_checker.assess_page(page)
                page_rect = page.rect
                width = float(page_rect.width)
                height = float(page_rect.height)

                if assessment.is_scanned and self.ocr_engine:
                    # Page is scanned: render high-res pixmap for OCR fallback
                    scanned_count += 1
                    # Render at 2x resolution (144 dpi) for OCR clarity
                    pix = page.get_pixmap(dpi=150)
                    pix_bytes = pix.tobytes("png")

                    ocr_res: OCRPageResult = self.ocr_engine.extract_text_from_pixmap(
                        pix_bytes, page_num
                    )
                    engine_name_used = ocr_res.engine_name
                    boxes = [
                        {
                            "x0": b.x0,
                            "y0": b.y0,
                            "x1": b.x1,
                            "y1": b.y1,
                            "text": b.text,
                            "confidence": b.confidence,
                        }
                        for b in ocr_res.boxes
                    ]
                    norm_text = self.normalizer.normalize_text(ocr_res.raw_text)

                    extracted_pages.append(
                        ExtractedPageData(
                            page_number=page_num,
                            raw_text=ocr_res.raw_text,
                            normalized_text=norm_text,
                            is_scanned=True,
                            ocr_applied=True,
                            layout_boxes=boxes,
                            confidence=ocr_res.average_confidence,
                            width=width,
                            height=height,
                        )
                    )
                else:
                    # Digital PDF: extract text blocks directly with geometric bounding boxes
                    blocks = page.get_text("blocks")
                    boxes = []
                    raw_lines = []

                    for b in blocks:
                        # b is (x0, y0, x1, y1, text, block_no, block_type)
                        b_text = b[4].strip()
                        if b_text:
                            raw_lines.append(b_text)
                            boxes.append(
                                {
                                    "x0": float(b[0]),
                                    "y0": float(b[1]),
                                    "x1": float(b[2]),
                                    "y1": float(b[3]),
                                    "text": b_text,
                                    "confidence": 1.0,
                                }
                            )

                    raw_text = "\n\n".join(raw_lines)
                    norm_text = self.normalizer.normalize_text(raw_text)

                    extracted_pages.append(
                        ExtractedPageData(
                            page_number=page_num,
                            raw_text=raw_text,
                            normalized_text=norm_text,
                            is_scanned=assessment.is_scanned,
                            ocr_applied=False,
                            layout_boxes=boxes,
                            confidence=1.0,
                            width=width,
                            height=height,
                        )
                    )

            return PDFExtractionResult(
                total_pages=len(doc),
                scanned_pages_count=scanned_count,
                pages=extracted_pages,
                ocr_engine_used=engine_name_used,
            )
        finally:
            doc.close()
