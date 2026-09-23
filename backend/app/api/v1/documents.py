from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.document import Document, DocumentPage
from app.schemas.document import (
    DocumentResponseSchema,
    DocumentCreateSchema,
    DocumentPageResponseSchema,
    DocumentIngestionResponseSchema,
)
from app.services import transaction_service
from app.ingestion.pipeline import ingestion_pipeline

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


@router.post(
    "/upload",
    response_model=DocumentIngestionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def upload_and_ingest_document(
    transaction_id: str,
    file: UploadFile = File(...),
    document_type: str = Form("OTHER"),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a transaction PDF file, automatically extract text, line layout coordinates,
    detect scanned pages, and apply OCR fallback where required.
    """
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )

    # Validate file extension
    filename = file.filename or "uploaded_document.pdf"
    if not filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported document format. Only PDF and scanned image files are supported.",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    result = await ingestion_pipeline.ingest_document(
        session=db,
        bundle_id=transaction_id,
        file_bytes=file_bytes,
        original_filename=filename,
        document_type=document_type,
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
        message=f"Document ingested successfully ({result.page_count} pages processed, {result.scanned_pages_count} scanned).",
    )


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
    result = await db.execute(
        select(DocumentPage)
        .filter_by(document_id=document_id)
        .order_by(DocumentPage.page_number.asc())
    )
    pages = result.scalars().all()
    if not pages:
        # Check if document exists
        doc_result = await db.execute(select(Document).filter_by(id=document_id))
        doc = doc_result.scalar_one_or_none()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{document_id}' not found.",
            )

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
