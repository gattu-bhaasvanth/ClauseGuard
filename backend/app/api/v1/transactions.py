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
from app.services import transaction_service

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
