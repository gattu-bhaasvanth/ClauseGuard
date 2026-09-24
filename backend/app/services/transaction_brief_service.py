from typing import List, Dict, Any, Optional
from datetime import datetime
import fitz
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import TransactionBundle
from app.schemas.transaction_intelligence import (
    TransactionBriefSchema,
    BriefSectionSchema,
)
from app.services.transaction_intelligence_orchestrator import (
    transaction_intelligence_orchestrator,
    format_currency_inr,
)
from app.services.timeline_service import timeline_service


class TransactionBriefService:
    """
    Executive Transaction Brief Engine:
    Synthesizes an evidence-traceable 7-section executive briefing document
    and exports vector-quality PDF and structured JSON reports.
    """

    PAGE_WIDTH = 595
    PAGE_HEIGHT = 842

    DARK_NAVY = (0.08, 0.09, 0.12)
    EMERALD = (0.06, 0.6, 0.38)
    AMBER = (0.85, 0.55, 0.1)
    ROSE = (0.85, 0.2, 0.25)
    LIGHT_GRAY = (0.94, 0.95, 0.96)
    TEXT_DARK = (0.15, 0.15, 0.18)
    TEXT_MUTED = (0.45, 0.45, 0.5)

    async def generate_brief(
        self, session: AsyncSession, bundle_id: str
    ) -> TransactionBriefSchema:
        bundle = await transaction_intelligence_orchestrator.get_raw_bundle(session, bundle_id)
        if not bundle:
            raise ValueError(f"Transaction bundle '{bundle_id}' not found.")

        cmd = await transaction_intelligence_orchestrator.get_command_center(session, bundle_id)
        timeline = await timeline_service.get_reconciled_timeline(session, bundle_id)

        if bundle.id == "skyview-a1204":
            sections = self._get_skyview_brief_sections(bundle, cmd, timeline)
        else:
            sections = self._get_custom_brief_sections(bundle, cmd, timeline)

        fin = cmd.financialExposure
        return TransactionBriefSchema(
            briefId=f"brief-{bundle.id}",
            bundleId=bundle.id,
            generatedAt=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            project=bundle.project,
            unit=bundle.unit,
            developer=bundle.developer,
            healthScore=bundle.health_score if bundle.health_score is not None else 74,
            riskLevel=cmd.riskLevel,
            totalFinancialExposure=fin.totalFinancialAtRiskFormatted,
            sections=sections,
        )

    def _get_skyview_brief_sections(
        self, bundle, cmd, timeline
    ) -> List[BriefSectionSchema]:
        sections: List[BriefSectionSchema] = []
        # Section 1: Transaction & Property Snapshot
        sections.append(
            BriefSectionSchema(
                sectionNumber=1,
                sectionKey="PROPERTY_SNAPSHOT",
                title="Transaction & Property Snapshot",
                summary=(
                    f"Acquisition of {bundle.unit} in {bundle.project}, developed by {bundle.developer}. "
                    f"Agreed total consideration is {cmd.financialExposure.baseConsiderationFormatted}."
                ),
                bulletPoints=[
                    f"Unit: {bundle.unit} (Floor {bundle.floor}, {bundle.tower})",
                    f"Carpet Area: {bundle.carpet_area_sqft:.0f} sq.ft (BBA Schedule A) vs {bundle.advertised_carpet_area_sqft or 1450:.0f} sq.ft advertised",
                    f"Super Area: {bundle.super_area_sqft:.0f} sq.ft",
                    f"Base Consideration: {cmd.financialExposure.baseConsiderationFormatted}",
                    f"Location: {bundle.location}",
                ],
                evidenceLineage=[
                    {
                        "document": "Allotment_Letter_Signed_A1204.pdf",
                        "page": 1,
                        "clause": "Allotment Terms",
                        "excerpt": f"Allotment of Unit {bundle.unit} in {bundle.project} for total consideration of Rs. {bundle.sale_price:,.0f}.",
                    },
                    {
                        "document": "Builder_Buyer_Agreement_SkyView_A1204.pdf",
                        "page": 4,
                        "clause": "Schedule A",
                        "excerpt": f"Specifications of the Apartment having Carpet Area of {bundle.carpet_area_sqft:.0f} sq.ft.",
                    },
                ],
            )
        )

        # Section 2: Executive Assessment & Health Rating
        sections.append(
            BriefSectionSchema(
                sectionNumber=2,
                sectionKey="EXECUTIVE_ASSESSMENT",
                title="Executive Assessment & Health Rating",
                summary=(
                    f"The transaction bundle is evaluated at an overall Health Score of {bundle.health_score}/100 ({cmd.riskLevel} Risk). "
                    "While title flow and booking terms are documented, the agreement contains significant contractual asymmetry "
                    "and unmitigated financial forfeiture risks."
                ),
                bulletPoints=[
                    f"Transaction Health Index: {bundle.health_score}/100",
                    "Primary Caveat: Delay compensation liability is severely unbalanced favoring developer (2.4% vs 18%).",
                    "Primary Caveat: Cancellation clause exposes 20% of base consideration (₹28.5L) to forfeiture.",
                    f"Total Documents Verified: {len(bundle.documents)} files ({cmd.missingDocumentsCount} checklist omissions).",
                ],
                evidenceLineage=[
                    {
                        "document": "System Audit Score",
                        "page": 1,
                        "clause": "Composite Scoring Engine",
                        "excerpt": f"Overall Health Index computed across 5 weighted risk vectors: {bundle.health_score}/100.",
                    }
                ],
            )
        )

        # Section 3: Financial Exposure Matrix
        fin = cmd.financialExposure
        sections.append(
            BriefSectionSchema(
                sectionNumber=3,
                sectionKey="FINANCIAL_EXPOSURE",
                title="Financial Exposure Matrix",
                summary=(
                    f"Total capital at risk is quantified at {fin.totalFinancialAtRiskFormatted}, including {fin.earnestMoneyForfeitRiskFormatted} "
                    f"in potential termination forfeiture and {fin.areaDiscrepancyCostImpactFormatted} in uncompensated carpet area deficit."
                ),
                bulletPoints=[
                    f"Earnest Money at Risk: {fin.earnestMoneyForfeitRiskFormatted} (20% of purchase price)",
                    f"Statutory Ceiling (RERA Sec 13): {fin.statutoryForfeitLimitFormatted} (10% max allowable advance)",
                    f"Excess Capital Exposure: {fin.excessForfeitExposureFormatted} at immediate risk upon dispute",
                    f"Monthly Late Penalty Asymmetry: {fin.monthlyAsymmetryCostFormatted} disparity between parties",
                    f"Carpet Area Valuation Deficit: {fin.areaDiscrepancyCostImpactFormatted}",
                ],
                evidenceLineage=[
                    {
                        "document": "Builder_Buyer_Agreement_SkyView_A1204.pdf",
                        "page": 11,
                        "clause": "Clause 6.1",
                        "excerpt": "In the event of cancellation by the Allottee, twenty percent (20%) of the total sale consideration shall stand forfeited as earnest money.",
                    }
                ],
            )
        )

        # Section 4: Critical Contractual Milestones
        milestone_bullets = []
        for ev in timeline.events[:4]:
            dt_str = ev.eventDate if ev.eventDate else "Milestone Dependent"
            milestone_bullets.append(f"{ev.title}: {dt_str} ({ev.dateType}) — {ev.description}")
        sections.append(
            BriefSectionSchema(
                sectionNumber=4,
                sectionKey="CONTRACTUAL_MILESTONES",
                title="Critical Contractual Milestones & Timeline",
                summary=(
                    f"Identified {timeline.totalEvents} key chronological milestones across the bundle, "
                    f"including {timeline.conflictingEventsCount} critical date conflicts between sales collateral and the contract."
                ),
                bulletPoints=milestone_bullets,
                evidenceLineage=[
                    {
                        "document": "Sales_Brochure_SkyView_Residency.pdf",
                        "page": 2,
                        "clause": "Marketing Timeline",
                        "excerpt": "Promised Handover: December 2026.",
                    },
                    {
                        "document": "Builder_Buyer_Agreement_SkyView_A1204.pdf",
                        "page": 19,
                        "clause": "Clause 11.2",
                        "excerpt": "Promoter proposes completion by 31st December 2027 plus 180 days grace period.",
                    },
                ],
            )
        )

        # Section 5: Key Discrepancies & Advertising Divergence
        sections.append(
            BriefSectionSchema(
                sectionNumber=5,
                sectionKey="DISCREPANCIES",
                title="Key Discrepancies & Advertising Divergence",
                summary=(
                    "Comparison between pre-contract marketing commitments and the formal BBA reveals 2 major discrepancies "
                    "affecting delivery timeline and apartment dimensions."
                ),
                bulletPoints=[
                    "Delivery Date Slippage: 12-month extension from marketing claim (Dec 2026) to agreement (Dec 2027 + 180-day grace).",
                    "Carpet Area Reduction: 70 sq.ft shortfall between promotional brochure (1,450 sq.ft) and Agreement (1,380 sq.ft).",
                    "Unilateral Tolerance: Clause 6.4 permits builder 3% area deviation without price adjustment.",
                ],
                evidenceLineage=[
                    {
                        "document": "Sales_Brochure_SkyView_Residency.pdf",
                        "page": 1,
                        "clause": "Unit Floor Plan Type A",
                        "excerpt": "3 BHK Luxury Carpet Area: 1,450 sq.ft | Super Area: 2,150 sq.ft.",
                    },
                    {
                        "document": "Builder_Buyer_Agreement_SkyView_A1204.pdf",
                        "page": 4,
                        "clause": "Schedule A Specification",
                        "excerpt": "Carpet Area of the Apartment is 1,380 sq.ft (128.20 sq.mtrs).",
                    },
                ],
            )
        )

        # Section 6: High-Priority Asymmetric Clauses
        sections.append(
            BriefSectionSchema(
                sectionNumber=6,
                sectionKey="ASYMMETRIC_CLAUSES",
                title="High-Priority Asymmetric Clauses",
                summary=(
                    "Forensic clause intelligence identified 3 one-sided provisions violating standard RERA model agreement principles."
                ),
                bulletPoints=[
                    "Clause 4.3 vs 8.2 (Delay Compensation): 18% buyer late charge vs ₹5/sq.ft/mo builder delay compensation.",
                    "Clause 6.1 (Cancellation Penalty): 20% forfeiture exceeds 10% statutory ceiling under RERA Section 13.",
                    "Clause 6.4 (Alteration Rights): Unilateral builder alteration right up to 10% without prior buyer written consent.",
                ],
                evidenceLineage=[
                    {
                        "document": "Builder_Buyer_Agreement_SkyView_A1204.pdf",
                        "page": 15,
                        "clause": "Clause 8.2",
                        "excerpt": "Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft. of super area per month for the period of delay.",
                    }
                ],
            )
        )

        # Section 7: Recommended Buyer Action Plan & Amendment Letter
        action_bullets = [f"{act.title} ({act.severity}): {act.recommendedAction}" for act in cmd.priorityActions[:5]]
        sections.append(
            BriefSectionSchema(
                sectionNumber=7,
                sectionKey="ACTION_PLAN",
                title="Recommended Buyer Action Plan & Amendment Draft",
                summary=(
                    "Concrete negotiation amendments to submit to the promoter prior to executing the formal agreement."
                ),
                bulletPoints=action_bullets,
                evidenceLineage=[
                    {
                        "document": "ClauseGuard Negotiation Generator",
                        "page": 1,
                        "clause": "Draft Rider to BBA",
                        "excerpt": "Draft contractual riders amending Clause 4.3, 6.1, 6.4, and 8.2 in conformity with RERA Act, 2016.",
                    }
                ],
            )
        )
        return sections

    def _get_custom_brief_sections(
        self, bundle, cmd, timeline
    ) -> List[BriefSectionSchema]:
        sections: List[BriefSectionSchema] = []
        primary_doc = bundle.documents[0].file_name if bundle.documents else "Uploaded Document"
        inconsistencies = [f for f in bundle.findings if f.finding_type == "INCONSISTENCY"]
        risks = [f for f in bundle.findings if f.finding_type == "RISK"]

        # Section 1: Transaction & Property Snapshot
        sections.append(
            BriefSectionSchema(
                sectionNumber=1,
                sectionKey="PROPERTY_SNAPSHOT",
                title="Transaction & Property Snapshot",
                summary=f"Acquisition of {bundle.unit} in {bundle.project}, developed by {bundle.developer}. Agreed total consideration is {cmd.financialExposure.baseConsiderationFormatted}.",
                bulletPoints=[
                    f"Unit: {bundle.unit} ({bundle.tower})",
                    f"Carpet Area: {bundle.carpet_area_sqft:.0f} sq.ft",
                    f"Super Area: {bundle.super_area_sqft:.0f} sq.ft",
                    f"Base Consideration: {cmd.financialExposure.baseConsiderationFormatted}",
                    f"Location: {bundle.location}",
                ],
                evidenceLineage=[
                    {
                        "document": primary_doc,
                        "page": 1,
                        "clause": "Property Schedule",
                        "excerpt": f"Unit {bundle.unit} in {bundle.project} for total consideration of Rs. {bundle.sale_price:,.0f}.",
                    }
                ],
            )
        )

        # Section 2: Executive Assessment & Health Rating
        sections.append(
            BriefSectionSchema(
                sectionNumber=2,
                sectionKey="EXECUTIVE_ASSESSMENT",
                title="Executive Assessment & Health Rating",
                summary=f"The transaction bundle is evaluated at an overall Health Score of {bundle.health_score}/100 ({cmd.riskLevel} Risk).",
                bulletPoints=[
                    f"Transaction Health Index: {bundle.health_score}/100",
                    f"Total Documents Verified: {len(bundle.documents)} files.",
                    f"Issues Detected: {len(bundle.findings)} findings across uploaded documents.",
                ],
                evidenceLineage=[
                    {
                        "document": "System Audit Score",
                        "page": 1,
                        "clause": "Composite Scoring Engine",
                        "excerpt": f"Overall Health Index: {bundle.health_score}/100.",
                    }
                ],
            )
        )

        # Section 3: Financial Exposure Matrix
        fin = cmd.financialExposure
        sections.append(
            BriefSectionSchema(
                sectionNumber=3,
                sectionKey="FINANCIAL_EXPOSURE",
                title="Financial Exposure Matrix",
                summary=f"Total capital at risk is quantified at {fin.totalFinancialAtRiskFormatted}.",
                bulletPoints=[
                    f"Base Consideration: {fin.baseConsiderationFormatted}",
                    f"Earnest Money at Risk: {fin.earnestMoneyForfeitRiskFormatted}",
                    f"Statutory Ceiling (RERA Sec 13): {fin.statutoryForfeitLimitFormatted}",
                    f"Monthly Late Penalty Asymmetry: {fin.monthlyAsymmetryCostFormatted}",
                ],
                evidenceLineage=[
                    {
                        "document": primary_doc,
                        "page": 1,
                        "clause": "Financial Terms",
                        "excerpt": f"Agreed consideration of {fin.baseConsiderationFormatted}.",
                    }
                ],
            )
        )

        # Section 4: Critical Contractual Milestones
        milestone_bullets = [
            f"{ev.title}: {ev.eventDate or 'Milestone Dependent'} ({ev.dateType}) — {ev.description}"
            for ev in timeline.events[:4]
        ] or [f"Target Possession Date: {bundle.possession_date or 'To be specified'}"]
        sections.append(
            BriefSectionSchema(
                sectionNumber=4,
                sectionKey="CONTRACTUAL_MILESTONES",
                title="Critical Contractual Milestones & Timeline",
                summary=f"Identified {timeline.totalEvents} key chronological milestones across the bundle.",
                bulletPoints=milestone_bullets,
                evidenceLineage=[
                    {
                        "document": primary_doc,
                        "page": 1,
                        "clause": "Possession Terms",
                        "excerpt": f"Target handover: {bundle.possession_date or 'Not stated'}.",
                    }
                ],
            )
        )

        # Section 5: Key Discrepancies
        discrepancy_bullets = [
            f"{f.title}: {f.description}" for f in inconsistencies[:3]
        ] or ["No cross-document discrepancies detected across current bundle documents."]
        discrepancy_lineage = [
            {
                "document": f.primary_evidence.get("documentName", primary_doc) if isinstance(f.primary_evidence, dict) else primary_doc,
                "page": f.primary_evidence.get("pageNumber", 1) if isinstance(f.primary_evidence, dict) else 1,
                "clause": f.primary_evidence.get("clauseNumber", "Discrepancy Evidence") if isinstance(f.primary_evidence, dict) else "Discrepancy Evidence",
                "excerpt": f.primary_evidence.get("excerpt", f.description) if isinstance(f.primary_evidence, dict) else f.description,
            }
            for f in inconsistencies[:2]
        ] or [{"document": primary_doc, "page": 1, "clause": "Verification", "excerpt": "No discrepancies found."}]
        sections.append(
            BriefSectionSchema(
                sectionNumber=5,
                sectionKey="DISCREPANCIES",
                title="Key Discrepancies & Document Divergence",
                summary=f"Identified {len(inconsistencies)} cross-document discrepancies in this transaction.",
                bulletPoints=discrepancy_bullets,
                evidenceLineage=discrepancy_lineage,
            )
        )

        # Section 6: High-Priority Asymmetric Clauses
        risk_bullets = [
            f"{r.title}: {r.description}" for r in risks[:3]
        ] or ["No high-priority asymmetric clauses flagged for this transaction."]
        risk_lineage = [
            {
                "document": r.primary_evidence.get("documentName", primary_doc) if isinstance(r.primary_evidence, dict) else primary_doc,
                "page": r.primary_evidence.get("pageNumber", 1) if isinstance(r.primary_evidence, dict) else 1,
                "clause": r.primary_evidence.get("clauseNumber", "Risk Clause") if isinstance(r.primary_evidence, dict) else "Risk Clause",
                "excerpt": r.primary_evidence.get("excerpt", r.description) if isinstance(r.primary_evidence, dict) else r.description,
            }
            for r in risks[:2]
        ] or [{"document": primary_doc, "page": 1, "clause": "Clause Audit", "excerpt": "No high risks detected."}]
        sections.append(
            BriefSectionSchema(
                sectionNumber=6,
                sectionKey="ASYMMETRIC_CLAUSES",
                title="High-Priority Asymmetric Clauses",
                summary=f"Identified {len(risks)} contractual risk clauses in this transaction.",
                bulletPoints=risk_bullets,
                evidenceLineage=risk_lineage,
            )
        )

        # Section 7: Action Plan
        action_bullets = [
            f"{act.title} ({act.severity}): {act.recommendedAction}" for act in cmd.priorityActions[:5]
        ] or ["Review agreement terms with qualified real estate legal counsel before signing."]
        sections.append(
            BriefSectionSchema(
                sectionNumber=7,
                sectionKey="ACTION_PLAN",
                title="Recommended Buyer Action Plan",
                summary="Actionable steps to resolve identified risks before executing binding agreements.",
                bulletPoints=action_bullets,
                evidenceLineage=[
                    {
                        "document": "ClauseGuard Audit Plan",
                        "page": 1,
                        "clause": "Pre-Execution Checklist",
                        "excerpt": "Address flagged contractual obligations and request written clarifications.",
                    }
                ],
            )
        )
        return sections

    def generate_pdf(self, brief: TransactionBriefSchema) -> bytes:
        """Renders vector-quality multi-page PDF briefing document using PyMuPDF."""
        doc = fitz.open()

        # Page 1: Sections 1-3
        p1 = doc.new_page(width=self.PAGE_WIDTH, height=self.PAGE_HEIGHT)
        self._draw_header(p1, brief)
        y = 105

        for sec in brief.sections[:3]:
            y = self._draw_section(p1, sec, y)
            y += 8

        self._draw_footer(p1, 1, 2)

        # Page 2: Sections 4-7
        p2 = doc.new_page(width=self.PAGE_WIDTH, height=self.PAGE_HEIGHT)
        self._draw_header_compact(p2, brief)
        y2 = 65

        for sec in brief.sections[3:]:
            y2 = self._draw_section(p2, sec, y2)
            y2 += 8

        self._draw_footer(p2, 2, 2)

        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def _draw_header(self, page: fitz.Page, brief: TransactionBriefSchema) -> None:
        page.draw_rect(fitz.Rect(0, 0, self.PAGE_WIDTH, 85), color=self.DARK_NAVY, fill=self.DARK_NAVY)
        page.insert_text(fitz.Point(36, 32), "CLAUSEGUARD FORENSIC BRIEF", fontsize=16, color=(1, 1, 1), fontname="helv")
        page.insert_text(fitz.Point(36, 48), f"Executive Transaction Brief: {brief.project} — {brief.unit}", fontsize=11, color=(0.8, 0.85, 0.9), fontname="helv")
        page.insert_text(fitz.Point(36, 64), f"Developer: {brief.developer} | Generated: {brief.generatedAt}", fontsize=8, color=(0.6, 0.65, 0.7), fontname="helv")

        # Health badge
        score_rect = fitz.Rect(self.PAGE_WIDTH - 110, 16, self.PAGE_WIDTH - 36, 68)
        page.draw_rect(score_rect, color=self.EMERALD, fill=(0.12, 0.16, 0.2), width=1.5)
        page.insert_text(fitz.Point(self.PAGE_WIDTH - 96, 42), f"{brief.healthScore}/100", fontsize=16, color=(1, 1, 1), fontname="helv")
        page.insert_text(fitz.Point(self.PAGE_WIDTH - 98, 56), f"RISK: {brief.riskLevel}", fontsize=7.5, color=self.AMBER, fontname="helv")

    def _draw_header_compact(self, page: fitz.Page, brief: TransactionBriefSchema) -> None:
        page.draw_rect(fitz.Rect(0, 0, self.PAGE_WIDTH, 45), color=self.DARK_NAVY, fill=self.DARK_NAVY)
        page.insert_text(fitz.Point(36, 26), f"ClauseGuard Brief — {brief.project} ({brief.unit})", fontsize=11, color=(1, 1, 1), fontname="helv")
        page.insert_text(fitz.Point(self.PAGE_WIDTH - 180, 26), f"Financial At Risk: {brief.totalFinancialExposure}", fontsize=9, color=self.ROSE, fontname="helv")

    def _draw_section(self, page: fitz.Page, sec: BriefSectionSchema, y: float) -> float:
        # Title pill
        page.draw_rect(fitz.Rect(36, y, self.PAGE_WIDTH - 36, y + 18), color=self.LIGHT_GRAY, fill=self.LIGHT_GRAY)
        page.insert_text(fitz.Point(42, y + 13), f"{sec.sectionNumber}. {sec.title.upper()}", fontsize=9, color=self.DARK_NAVY, fontname="helv")
        y += 24

        # Summary paragraph
        y = self._draw_text_wrapped(page, sec.summary, 42, y, self.PAGE_WIDTH - 72, fontsize=8.5, color=self.TEXT_DARK)
        y += 4

        # Bullet points
        for bp in sec.bulletPoints[:4]:
            page.draw_circle(fitz.Point(46, y + 4), 1.5, color=self.EMERALD, fill=self.EMERALD)
            y = self._draw_text_wrapped(page, bp, 54, y, self.PAGE_WIDTH - 90, fontsize=8, color=self.TEXT_DARK)
            y += 2

        return y

    def _draw_text_wrapped(self, page: fitz.Page, text: str, x: float, y: float, max_w: float, fontsize: float, color: tuple) -> float:
        words = text.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            # Approx character width
            if len(test_line) * (fontsize * 0.5) > max_w:
                page.insert_text(fitz.Point(x, y + fontsize), line, fontsize=fontsize, color=color, fontname="helv")
                y += fontsize + 3
                line = word
            else:
                line = test_line
        if line:
            page.insert_text(fitz.Point(x, y + fontsize), line, fontsize=fontsize, color=color, fontname="helv")
            y += fontsize + 3
        return y

    def _draw_footer(self, page: fitz.Page, current_page: int, total_pages: int) -> None:
        page.draw_line(fitz.Point(36, self.PAGE_HEIGHT - 35), fitz.Point(self.PAGE_WIDTH - 36, self.PAGE_HEIGHT - 35), color=self.LIGHT_GRAY)
        page.insert_text(
            fitz.Point(36, self.PAGE_HEIGHT - 22),
            "Confidential Forensic Brief — Prepared by ClauseGuard Transaction Intelligence Engine.",
            fontsize=7,
            color=self.TEXT_MUTED,
            fontname="helv",
        )
        page.insert_text(
            fitz.Point(self.PAGE_WIDTH - 70, self.PAGE_HEIGHT - 22),
            f"Page {current_page} of {total_pages}",
            fontsize=7,
            color=self.TEXT_MUTED,
            fontname="helv",
        )


transaction_brief_service = TransactionBriefService()
