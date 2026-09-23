import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document, DocumentPage
from app.ingestion.storage import storage_manager, StorageManager
from app.ingestion.extractors.digital_pdf import (
    DigitalPDFExtractor,
    PDFExtractionResult,
    ExtractedPageData,
)
from app.ingestion.ocr import get_ocr_engine, BaseOCREngine
from app.ingestion.normalizer import DocumentNormalizer
from app.config import settings


@dataclass
class IngestionResult:
    document_id: str
    bundle_id: str
    file_name: str
    file_size: str
    page_count: int
    scanned_pages_count: int
    ocr_status: str
    ocr_engine_used: Optional[str]
    pages: List[ExtractedPageData]


class IngestionPipeline:
    """
    End-to-end ingestion pipeline:
    1. Validates and persists uploaded PDF into data/uploads/
    2. Inspects pages for scan vs. digital density
    3. Extracts text and coordinate bounding boxes with automated OCR fallback
    4. Normalizes extracted text
    5. Persists Document and DocumentPage database entities
    """

    def __init__(
        self,
        ocr_engine: Optional[BaseOCREngine] = None,
        storage: Optional[StorageManager] = None,
        normalizer: Optional[DocumentNormalizer] = None,
    ):
        self.storage = storage or storage_manager
        self.normalizer = normalizer or DocumentNormalizer()
        self.ocr_engine = ocr_engine or get_ocr_engine(settings.OCR_ENGINE if hasattr(settings, "OCR_ENGINE") else "paddleocr")
        self.extractor = DigitalPDFExtractor(
            ocr_engine=self.ocr_engine,
            normalizer=self.normalizer,
        )

    async def ingest_document(
        self,
        session: AsyncSession,
        bundle_id: str,
        file_bytes: bytes,
        original_filename: str,
        document_type: str = "OTHER",
        document_id: Optional[str] = None,
    ) -> IngestionResult:
        # 1. Save file to storage
        saved_path, file_hash, file_size_str = self.storage.save_upload_stream(
            file_bytes, original_filename
        )

        # 2. Run extraction
        extraction_res: PDFExtractionResult = self.extractor.extract_document(saved_path)

        # Determine OCR status
        if extraction_res.scanned_pages_count > 0:
            ocr_status = "OCR_FALLBACK_USED"
        elif extraction_res.total_pages > 0:
            ocr_status = "NOT_REQUIRED"
        else:
            ocr_status = "EMPTY"

        # 3. Create or update Document record in database
        doc_id = document_id or f"doc-{uuid.uuid4().hex[:8]}"
        result = await session.execute(select(Document).filter_by(id=doc_id))
        doc = result.scalar_one_or_none()

        if not doc:
            doc = Document(
                id=doc_id,
                bundle_id=bundle_id,
                file_name=original_filename,
                document_type=document_type,
                file_path=str(saved_path),
                file_size=file_size_str,
                page_count=extraction_res.total_pages,
                ocr_status=ocr_status,
                clause_count=0,
                issue_count=0,
            )
            session.add(doc)
        else:
            doc.file_path = str(saved_path)
            doc.file_size = file_size_str
            doc.page_count = extraction_res.total_pages
            doc.ocr_status = ocr_status

        # 4. Save DocumentPage entities
        for page_data in extraction_res.pages:
            page_id = f"page-{uuid.uuid4().hex[:8]}"
            doc_page = DocumentPage(
                id=page_id,
                document_id=doc_id,
                page_number=page_data.page_number,
                raw_text=page_data.normalized_text or page_data.raw_text,
                layout_boxes=page_data.layout_boxes,
            )
            session.add(doc_page)

        await session.commit()
        await session.refresh(doc)

        return IngestionResult(
            document_id=doc.id,
            bundle_id=bundle_id,
            file_name=doc.file_name,
            file_size=doc.file_size,
            page_count=doc.page_count,
            scanned_pages_count=extraction_res.scanned_pages_count,
            ocr_status=doc.ocr_status,
            ocr_engine_used=extraction_res.ocr_engine_used,
            pages=extraction_res.pages,
        )


ingestion_pipeline = IngestionPipeline()
