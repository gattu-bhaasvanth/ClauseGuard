from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.transaction import TransactionBundle
from app.models.document import Document
from app.models.clause import Clause
from app.models.finding import Finding
from app.schemas.transaction import (
    TransactionCreateSchema,
    TransactionListItemSchema,
    TransactionDetailSchema,
    PropertySummarySchema,
    ImportantDateSchema,
    PaymentObligationSchema,
)
from app.schemas.document import DocumentResponseSchema, DocumentCreateSchema
from app.schemas.finding import InconsistencyResponseSchema, RiskResponseSchema
from app.schemas.clause import ClauseResponseSchema


def map_bundle_to_list_item(bundle: TransactionBundle) -> TransactionListItemSchema:
    return TransactionListItemSchema(
        id=bundle.id,
        title=bundle.title,
        property=PropertySummarySchema(
            project=bundle.project,
            developer=bundle.developer,
            unit=bundle.unit,
            floor=bundle.floor,
            tower=bundle.tower,
            carpetAreaSqFt=bundle.carpet_area_sqft,
            superAreaSqFt=bundle.super_area_sqft,
            advertisedCarpetAreaSqFt=bundle.advertised_carpet_area_sqft,
            salePrice=bundle.sale_price,
            possessionDate=bundle.possession_date,
            gracePeriodMonths=bundle.grace_period_months,
            location=bundle.location,
        ),
        healthScore=bundle.health_score,
        status=bundle.status,
        documentsCount=len(bundle.documents),
        issuesCount=len(bundle.findings),
        updatedAt=bundle.updated_at.isoformat(),
    )


def map_bundle_to_detail(bundle: TransactionBundle) -> TransactionDetailSchema:
    # Separate findings into inconsistencies and risks
    inconsistencies = []
    risks = []
    for f in bundle.findings:
        if f.finding_type == "INCONSISTENCY":
            inconsistencies.append(
                InconsistencyResponseSchema(
                    id=f.id,
                    title=f.title,
                    field=f.category,
                    category=f.category,
                    severity=f.severity,
                    description=f.description,
                    primaryEvidence=f.primary_evidence,
                    secondaryEvidence=f.secondary_evidence or f.primary_evidence,
                    detectedAt=f.detected_at.isoformat(),
                )
            )
        else:
            risks.append(
                RiskResponseSchema(
                    id=f.id,
                    title=f.title,
                    clauseType=f.category,
                    severity=f.severity,
                    impact=f.impact or "",
                    explanation=f.description,
                    citation=f.primary_evidence,
                    recommendationNote=f.recommendation_note or "",
                )
            )

    docs = [
        DocumentResponseSchema(
            id=d.id,
            fileName=d.file_name,
            documentType=d.document_type,
            fileSize=d.file_size,
            pageCount=d.page_count,
            uploadedAt=d.created_at.isoformat(),
            ocrStatus=d.ocr_status,
            clauseCount=d.clause_count,
            issueCount=d.issue_count,
        )
        for d in bundle.documents
    ]

    clauses = [
        ClauseResponseSchema(
            id=c.id,
            clauseNumber=c.clause_number,
            title=c.title,
            category=c.category,
            status=c.status,
            severity=c.severity,
            obligationType=getattr(c, "obligation_type", "MUTUAL") or "MUTUAL",
            pageNumber=c.page_number,
            previewText=c.preview_text,
            fullExcerpt=c.full_excerpt,
            analysisSummary=c.analysis_summary,
            riskDetails=c.risk_details,
        )
        for c in bundle.clauses
    ]

    # Deterministic dates & milestone obligations based on bundle
    dates = [
        ImportantDateSchema(
            id="date-01",
            title="Foundation & 4th Slab Milestone",
            date="2026-11-15",
            sourceDoc="Payment_Schedule_Milestone_Plan.pdf",
            isMilestone=True,
            status="UPCOMING",
            description="10% milestone installment due on structural slab casting.",
        ),
        ImportantDateSchema(
            id="date-02",
            title="Target Possession Handover",
            date=bundle.possession_date or "2027-12-31",
            sourceDoc="Agreement for Sale",
            isMilestone=False,
            status="TENTATIVE",
            description=f"Promised contractual handover date with {bundle.grace_period_months}-month grace period.",
        ),
    ]

    payments = [
        PaymentObligationSchema(
            id="pay-01",
            milestoneTitle="Booking & Earnest Token",
            percentage=10.0,
            amount=bundle.sale_price * 0.10,
            dueDateCondition="Paid at application",
            status="PAID",
            clauseCitation="Allotment Letter, Page 1",
        ),
        PaymentObligationSchema(
            id="pay-02",
            milestoneTitle="Execution of Sale Agreement",
            percentage=10.0,
            amount=bundle.sale_price * 0.10,
            dueDateCondition="Within 30 days of allotment",
            status="PAID",
            clauseCitation="Clause 3.1",
        ),
        PaymentObligationSchema(
            id="pay-03",
            milestoneTitle="Completion of 4th Slab",
            percentage=10.0,
            amount=bundle.sale_price * 0.10,
            dueDateCondition="Projected 15 Nov 2026",
            status="PENDING",
            clauseCitation="Payment Schedule Item 3",
        ),
    ]

    return TransactionDetailSchema(
        id=bundle.id,
        title=bundle.title,
        property=PropertySummarySchema(
            project=bundle.project,
            developer=bundle.developer,
            unit=bundle.unit,
            floor=bundle.floor,
            tower=bundle.tower,
            carpetAreaSqFt=bundle.carpet_area_sqft,
            superAreaSqFt=bundle.super_area_sqft,
            advertisedCarpetAreaSqFt=bundle.advertised_carpet_area_sqft,
            salePrice=bundle.sale_price,
            possessionDate=bundle.possession_date,
            gracePeriodMonths=bundle.grace_period_months,
            location=bundle.location,
        ),
        healthScore=bundle.health_score,
        status=bundle.status,
        documentsCount=len(docs),
        issuesCount=len(inconsistencies) + len(risks),
        inconsistenciesCount=len(inconsistencies),
        risksCount=len(risks),
        importantDatesCount=len(dates),
        paymentObligationsCount=len(payments),
        documents=docs,
        inconsistencies=inconsistencies,
        risks=risks,
        importantDates=dates,
        paymentObligations=payments,
        clauses=clauses,
        createdAt=bundle.created_at.isoformat(),
        updatedAt=bundle.updated_at.isoformat(),
    )


