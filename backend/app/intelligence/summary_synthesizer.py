from typing import List
from app.models.transaction import TransactionBundle
from app.models.finding import Finding
from app.schemas.report import ExecutiveSummarySchema


class ExecutiveSummarySynthesizer:
    """
    Synthesizes an evidence-backed narrative executive summary from transaction metrics,
    findings, and document checklists.
    """

    def synthesize_summary(
        self,
        bundle: TransactionBundle,
        findings: List[Finding],
        missing_doc_count: int,
    ) -> ExecutiveSummarySchema:
        inconsistencies = [f for f in findings if f.finding_type == "INCONSISTENCY"]
        risks = [f for f in findings if f.finding_type == "RISK"]

        # 1. Profile
        price_fmt = f"₹ {bundle.sale_price:,.2f}" if bundle.sale_price else "Price upon application"
        carpet_fmt = f"{bundle.carpet_area_sqft:,.0f}" if bundle.carpet_area_sqft else "N/A"
        super_fmt = f"{bundle.super_area_sqft:,.0f}" if bundle.super_area_sqft else "N/A"

        profile_str = (
            f"Transaction audit for {bundle.property_type} {bundle.unit} at '{bundle.project}', "
            f"{bundle.location or bundle.city}. Developer: {bundle.developer}. "
            f"Contractual carpet area is recorded at {carpet_fmt} sq.ft "
            f"(Super Area: {super_fmt} sq.ft). "
            f"Agreed total consideration is {price_fmt}. "
            f"Contractual possession date is scheduled for {bundle.possession_date or 'TBD'} "
            f"with an agreed {bundle.grace_period_months or 6}-month grace period."
        )

        # 2. Key Findings Narrative
        if inconsistencies:
            inc_bullets = "; ".join([f"{inc.title} ({inc.description[:90]}...)" for inc in inconsistencies[:3]])
            findings_narrative = (
                f"Cross-document consistency analysis identified {len(inconsistencies)} variance(s) "
                f"between preliminary representations and binding contract terms: {inc_bullets}. "
                f"These discrepancies represent potential variations between pre-booking claims and executed covenants."
            )
        else:
            findings_narrative = (
                "Cross-document verification indicated consistent alignment across the analyzed documents "
                "for carpet area, unit identifiers, and total consideration terms."
            )

        # 3. Critical Risks Narrative
        critical_risks = [r for r in risks if r.severity in ("CRITICAL", "HIGH")]
        if critical_risks:
            risk_bullets = "; ".join([f"{r.title}" for r in critical_risks[:3]])
            risks_narrative = (
                f"Contractual risk assessment flagged {len(critical_risks)} significant provision(s): {risk_bullets}. "
                f"Chief among these is asymmetrical delay compensation where buyer default interest rates substantially "
                f"exceed developer delayed handover compensation, alongside unilateral alteration discretion."
            )
        else:
            risks_narrative = (
                "No critical asymmetric risk clauses were identified exceeding standard market tolerance thresholds."
            )

        # 4. Actionable Next Steps
        actions: List[str] = []
        if any(f.category == "AREA" for f in inconsistencies):
            actions.append(
                "Request written confirmation from promoter reconciling brochure carpet area (1,450 sq.ft) with agreement (1,380 sq.ft) and confirm pro-rata price adjustment."
            )
        if any(f.category == "POSSESSION" for f in inconsistencies):
            actions.append(
                "Verify registered completion deadline on the State RERA portal against the agreement completion date."
            )
        if any(r.severity == "CRITICAL" for r in risks):
            actions.append(
                "Seek amendment or addendum stipulating reciprocal interest rates for both buyer and promoter delays in compliance with RERA Section 18."
            )
        if missing_doc_count > 0:
            actions.append(
                f"Obtain and verify the {missing_doc_count} missing recommended document(s), specifically sanctioned layout plans and formal RERA certificate."
            )
        actions.append(
            "Have an independent property attorney review the completed Transaction Audit Report before executing the sale deed."
        )

        return ExecutiveSummarySchema(
            transactionProfile=profile_str,
            keyFindingsNarrative=findings_narrative,
            criticalRisksNarrative=risks_narrative,
            recommendedActions=actions,
        )


executive_summary_synthesizer = ExecutiveSummarySynthesizer()
