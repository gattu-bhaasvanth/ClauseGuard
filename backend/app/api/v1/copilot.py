from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.transaction_intelligence import (
    TransactionCommandCenterResponse,
    ExplainableRiskResponseSchema,
    TimelineResponseSchema,
    TransactionBriefSchema,
)
from app.schemas.copilot import (
    CopilotQueryRequestSchema,
    CopilotQueryResponseSchema,
)
from app.services.transaction_intelligence_orchestrator import transaction_intelligence_orchestrator
from app.services.copilot_service import transaction_copilot_service
from app.services.timeline_service import timeline_service
from app.services.transaction_brief_service import transaction_brief_service

router = APIRouter(prefix="/transactions/{transaction_id}/copilot", tags=["Transaction Copilot"])


@router.get("/command-center", response_model=TransactionCommandCenterResponse)
async def get_transaction_command_center(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the executive Transaction Command Center:
    Composite health score, 5 multi-dimensional risk vectors, financial exposure breakdown,
    and prioritized action items.
    """
    try:
        return await transaction_intelligence_orchestrator.get_command_center(db, transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/query", response_model=CopilotQueryResponseSchema)
async def query_transaction_copilot(
    transaction_id: str,
    payload: CopilotQueryRequestSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    Grounded Transaction Copilot query:
    Answers bundle-level queries with multi-intent synthesis, strict citations,
    and anti-hallucination refusal guardrails.
    """
    try:
        return await transaction_copilot_service.query_copilot(db, transaction_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/explain-risk/{finding_id}", response_model=ExplainableRiskResponseSchema)
async def explain_risk_finding(
    transaction_id: str,
    finding_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Explainable Risk Intelligence ("Why is this risky?"):
    Detailed harm analysis, statutory RERA benchmarks, quantified financial impacts,
    and 5-tier citation lineage for a specific finding.
    """
    try:
        return await transaction_intelligence_orchestrator.get_explainable_risk(
            db, transaction_id, finding_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/timeline", response_model=TimelineResponseSchema)
async def get_transaction_timeline(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """
    Transaction Timeline & Obligation Intelligence:
    Reconciled chronological milestones classified into 5 certainty states:
    CONTRACTUAL, INFERRED, MARKETING, CONFLICTING, UNCERTAIN.
    """
    try:
        return await timeline_service.get_reconciled_timeline(db, transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/brief", response_model=TransactionBriefSchema)
async def get_transaction_brief(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """
    Executive Transaction Brief:
    Structured 7-section evidence-traceable executive briefing summary.
    """
    try:
        return await transaction_brief_service.generate_brief(db, transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/brief/pdf")
async def download_transaction_brief_pdf(
    transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """
    Streams a vector-quality PDF of the 7-section Executive Transaction Brief.
    """
    try:
        brief = await transaction_brief_service.generate_brief(db, transaction_id)
        pdf_bytes = transaction_brief_service.generate_pdf(brief)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="ClauseGuard_Brief_{transaction_id}.pdf"'
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
