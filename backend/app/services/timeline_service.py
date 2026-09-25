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

    def _build_dynamic_timeline_events(
        self, bundle: TransactionBundle, sale_price: float
    ) -> List[TimelineEventSchema]:
        import calendar

        events: List[TimelineEventSchema] = []
        doc_map = {d.id: d for d in bundle.documents}

        # 1. Collect all possession dates from extracted attributes
        possession_attrs = [
            a for a in bundle.extracted_attributes if a.attribute_key == "possession_date"
        ]

        # Deduplicate possession attributes per document (pick highest confidence)
        doc_possession: Dict[str, Any] = {}
        for a in possession_attrs:
            if a.document_id not in doc_possession or a.confidence > doc_possession[a.document_id].confidence:
                doc_possession[a.document_id] = a

        # Check if there are conflicting dates across documents
        unique_dates = {a.normalized_value for a in doc_possession.values() if a.normalized_value}

        ev_idx = 1
        possession_events = []
        for doc_id, attr in doc_possession.items():
            doc = doc_map.get(doc_id)
            doc_name = doc.file_name if doc else "Document"
            doc_type = (doc.document_type or "").upper() if doc else "DOCUMENT"

            is_marketing = "BROCHURE" in doc_type or "brochure" in doc_name.lower() or "marketing" in doc_name.lower()
            is_allotment = "ALLOTMENT" in doc_type or "allotment" in doc_name.lower()

            if is_marketing:
                date_type = "MARKETING"
                title = "Advertised Project Handover"
            elif is_allotment:
                date_type = "CONTRACTUAL"
                title = "Allotment Letter Promised Handover"
            else:
                date_type = "CONTRACTUAL"
                title = "Contractual Handover Deadline"

            precision = attr.unit.replace("date:", "") if (attr.unit and attr.unit.startswith("date:")) else ("YEAR" if len(attr.normalized_value) == 4 else "DAY")

            # Check if there's a conflicting date from another document
            conflicting_date = None
            if len(unique_dates) > 1:
                for other_date in unique_dates:
                    if other_date != attr.normalized_value:
                        if precision == "YEAR" and other_date.startswith(attr.normalized_value):
                            continue
                        conflicting_date = other_date
                        break

            if precision == "YEAR":
                desc = f"Target handover year ({attr.attribute_value}) stated in {doc_name}; exact day not specified."
            elif precision == "MONTH":
                desc = f"Projected completion month ({attr.attribute_value}) stated in {doc_name}."
            else:
                desc = f"Handover deadline committed in {doc_name}."

            clause_ref = f"Clause {attr.source_clause}" if attr.source_clause else f"Page {attr.source_page}"

            possession_events.append(
                TimelineEventSchema(
                    id=f"time-{bundle.id}-{ev_idx:02d}",
                    title=title,
                    eventDate=attr.normalized_value,
                    dateType=date_type,
                    status="UPCOMING",
                    description=desc,
                    documentName=doc_name,
                    pageNumber=attr.source_page or 1,
                    clauseReference=clause_ref,
                    conflictingDate=conflicting_date,
                )
            )
            ev_idx += 1

        # Sort possession events: earlier date first, marketing/contractual distinction
        possession_events.sort(key=lambda e: (e.eventDate or "9999", e.dateType != "CONTRACTUAL"))
        events.extend(possession_events)

        # 2. Check for Grace Period from Agreement / BBA
        contractual_candidates = [
            e for e in possession_events if e.dateType == "CONTRACTUAL" and len(e.eventDate or "") == 10
        ]
        bba_contractual = next((e for e in contractual_candidates if "agreement" in e.documentName.lower() or "bba" in e.documentName.lower()), None)
        contractual_p = bba_contractual or (max(contractual_candidates, key=lambda x: x.eventDate) if contractual_candidates else None)
        grace_months = bundle.grace_period_months or 6
        if contractual_p and contractual_p.eventDate:
            try:
                base_dt = datetime.strptime(contractual_p.eventDate, "%Y-%m-%d")
                new_m = base_dt.month + grace_months
                new_y = base_dt.year + (new_m - 1) // 12
                new_m = ((new_m - 1) % 12) + 1
                max_d = calendar.monthrange(new_y, new_m)[1]
                expiry_dt = datetime(new_y, new_m, min(base_dt.day, max_d))
                expiry_str = expiry_dt.strftime("%Y-%m-%d")

                events.append(
                    TimelineEventSchema(
                        id=f"time-{bundle.id}-{ev_idx:02d}",
                        title=f"Unilateral {grace_months}-Month Grace Period Expiry",
                        eventDate=expiry_str,
                        dateType="INFERRED",
                        status="UPCOMING",
                        description=f"End of promoter's {grace_months}-month grace period; delay compensation becomes legally enforceable thereafter.",
                        documentName=contractual_p.documentName,
                        pageNumber=contractual_p.pageNumber,
                        clauseReference="Grace Period Clause",
                    )
                )
                ev_idx += 1
            except Exception:
                pass

        # 3. Final Contingent Milestone (UNCERTAIN)
        events.append(
            TimelineEventSchema(
                id=f"time-{bundle.id}-{ev_idx:02d}",
                title="Notice of Possession & Conveyance Deed Execution",
                eventDate=None,
                dateType="UNCERTAIN",
                status="TENTATIVE",
                description="Contingent upon developer obtaining statutory Occupation Certificate (OC) from the municipal planning authority.",
                documentName=bundle.documents[0].file_name if bundle.documents else "Uploaded Document",
                pageNumber=1,
                clauseReference="Conveyance & OC",
                linkedObligationAmount=round(sale_price * 0.05, 2),
                linkedObligationFormatted=format_currency_inr(sale_price * 0.05),
            )
        )

        return events

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
            events = self._build_dynamic_timeline_events(bundle, sale_price)

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