async def get_all_transactions(session: AsyncSession) -> List[TransactionListItemSchema]:
    result = await session.execute(
        select(TransactionBundle)
        .options(selectinload(TransactionBundle.documents), selectinload(TransactionBundle.findings))
        .order_by(TransactionBundle.created_at.desc())
    )
    bundles = result.scalars().all()
    return [map_bundle_to_list_item(b) for b in bundles]


async def get_transaction_by_id(session: AsyncSession, bundle_id: str) -> Optional[TransactionDetailSchema]:
    result = await session.execute(
        select(TransactionBundle)
        .filter_by(id=bundle_id)
        .options(
            selectinload(TransactionBundle.documents),
            selectinload(TransactionBundle.findings),
            selectinload(TransactionBundle.clauses),
        )
    )
    bundle = result.scalar_one_or_none()
    if not bundle:
        return None
    return map_bundle_to_detail(bundle)


async def create_transaction(session: AsyncSession, data: TransactionCreateSchema) -> TransactionDetailSchema:
    bundle_id = f"tx-{uuid.uuid4().hex[:8]}"
    bundle = TransactionBundle(
        id=bundle_id,
        title=f"{data.projectName} — {data.unit}",
        project=data.projectName,
        unit=data.unit,
        floor=1,
        tower="Tower A",
        developer=data.developer,
        city=data.city,
        location=f"{data.projectName}, {data.city}",
        property_type=data.propertyType or "Residential Apartment",
        carpet_area_sqft=data.carpetAreaSqFt or 1200.0,
        super_area_sqft=data.superAreaSqFt or 1600.0,
        advertised_carpet_area_sqft=data.carpetAreaSqFt or 1200.0,
        sale_price=data.approxPrice or 10000000.0,
        possession_date="2027-12-31",
        grace_period_months=6,
        health_score=85,
        status="IN_PROGRESS",
    )
    session.add(bundle)
    await session.commit()
    await session.refresh(bundle)
    return await get_transaction_by_id(session, bundle_id)  # type: ignore


async def add_document_to_transaction(
    session: AsyncSession, bundle_id: str, doc_in: DocumentCreateSchema
) -> DocumentResponseSchema:
    doc_id = f"doc-{uuid.uuid4().hex[:8]}"
    doc = Document(
        id=doc_id,
        bundle_id=bundle_id,
        file_name=doc_in.file_name,
        document_type=doc_in.document_type,
        file_path=doc_in.file_path or "",
        file_size=doc_in.file_size or "1.5 MB",
        page_count=doc_in.page_count or 10,
        ocr_status="COMPLETED",
        clause_count=0,
        issue_count=0,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentResponseSchema(
        id=doc.id,
        fileName=doc.file_name,
        documentType=doc.document_type,
        fileSize=doc.file_size,
        pageCount=doc.page_count,
        uploadedAt=doc.created_at.isoformat(),
        ocrStatus=doc.ocr_status,
        clauseCount=doc.clause_count,
        issueCount=doc.issue_count,
    )
