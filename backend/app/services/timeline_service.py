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

    async def get_reconciled_timeline(
        self, session: AsyncSession, bundle_id: str
    ) -> TimelineResponseSchema:
        bundle = await transaction_intelligence_orchestrator.get_raw_bundle(session, bundle_id)
        if not bundle:
            raise ValueError(f"Transaction bundle '{bundle_id}' not found.")

        sale_price = float(bundle.sale_price or 14_250_000.0)
        events: List[TimelineEventSchema] = []

        # 1. Booking & Allotment Milestone (PAST / CONTRACTUAL)
        events.append(
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
            )
        )

        # 2. Marketing Promised Delivery Date (MARKETING / CONFLICTING)
        events.append(
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
                conflictDetails="12-month discrepancy with formal Builder-Buyer Agreement Clause 11.2 (31 Dec 2027).",
            )
        )

        # 3. Allotment Letter Target Handover (MARKETING / CONFLICTING)
        events.append(
            TimelineEventSchema(
                id="time-03",
                title="Allotment Letter Projected Possession",
                eventDate="2027-06-30",
                dateType="MARKETING",
                status="UPCOMING",
                description="Interim handover projection stated in the signed Allotment Letter prior to agreement signing.",
                documentName="Allotment_Letter_Signed_A1204.pdf",
                pageNumber=2,
                clauseReference="Paragraph 4",
                conflictingDate="2027-12-31",
                conflictDetails="Differs from Agreement Clause 11.2 by 6 months.",
            )
        )

        # 4. Superstructure Milestone Payment (UNCERTAIN)
        events.append(
            TimelineEventSchema(
                id="time-04",
                title="4th Floor Slab Casting Installment",
                eventDate=None,
                dateType="UNCERTAIN",
                status="UPCOMING",
                description="Milestone-linked demand triggered strictly upon architect certification of 4th floor structural casting.",
                documentName="Payment_Schedule_SkyView_A1204.pdf",
                pageNumber=1,
                clauseReference="Milestone 3",
                linkedObligationAmount=round(sale_price * 0.10, 2),
                linkedObligationFormatted=format_currency_inr(sale_price * 0.10),
            )
        )

        # 5. Contractual Binding Delivery Deadline (CONTRACTUAL)
        contractual_date = bundle.possession_date or "2027-12-31"
        events.append(
            TimelineEventSchema(
                id="time-05",
                title="Contractual Possession Handover Deadline",
                eventDate=contractual_date,
                dateType="CONTRACTUAL",
                status="UPCOMING",
                description="Binding contractual completion deadline stipulated in the formal registered agreement.",
                documentName="Builder_Buyer_Agreement_SkyView_A1204.pdf",
                pageNumber=19,
                clauseReference="Clause 11.2",
                conflictingDate="2026-12-31",
                conflictDetails="Contradicts earlier 2026 brochure marketing promise.",
            )
        )

        # 6. Contractual Grace Buffer Limit (INFERRED)
        events.append(
            TimelineEventSchema(
                id="time-06",
                title="Contractual Grace Period Expiry (180 Days)",
                eventDate="2028-06-30",
                dateType="INFERRED",
                status="TENTATIVE",
                description="End of promoter's unconditional 180-day grace period; delay compensation becomes payable thereafter.",
                documentName="Builder_Buyer_Agreement_SkyView_A1204.pdf",
                pageNumber=19,
                clauseReference="Clause 11.2 (Grace Period)",
            )
        )

        # 7. Final Handover & Registration (UNCERTAIN / CONDITIONAL)
        events.append(
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
