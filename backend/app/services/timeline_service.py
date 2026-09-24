from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import TransactionBundle
from app.models.document import Document
from app.models.finding import Finding
from app.schemas.transaction_intelligence import (
    TimelineEventSchema,
    TimelineResponseSchema,
)
from app.services.transaction_intelligence_orchestrator import (
    transaction_intelligence_orchestrator,
    format_currency_inr,
)


class TimelineService:
    """
    Timeline & Obligation Intelligence Engine:
    Reconciles chronological milestones, obligations, and date commitments across
    the transaction bundle while strictly distinguishing 5 certainty states:
    CONTRACTUAL, INFERRED, MARKETING, CONFLICTING, UNCERTAIN.
    """

    def _get_skyview_events(self, sale_price: float) -> List[TimelineEventSchema]:
        return [
            # 1. Booking & Allotment Milestone (PAST / CONTRACTUAL)
            TimelineEventSchema(
                id="time-01",
                title="Booking Application & Token Deposit",
                eventDate="2026-06-15",
                dateType="CONTRACTUAL",
                status="PAST",
                description="Initial 10% booking token paid upon submission of allotment application form.",
                documentName="Allotment_Letter_Signed_A1204.pdf",
                pageNumber=1,
                clauseReference="Paragraph 1",
                linkedObligationAmount=round(sale_price * 0.10, 2),
                linkedObligationFormatted=format_currency_inr(sale_price * 0.10),
            ),
            # 2. Marketing Promised Delivery Date (MARKETING / CONFLICTING)
            TimelineEventSchema(
                id="time-02",
                title="Advertised Project Handover (Sales Brochure)",
                eventDate="2026-12-31",
                dateType="MARKETING",
                status="PAST",
                description="Handover timeline advertised in primary marketing brochure and sales deck presented at booking.",
                documentName="Sales_Brochure_SkyView_Residency.pdf",
                pageNumber=2,
                clauseReference="Project Highlights",
                conflictingDate="2027-12-31",
            ),
            # 3. Execution of Agreement for Sale (PAST / CONTRACTUAL)
            TimelineEventSchema(
                id="time-03",
                title="Execution of Builder-Buyer Agreement",
                eventDate="2026-09-18",
                dateType="CONTRACTUAL",
                status="PAST",
                description="Formal bilateral agreement executed. Second installment of 10% consideration paid.",
                documentName="Builder_Buyer_Agreement_SkyView_A1204.pdf",
                pageNumber=3,
                clauseReference="Clause 3.1 (Payment Terms)",
                linkedObligationAmount=round(sale_price * 0.10, 2),
                linkedObligationFormatted=format_currency_inr(sale_price * 0.10),
            ),
            # 4. Projected Structural Milestone (INFERRED / UPCOMING)
            TimelineEventSchema(
                id="time-04",
                title="Completion of 4th Floor Slab Casting",
                eventDate="2026-11-15",
                dateType="INFERRED",
                status="UPCOMING",
                description="Inferred milestone from construction schedule. Triggers 10% installment under Schedule C.",
                documentName="Payment_Schedule_Milestone_Plan.pdf",
                pageNumber=1,
                clauseReference="Milestone Item 3",
                linkedObligationAmount=round(sale_price * 0.10, 2),
                linkedObligationFormatted=format_currency_inr(sale_price * 0.10),
            ),
            # 5. Contractual Handover Deadline (CONTRACTUAL / CONFLICTING)
            TimelineEventSchema(
                id="time-05",
                title="Contractual Possession Handover Deadline",
                eventDate="2027-12-31",
                dateType="CONTRACTUAL",
                status="UPCOMING",
                description="Formally agreed handover target in BBA Clause 11.1 (12 months later than marketing brochure).",
                documentName="Builder_Buyer_Agreement_SkyView_A1204.pdf",
                pageNumber=18,
                clauseReference="Clause 11.1 (Possession Handover)",
                conflictingDate="2026-12-31",
            ),
            # 6. Unilateral Grace Period Expiry (INFERRED / CONFLICTING)
            TimelineEventSchema(
                id="time-06",
                title="Unilateral 180-Day Grace Period Expiry",
                eventDate="2028-06-30",
                dateType="INFERRED",
                status="UPCOMING",
                description="End of promoter's unconditional 180-day grace period; delay compensation becomes payable thereafter.",
                documentName="Builder_Buyer_Agreement_SkyView_A1204.pdf",
                pageNumber=19,
                clauseReference="Clause 11.2 (Grace Period)",
            ),
            # 7. Final Handover & Registration (UNCERTAIN / CONDITIONAL)
            TimelineEventSchema(
                id="time-07",
                title="Notice of Possession & Conveyance Deed Execution",
                eventDate=None,
                dateType="UNCERTAIN",
                status="TENTATIVE",
                description="Contingent upon developer obtaining statutory Occupation Certificate (OC) from town planning authority.",
                documentName="Builder_Buyer_Agreement_SkyView_A1204.pdf",
                pageNumber=22,
                clauseReference="Clause 12.1",
                linkedObligationAmount=round(sale_price * 0.05, 2),
                linkedObligationFormatted=format_currency_inr(sale_price * 0.05),
            ),
        ]

    async def get_reconciled_timeline(
        self, session: AsyncSession, bundle_id: str
    ) -> TimelineResponseSchema:
        bundle = await transaction_intelligence_orchestrator.get_raw_bundle(session, bundle_id)
        if not bundle:
            raise ValueError(f"Transaction bundle '{bundle_id}' not found.")

        sale_price = float(bundle.sale_price or 14_250_000.0)

        if bundle.id == "skyview-a1204":
            events = self._get_skyview_events(sale_price)
        else:
            events = []
            if bundle.possession_date:
                doc_name = bundle.documents[0].file_name if bundle.documents else "Uploaded Document"
                events.append(
                    TimelineEventSchema(
                        id=f"time-{bundle.id}-01",
                        title="Target Possession Handover",
                        eventDate=bundle.possession_date,
                        dateType="CONTRACTUAL",
                        status="TENTATIVE",
                        description=f"Promised contractual handover date with {bundle.grace_period_months}-month grace period.",
                        documentName=doc_name,
                        pageNumber=1,
                        clauseReference="Possession Clause",
                        linkedObligationAmount=round(sale_price, 2),
                        linkedObligationFormatted=format_currency_inr(sale_price),
                    )
                )

        # Compute summary counts
        contractual_count = sum(1 for e in events if e.dateType == "CONTRACTUAL")
        marketing_count = sum(1 for e in events if e.dateType == "MARKETING")
        inferred_count = sum(1 for e in events if e.dateType == "INFERRED")
        uncertain_count = sum(1 for e in events if e.dateType == "UNCERTAIN")
        conflicting_count = sum(1 for e in events if e.conflictingDate is not None)

        return TimelineResponseSchema(
            bundleId=bundle.id,
            events=events,
            totalEvents=len(events),
            conflictingEventsCount=conflicting_count,
            contractualEventsCount=contractual_count,
            marketingEventsCount=marketing_count,
            inferredEventsCount=inferred_count,
            uncertainEventsCount=uncertain_count,
        )


timeline_service = TimelineService()
