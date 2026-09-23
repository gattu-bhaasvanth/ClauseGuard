from dataclasses import dataclass
from typing import Optional
import fitz  # PyMuPDF


@dataclass
class PageScanAssessment:
    page_number: int
    is_scanned: bool
    char_count: int
    word_count: int
    image_count: int
    image_coverage_ratio: float
    confidence: float
    reason: str


class PageDensityChecker:
    """
    Heuristic analyzer that evaluates whether a PDF page contains native digital text
    or is a scanned / photographed image requiring OCR fallback.
    """

    def __init__(self, min_char_threshold: int = 60, min_word_threshold: int = 10):
        self.min_char_threshold = min_char_threshold
        self.min_word_threshold = min_word_threshold

    def assess_page(self, page: fitz.Page) -> PageScanAssessment:
        page_num = page.number + 1
        text = page.get_text("text").strip()
        words = text.split()
        char_count = len(text)
        word_count = len(words)

        images = page.get_images()
        image_count = len(images)

        # Calculate image area coverage ratio
        page_rect = page.rect
        page_area = max(1.0, page_rect.width * page_rect.height)
        total_image_area = 0.0

        for img_info in images:
            xref = img_info[0]
            try:
                rects = page.get_image_rects(xref)
                for r in rects:
                    total_image_area += (r.width * r.height)
            except Exception:
                pass

        coverage_ratio = min(1.0, total_image_area / page_area)

        # Decision heuristics
        if char_count < self.min_char_threshold:
            if image_count > 0 or coverage_ratio > 0.3:
                return PageScanAssessment(
                    page_number=page_num,
                    is_scanned=True,
                    char_count=char_count,
                    word_count=word_count,
                    image_count=image_count,
                    image_coverage_ratio=coverage_ratio,
                    confidence=0.95,
                    reason=f"Low text density ({char_count} chars) with {image_count} image(s) covering {coverage_ratio*100:.1f}% area.",
                )
            else:
                return PageScanAssessment(
                    page_number=page_num,
                    is_scanned=False,
                    char_count=char_count,
                    word_count=word_count,
                    image_count=image_count,
                    image_coverage_ratio=coverage_ratio,
                    confidence=0.7,
                    reason="Sparse page (cover/blank) without prominent image layer.",
                )

        # Page has sufficient digital text
        return PageScanAssessment(
            page_number=page_num,
            is_scanned=False,
            char_count=char_count,
            word_count=word_count,
            image_count=image_count,
            image_coverage_ratio=coverage_ratio,
            confidence=0.98,
            reason=f"High native text density ({char_count} characters, {word_count} words).",
        )
