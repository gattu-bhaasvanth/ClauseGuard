from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.document import DocumentResponseSchema, DocumentCreateSchema
from app.services import transaction_service

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
