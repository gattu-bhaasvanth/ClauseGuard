from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.transaction import TransactionBundle
from app.models.document import Document
from app.models.attribute import ExtractedAttribute
from app.models.finding import Finding
from app.intelligence.evaluators import (
    BaseDiscrepancyEvaluator,
    AreaDiscrepancyEvaluator,
    PossessionDiscrepancyEvaluator,
    PricingDiscrepancyEvaluator,
    UnitDiscrepancyEvaluator,
)
from app.schemas.finding import InconsistencyResponseSchema, RiskResponseSchema
from app.schemas.matrix import TransactionAnalysisResponseSchema


class CrossDocumentIntelligenceEngine:
    """
    Coordinates cross-document inconsistency detection, evidence assembly,
    database persistence, and transaction health scoring.
    """

    SEVERITY_PENALTIES = {
        "CRITICAL": 20,
        "HIGH": 10,
        "MEDIUM": 5,
        "LOW": 2,
    }

    def __init__(self, evaluators: Optional[List[BaseDiscrepancyEvaluator]] = None):
        self.evaluators = evaluators or [
            AreaDiscrepancyEvaluator(),
            PossessionDiscrepancyEvaluator(),
            PricingDiscrepancyEvaluator(),
            UnitDiscrepancyEvaluator(),
        ]

    async def analyze_transaction(
        self, session: AsyncSession, bundle_id: str
    ) -> TransactionAnalysisResponseSchema:
        # 1. Fetch bundle
        res_bundle = await session.execute(
            select(TransactionBundle).filter_by(id=bundle_id)
        )
        bundle = res_bundle.scalar_one_or_none()
        if not bundle:
            raise ValueError(f"Transaction bundle '{bundle_id}' not found.")

        # 2. Fetch all documents for this bundle
        res_docs = await session.execute(
            select(Document).filter_by(bundle_id=bundle_id)
        )
        documents = res_docs.scalars().all()

        # 3. Fetch all extracted attributes for this bundle
        res_attrs = await session.execute(
            select(ExtractedAttribute).filter_by(bundle_id=bundle_id)
        )
        attributes = res_attrs.scalars().all()

        # 4. Run discrepancy evaluators
        detected_inconsistencies: List[Finding] = []
        for evaluator in self.evaluators:
            findings = evaluator.evaluate(
                bundle_id=bundle_id,
                documents=documents,
                attributes=attributes,
            )
            detected_inconsistencies.extend(findings)

        # 5. Clean old INCONSISTENCY findings for this bundle to prevent duplication
        await session.execute(
            delete(Finding)
            .filter_by(bundle_id=bundle_id, finding_type="INCONSISTENCY")
        )

        # 6. Add new detected inconsistencies to session
        for f in detected_inconsistencies:
            session.add(f)

        await session.flush()

        # 7. Fetch all active findings (new inconsistencies + existing risks)
        all_findings_res = await session.execute(
            select(Finding).filter_by(bundle_id=bundle_id)
        )
        all_findings = all_findings_res.scalars().all()

        inconsistencies = [f for f in all_findings if f.finding_type == "INCONSISTENCY"]
        risks = [f for f in all_findings if f.finding_type == "RISK"]

        # 8. Compute dynamic health score
        penalty = 0
        for f in all_findings:
            sev = (f.severity or "MEDIUM").upper()
            penalty += self.SEVERITY_PENALTIES.get(sev, 5)

        computed_score = max(10, 100 - penalty)
        new_status = "ANALYSIS_COMPLETE" if computed_score >= 75 else "NEEDS_ATTENTION"

        bundle.health_score = computed_score
        bundle.status = new_status
        await session.commit()

        # 9. Format response
        summary_msg = (
            f"Cross-document analysis complete. Detected {len(inconsistencies)} inconsistency findings "
            f"and {len(risks)} contractual risk alerts. Health score computed at {computed_score}/100."
        )

        return TransactionAnalysisResponseSchema(
            bundleId=bundle_id,
            healthScore=computed_score,
            status=new_status,
            totalIssues=len(all_findings),
            inconsistenciesCount=len(inconsistencies),
            risksCount=len(risks),
            inconsistencies=[
                InconsistencyResponseSchema(
                    id=inc.id,
                    title=inc.title,
                    field=inc.category or "GENERAL",
                    category=inc.category or "GENERAL",
                    severity=inc.severity or "HIGH",
                    description=inc.description or "",
                    primaryEvidence=inc.primary_evidence,
                    secondaryEvidence=inc.secondary_evidence or inc.primary_evidence,
                    detectedAt=inc.detected_at.isoformat() if inc.detected_at else "",
                )
                for inc in inconsistencies
            ],
            risks=[
                RiskResponseSchema(
                    id=r.id,
                    title=r.title,
                    clauseType=r.category or "GENERAL",
                    severity=r.severity or "HIGH",
                    impact=r.impact or "",
                    explanation=r.description or "",
                    citation=r.primary_evidence,
                    recommendationNote=r.recommendation_note or "",
                )
                for r in risks
            ],
            summary=summary_msg,
        )


cross_document_engine = CrossDocumentIntelligenceEngine()
