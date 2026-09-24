from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.document import Document, DocumentPage
from app.models.clause import Clause
from app.models.attribute import ExtractedAttribute
from app.schemas.document import (
    DocumentResponseSchema,
    DocumentCreateSchema,
    DocumentPageResponseSchema,
    DocumentIngestionResponseSchema,
)
from app.schemas.clause import ClauseResponseSchema
from app.schemas.attribute import (
    ExtractedAttributeSchema,
    DocumentMetadataResponseSchema,
)
from app.services import transaction_service
from app.ingestion.pipeline import ingestion_pipeline
from app.intelligence.clause_engine import clause_intelligence_engine
from app.intelligence.metadata_engine import metadata_engine

router = APIRouter(prefix="/transactions/{transaction_id}/documents", tags=["Documents"])


@router.get("", response_model=List[DocumentResponseSchema])
async def list_transaction_documents(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """List all documents uploaded to a transaction bundle."""
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )
    return bundle.documents


@router.post("", response_model=DocumentResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_document(
    transaction_id: str,
    payload: DocumentCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    """Register document metadata within a transaction bundle."""
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )
    return await transaction_service.add_document_to_transaction(db, transaction_id, payload)


MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB production limit


async def _get_verified_document(
    db: AsyncSession, transaction_id: str, document_id: str
) -> Document:
    """Strict transaction isolation: verify document belongs to the requested transaction bundle."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.bundle_id == transaction_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found in transaction '{transaction_id}'.",
        )
    return doc


@router.post(
    "/upload",
    response_model=DocumentIngestionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def upload_and_ingest_document(
    transaction_id: str,
    file: UploadFile = File(...),
    document_type: str = Form("OTHER"),
    auto_extract_clauses: bool = Form(True),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a transaction PDF file, automatically extract text, layout coordinates,
    detect scanned pages, apply OCR fallback where required, and optionally segment clauses.
    """
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )

    # Validate file extension
    filename = file.filename or "uploaded_document.pdf"
    lower_fn = filename.lower()
    if not lower_fn.endswith((".pdf", ".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported document format. Only PDF and scanned image files (.pdf, .png, .jpg, .jpeg) are supported.",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum allowed limit of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB.",
        )

    # Magic byte validation for PDFs
    if lower_fn.endswith(".pdf") and not file_bytes.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupt PDF file: missing '%PDF' file header.",
        )

    try:
        result = await ingestion_pipeline.ingest_document(
            session=db,
            bundle_id=transaction_id,
            file_bytes=file_bytes,
            original_filename=filename,
            document_type=document_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document ingestion failed: {str(e)}",
        )

    # Auto extract clauses and metadata if requested
    if auto_extract_clauses:
        await clause_intelligence_engine.process_document_clauses(
            session=db, bundle_id=transaction_id, document_id=result.document_id
        )
        await metadata_engine.process_document_metadata(
            session=db, bundle_id=transaction_id, document_id=result.document_id
        )

    return DocumentIngestionResponseSchema(
        documentId=result.document_id,
        bundleId=result.bundle_id,
        fileName=result.file_name,
        fileSize=result.file_size,
        pageCount=result.page_count,
        scannedPagesCount=result.scanned_pages_count,
        ocrStatus=result.ocr_status,
        ocrEngineUsed=result.ocr_engine_used,
        message=f"Document ingested successfully ({result.page_count} pages processed).",
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponseSchema,
)
async def get_document(
    transaction_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve document details by ID, enforcing strict transaction bundle isolation."""
    return await _get_verified_document(db, transaction_id, document_id)


@router.get(
    "/{document_id}/pages",
    response_model=List[DocumentPageResponseSchema],
)
async def get_document_pages(
    transaction_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all parsed pages with layout coordinates and raw extracted text."""
    await _get_verified_document(db, transaction_id, document_id)
    result = await db.execute(
        select(DocumentPage)
        .filter_by(document_id=document_id)
        .order_by(DocumentPage.page_number.asc())
    )
    pages = result.scalars().all()

    return [
        DocumentPageResponseSchema(
            id=p.id,
            documentId=p.document_id,
            pageNumber=p.page_number,
            rawText=p.raw_text,
            layoutBoxes=p.layout_boxes or [],
        )
        for p in pages
    ]


@router.post(
    "/{document_id}/extract-clauses",
    response_model=List[ClauseResponseSchema],
)
async def extract_document_clauses(
    transaction_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers clause boundary detection and legal taxonomy classification on an ingested document.
    """
    await _get_verified_document(db, transaction_id, document_id)

    clauses = await clause_intelligence_engine.process_document_clauses(
        session=db, bundle_id=transaction_id, document_id=document_id
    )

    return [
        ClauseResponseSchema(
            id=c.id,
            clauseNumber=c.clause_number,
            title=c.title,
            category=c.category,
            status=c.status,
            severity=c.severity,
            obligationType=c.obligation_type,
            pageNumber=c.page_number,
            previewText=c.preview_text,
            fullExcerpt=c.full_excerpt,
            analysisSummary=c.analysis_summary,
            riskDetails=c.risk_details,
            confidence=getattr(c, "confidence", 1.0) or 1.0,
            classificationSource=getattr(c, "classification_source", "DETERMINISTIC_HEURISTIC") or "DETERMINISTIC_HEURISTIC",
            modelVersion=getattr(c, "model_version", None),
            datasetVersion=getattr(c, "dataset_version", None),
            topAlternatives=getattr(c, "top_alternatives", None),
            explanationNotes=getattr(c, "explanation_notes", None),
        )
        for c in clauses
    ]


@router.get(
    "/{document_id}/clauses",
    response_model=List[ClauseResponseSchema],
)
async def get_document_clauses(
    transaction_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve extracted clauses for a specific document."""
    await _get_verified_document(db, transaction_id, document_id)
    result = await db.execute(
        select(Clause)
        .filter_by(document_id=document_id)
        .order_by(Clause.page_number.asc())
    )
    clauses = result.scalars().all()
    return [
        ClauseResponseSchema(
            id=c.id,
            clauseNumber=c.clause_number,
            title=c.title,
            category=c.category,
            status=c.status,
            severity=c.severity,
            obligationType=c.obligation_type,
            pageNumber=c.page_number,
            previewText=c.preview_text,
            fullExcerpt=c.full_excerpt,
            analysisSummary=c.analysis_summary,
            riskDetails=c.risk_details,
            confidence=getattr(c, "confidence", 1.0) or 1.0,
            classificationSource=getattr(c, "classification_source", "DETERMINISTIC_HEURISTIC") or "DETERMINISTIC_HEURISTIC",
            modelVersion=getattr(c, "model_version", None),
            datasetVersion=getattr(c, "dataset_version", None),
            topAlternatives=getattr(c, "top_alternatives", None),
            explanationNotes=getattr(c, "explanation_notes", None),
        )
        for c in clauses
    ]


@router.post(
    "/{document_id}/extract-metadata",
    response_model=DocumentMetadataResponseSchema,
)
async def extract_document_metadata(
    transaction_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Extracts structured real-estate parameters (carpet area, price, timelines, parties)
    from document pages and segmented clauses.
    """
    await _get_verified_document(db, transaction_id, document_id)

    attrs = await metadata_engine.process_document_metadata(
        session=db, bundle_id=transaction_id, document_id=document_id
    )

    return DocumentMetadataResponseSchema(
        documentId=document_id,
        bundleId=transaction_id,
        attributeCount=len(attrs),
        attributes=[
            ExtractedAttributeSchema(
                id=a.id,
                documentId=a.document_id,
                bundleId=a.bundle_id,
                attributeKey=a.attribute_key,
                attributeValue=a.attribute_value,
                normalizedValue=a.normalized_value or "",
                unit=a.unit or "",
                sourcePage=a.source_page or 1,
                sourceClause=a.source_clause,
                rawExcerpt=a.raw_excerpt,
                confidence=a.confidence or 1.0,
            )
            for a in attrs
        ],
    )


@router.get(
    "/{document_id}/metadata",
    response_model=DocumentMetadataResponseSchema,
)
async def get_document_metadata(
    transaction_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve extracted metadata attributes for a specific document."""
    await _get_verified_document(db, transaction_id, document_id)
    res = await db.execute(
        select(ExtractedAttribute)
        .filter_by(document_id=document_id)
        .order_by(ExtractedAttribute.source_page.asc())
    )
    attrs = res.scalars().all()
    return DocumentMetadataResponseSchema(
        documentId=document_id,
        bundleId=transaction_id,
        attributeCount=len(attrs),
        attributes=[
            ExtractedAttributeSchema(
                id=a.id,
                documentId=a.document_id,
                bundleId=a.bundle_id,
                attributeKey=a.attribute_key,
                attributeValue=a.attribute_value,
                normalizedValue=a.normalized_value or "",
                unit=a.unit or "",
                sourcePage=a.source_page or 1,
                sourceClause=a.source_clause,
                rawExcerpt=a.raw_excerpt,
                confidence=a.confidence or 1.0,
            )
            for a in attrs
        ],
    )
