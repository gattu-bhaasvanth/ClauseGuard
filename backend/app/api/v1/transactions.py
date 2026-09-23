from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.transaction import (
    TransactionListItemSchema,
    TransactionDetailSchema,
    TransactionCreateSchema,
)
from app.schemas.clause import ClauseResponseSchema
from app.schemas.finding import InconsistencyResponseSchema, RiskResponseSchema
from app.schemas.attribute import UnifiedTransactionMetadataSchema
from app.schemas.matrix import (
    ComparisonMatrixResponseSchema,
    TransactionAnalysisResponseSchema,
)
from app.models.document import Document
from app.models.attribute import ExtractedAttribute
from app.services import transaction_service
from app.intelligence.metadata_engine import metadata_engine
from app.intelligence.cross_doc_engine import cross_document_engine
from app.intelligence.alignment_matrix import alignment_matrix_builder
from sqlalchemy import select

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionListItemSchema])
async def list_transactions(db: AsyncSession = Depends(get_db)):
    """List all active property transaction bundles."""
    return await transaction_service.get_all_transactions(db)


@router.post("", response_model=TransactionDetailSchema, status_code=status.HTTP_201_CREATED)
async def create_new_transaction(
    payload: TransactionCreateSchema, db: AsyncSession = Depends(get_db)
):
    """Create a new property transaction workspace."""
    return await transaction_service.create_transaction(db, payload)


@router.get("/{transaction_id}", response_model=TransactionDetailSchema)
async def get_transaction(transaction_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve complete transaction bundle details, metrics, and cross-document findings."""
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )
    return bundle


@router.get("/{transaction_id}/clauses", response_model=List[ClauseResponseSchema])
async def get_transaction_clauses(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """Retrieve extracted clauses for a specific transaction bundle."""
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )
    return bundle.clauses


@router.get("/{transaction_id}/findings")
async def get_transaction_findings(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """Retrieve cross-document inconsistencies and risk findings."""
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )
    return {
        "inconsistencies": bundle.inconsistencies,
        "risks": bundle.risks,
        "totalIssues": bundle.issuesCount,
    }


@router.get("/{transaction_id}/metadata", response_model=UnifiedTransactionMetadataSchema)
async def get_transaction_unified_metadata(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """Retrieve synthesized bundle-level Unified Transaction Model across all extracted attributes."""
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )
    return await metadata_engine.get_unified_transaction_metadata(
        session=db, bundle_id=transaction_id
    )


@router.post("/{transaction_id}/analyze", response_model=TransactionAnalysisResponseSchema)
async def analyze_transaction_consistency(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """
    Triggers automated cross-document consistency verification across an entire transaction bundle.
    Detects contradictions in carpet area, possession dates, pricing, and unit IDs,
    constructs dual-cited audit evidence, and recalculates the dynamic transaction health score.
    """
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )
    return await cross_document_engine.analyze_transaction(
        session=db, bundle_id=transaction_id
    )


@router.get("/{transaction_id}/inconsistencies", response_model=List[InconsistencyResponseSchema])
async def get_transaction_inconsistencies(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """Retrieve all cross-document inconsistency findings for a transaction bundle."""
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )
    return bundle.inconsistencies


@router.get("/{transaction_id}/matrix", response_model=ComparisonMatrixResponseSchema)
async def get_transaction_comparison_matrix(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """
    Retrieve side-by-side comparative attribute matrix across all documents in a bundle
    with variance flags and exact source citations.
    """
    bundle = await transaction_service.get_transaction_by_id(db, transaction_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )

    res_docs = await db.execute(select(Document).filter_by(bundle_id=transaction_id))
    documents = res_docs.scalars().all()

    res_attrs = await db.execute(select(ExtractedAttribute).filter_by(bundle_id=transaction_id))
    attributes = res_attrs.scalars().all()

    return alignment_matrix_builder.build_matrix(
        bundle_id=transaction_id,
        documents=documents,
        attributes=attributes,
    )

