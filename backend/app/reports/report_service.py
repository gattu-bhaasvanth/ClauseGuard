import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.transaction import TransactionBundle
from app.models.document import Document
from app.models.clause import Clause
from app.models.finding import Finding
from app.models.attribute import ExtractedAttribute

from app.schemas.report import (
    TransactionAuditReportSchema,
    DocumentChecklistItemSchema,
    RiskCategoryScoreSchema,
)
from app.schemas.finding import InconsistencyResponseSchema, RiskResponseSchema
from app.intelligence.document_checklist import document_checklist_auditor
from app.intelligence.risk_scorer import transaction_risk_scorer
from app.intelligence.summary_synthesizer import executive_summary_synthesizer
from app.intelligence.alignment_matrix import alignment_matrix_builder
from app.reports.pdf_generator import audit_report_pdf_generator


LEGAL_DISCLAIMER_TEXT = (
    "THIS TRANSACTION AUDIT REPORT IS AN INFORMATIONAL AI-ASSISTED DOCUMENT COMPARISON TOOL AND DOES NOT "
    "CONSTITUTE FORMAL LEGAL ADVICE, TITLE GUARANTEE, OR REGULATORY ENDORSEMENT. REAL-ESTATE CONVEYANCING "
    "INVOLVES BINDING LEGAL LIABILITIES. ALL IDENTIFIED INCONSISTENCIES, VARIATIONS, AND CONTRACTUAL RISKS "
    "SHOULD BE SUBMITTED TO A QUALIFIED LEGAL PRACTITIONER BEFORE SIGNING."
)


class TransactionReportService:
    """
    Assembles complete transaction audit report schemas and coordinates PDF rendering.
    """

    async def build_audit_report(
        self, session: AsyncSession, bundle_id: str
    ) -> TransactionAuditReportSchema:
        # 1. Fetch Bundle
        res_bundle = await session.execute(
            select(TransactionBundle).filter_by(id=bundle_id)
        )
        bundle = res_bundle.scalar_one_or_none()
        if not bundle:
            raise ValueError(f"Transaction bundle '{bundle_id}' not found.")

        # 2. Fetch Documents
        res_docs = await session.execute(
            select(Document).filter_by(bundle_id=bundle_id)
        )
        documents = res_docs.scalars().all()

        # 3. Fetch Clauses
        res_clauses = await session.execute(
            select(Clause).filter_by(bundle_id=bundle_id)
        )
        clauses = res_clauses.scalars().all()

        # 4. Fetch Findings
        res_findings = await session.execute(
            select(Finding).filter_by(bundle_id=bundle_id)
        )
        findings = res_findings.scalars().all()

        # 5. Fetch Attributes
        res_attrs = await session.execute(
            select(ExtractedAttribute).filter_by(bundle_id=bundle_id)
        )
        attributes = res_attrs.scalars().all()

        # 6. Run Document Checklist Audit
        checklist = document_checklist_auditor.audit_documents(documents)
        missing_count = sum(1 for item in checklist if item.status == "MISSING")

        # 7. Run Risk Scorer
        risk_scores = transaction_risk_scorer.compute_category_scores(clauses, findings)

        # 8. Synthesize Executive Summary
        exec_summary = executive_summary_synthesizer.synthesize_summary(
            bundle=bundle,
            findings=findings,
            missing_doc_count=missing_count,
        )

        # 9. Build Comparison Matrix
        matrix_res = alignment_matrix_builder.build_matrix(
            bundle_id=bundle_id,
            documents=documents,
            attributes=attributes,
        )

        # 10. Map findings
        inconsistencies = [
            InconsistencyResponseSchema(
                id=f.id,
                title=f.title,
                field=f.category or "GENERAL",
                category=f.category or "GENERAL",
                severity=f.severity or "HIGH",
                description=f.description or "",
                primaryEvidence=f.primary_evidence,
                secondaryEvidence=f.secondary_evidence or f.primary_evidence,
                detectedAt=f.detected_at.isoformat() if f.detected_at else "",
            )
            for f in findings
            if f.finding_type == "INCONSISTENCY"
        ]

        risks = [
            RiskResponseSchema(
                id=f.id,
                title=f.title,
                clauseType=f.category or "GENERAL",
                severity=f.severity or "HIGH",
                impact=f.impact or "",
                explanation=f.description or "",
                citation=f.primary_evidence,
                recommendationNote=f.recommendation_note or "",
            )
            for f in findings
            if f.finding_type == "RISK"
        ]

        report_id = f"rpt-{bundle_id[:8]}-{uuid.uuid4().hex[:6]}"

        return TransactionAuditReportSchema(
            reportId=report_id,
            bundleId=bundle_id,
            generatedAt=datetime.utcnow().isoformat(),
            projectTitle=bundle.project or bundle.title,
            unit=bundle.unit or "N/A",
            developer=bundle.developer or "Promoter",
            city=bundle.city or "India",
            healthScore=bundle.health_score or 100,
            status=bundle.status or "ANALYSIS_COMPLETE",
            executiveSummary=exec_summary,
            documentChecklist=checklist,
            categoryRiskScores=risk_scores,
            inconsistencies=inconsistencies,
            risks=risks,
            comparisonMatrix=matrix_res.matrix,
            disclaimer=LEGAL_DISCLAIMER_TEXT,
        )

    async def generate_audit_report_pdf(
        self, session: AsyncSession, bundle_id: str
    ) -> bytes:
        report = await self.build_audit_report(session, bundle_id)
        return audit_report_pdf_generator.generate_pdf(report)


report_service = TransactionReportService()
