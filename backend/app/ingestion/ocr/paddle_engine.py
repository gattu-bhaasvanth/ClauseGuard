import io
import logging
from typing import Optional
from app.ingestion.ocr.base import BaseOCREngine, OCRPageResult, OCRBox

logger = logging.getLogger(__name__)


class PaddleOCREngine(BaseOCREngine):
    """
    PaddleOCR implementation for scanned contracts and stamped legal papers.
    Uses lazy loading to avoid importing paddle until first required.
    """

    def __init__(self, lang: str = "en", use_angle_cls: bool = True):
        self.lang = lang
        self.use_angle_cls = use_angle_cls
        self._ocr_instance = None
        self._initialized = False

    @property
    def is_available(self) -> bool:
        try:
            import paddleocr
            return True
        except ImportError:
            return False

    def _get_ocr(self):
        if not self._initialized:
            try:
                from paddleocr import PaddleOCR
                self._ocr_instance = PaddleOCR(
                    use_angle_cls=self.use_angle_cls,
                    lang=self.lang,
                    show_log=False,
                )
                self._initialized = True
            except Exception as e:
                logger.warning(f"PaddleOCR runtime not initialized: {e}")
                self._ocr_instance = None
                self._initialized = True
        return self._ocr_instance

    def extract_text_from_pixmap(
        self, pixmap_bytes: bytes, page_number: int
    ) -> OCRPageResult:
        ocr = self._get_ocr()
        if not ocr:
            # Graceful degraded fallback if paddle is unavailable in current env
            return OCRPageResult(
                page_number=page_number,
                raw_text="[OCR Fallback Notice: PaddleOCR engine not installed on host. Install paddleocr to extract scanned images.]",
                boxes=[],
                average_confidence=0.0,
                engine_name="paddleocr-unavailable",
            )

        try:
            # PaddleOCR accepts numpy array or image file path
            import numpy as np
            from PIL import Image
            image = Image.open(io.BytesIO(pixmap_bytes)).convert("RGB")
            img_np = np.array(image)

            result = ocr.ocr(img_np, cls=self.use_angle_cls)
            lines_text = []
            boxes = []
            confidences = []

            if result and len(result) > 0 and result[0]:
                for line in result[0]:
                    coords = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    text, conf = line[1]
                    lines_text.append(text)
                    confidences.append(float(conf))

                    x_coords = [p[0] for p in coords]
                    y_coords = [p[1] for p in coords]
                    boxes.append(
                        OCRBox(
                            x0=float(min(x_coords)),
                            y0=float(min(y_coords)),
                            x1=float(max(x_coords)),
                            y1=float(max(y_coords)),
                            text=text,
                            confidence=float(conf),
                        )
                    )

            full_text = "\n".join(lines_text)
            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

            return OCRPageResult(
                page_number=page_number,
                raw_text=full_text,
                boxes=boxes,
                average_confidence=avg_conf,
                engine_name="paddleocr",
            )
        except Exception as e:
            logger.error(f"Error during PaddleOCR inference on page {page_number}: {e}")
            return OCRPageResult(
                page_number=page_number,
                raw_text="",
                boxes=[],
                average_confidence=0.0,
                engine_name="paddleocr-error",
            )
