from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import uuid

from app.models.document import Document
from app.models.attribute import ExtractedAttribute
from app.models.finding import Finding
from app.intelligence.evidence_pairing import evidence_pairing_service


class BaseDiscrepancyEvaluator:
    """Base class for deterministic cross-document discrepancy evaluators."""

    def evaluate(
        self,
        bundle_id: str,
        documents: List[Document],
        attributes: List[ExtractedAttribute],
    ) -> List[Finding]:
        raise NotImplementedError


class AreaDiscrepancyEvaluator(BaseDiscrepancyEvaluator):
    """Detects carpet area differences between marketing brochures, allotment letters, and agreements."""

    def evaluate(
        self,
        bundle_id: str,
        documents: List[Document],
        attributes: List[ExtractedAttribute],
    ) -> List[Finding]:
        doc_map = {d.id: d for d in documents}
        area_attrs = [a for a in attributes if a.attribute_key == "carpet_area"]
        if len(area_attrs) < 2:
            return []

        findings: List[Finding] = []

        # Compare pairs across different documents
        for i in range(len(area_attrs)):
            for j in range(i + 1, len(area_attrs)):
                a1 = area_attrs[i]
                a2 = area_attrs[j]
                if a1.document_id == a2.document_id:
                    continue

                try:
                    val1 = float(a1.normalized_value)
                    val2 = float(a2.normalized_value)
                except (ValueError, TypeError):
                    continue

                diff = val1 - val2
                if abs(diff) > 5.0:  # Tolerance: 5 sq.ft
                    doc1 = doc_map.get(a1.document_id)
                    doc2 = doc_map.get(a2.document_id)

                    # Put brochure or allotment first as primary, agreement as secondary
                    if doc2 and "AGREEMENT" in (doc2.document_type or "").upper():
                        primary_attr, sec_attr = a1, a2
                        primary_doc, sec_doc = doc1, doc2
                    else:
                        primary_attr, sec_attr = a2, a1
                        primary_doc, sec_doc = doc2, doc1

                    paired_evidence = evidence_pairing_service.pair_discrepancy_evidence(
                        doc_a=primary_doc,
                        attr_a=primary_attr,
                        doc_b=sec_doc,
                        attr_b=sec_attr,
                    )

                    p_name = primary_doc.file_name if primary_doc else "Primary Document"
                    s_name = sec_doc.file_name if sec_doc else "Agreement Document"

                    findings.append(
                        Finding(
                            id=f"inc-area-{uuid.uuid4().hex[:6]}",
                            bundle_id=bundle_id,
                            finding_type="INCONSISTENCY",
                            category="AREA",
                            severity="HIGH",
                            title="Carpet Area Discrepancy",
                            description=(
                                f"Discrepancy detected between documents: {p_name} mentions "
                                f"{primary_attr.attribute_value}, whereas {s_name} stipulates "
                                f"{sec_attr.attribute_value} (variance of {abs(diff):.1f} sq.ft)."
                            ),
                            impact=(
                                f"Potential net reduction of {abs(diff):.1f} sq.ft between pre-contract "
                                f"marketing/allotment representations and binding agreement specifications."
                            ),
                            recommendation_note=(
                                "Under RERA provisions, allottees pay strictly for carpet area. "
                                "Request written clarification whether total consideration will be adjusted."
                            ),
                            primary_evidence=paired_evidence["primary_evidence"],
                            secondary_evidence=paired_evidence["secondary_evidence"],
                            detected_at=datetime.utcnow(),
                        )
                    )
                    # Once a major discrepancy is flagged for carpet area, stop to avoid duplicate pairs
                    return findings

        return findings


class PossessionDiscrepancyEvaluator(BaseDiscrepancyEvaluator):
    """Detects promised possession date shifts and grace period extensions between documents."""

    def evaluate(
        self,
        bundle_id: str,
        documents: List[Document],
        attributes: List[ExtractedAttribute],
    ) -> List[Finding]:
        doc_map = {d.id: d for d in documents}
        possession_attrs = [a for a in attributes if a.attribute_key == "possession_date"]
        if len(possession_attrs) < 2:
            return []

        findings: List[Finding] = []

        for i in range(len(possession_attrs)):
            for j in range(i + 1, len(possession_attrs)):
                p1 = possession_attrs[i]
                p2 = possession_attrs[j]
                if p1.document_id == p2.document_id:
                    continue

                d1_str = p1.normalized_value
                d2_str = p2.normalized_value

                if d1_str and d2_str and d1_str != d2_str:
                    doc1 = doc_map.get(p1.document_id)
                    doc2 = doc_map.get(p2.document_id)

                    # Order: earlier promised date as primary, later contract date as secondary
                    if d1_str < d2_str:
                        primary_p, sec_p = p1, p2
                        primary_doc, sec_doc = doc1, doc2
                    else:
                        primary_p, sec_p = p2, p1
                        primary_doc, sec_doc = doc2, doc1

                    paired = evidence_pairing_service.pair_discrepancy_evidence(
                        doc_a=primary_doc,
                        attr_a=primary_p,
                        doc_b=sec_doc,
                        attr_b=sec_p,
                    )

                    p_name = primary_doc.file_name if primary_doc else "Allotment Letter"
                    s_name = sec_doc.file_name if sec_doc else "Builder-Buyer Agreement"

                    findings.append(
                        Finding(
                            id=f"inc-possession-{uuid.uuid4().hex[:6]}",
                            bundle_id=bundle_id,
                            finding_type="INCONSISTENCY",
                            category="POSSESSION",
                            severity="MEDIUM",
                            title="Promised Possession Date Shift",
                            description=(
                                f"{p_name} projects handover by {primary_p.attribute_value} ({primary_p.normalized_value}), "
                                f"but {s_name} postpones completion to {sec_p.attribute_value} ({sec_p.normalized_value})."
                            ),
                            impact=(
                                f"Handover timeline extended beyond initial commitment. "
                                f"Delays physical occupancy and impacts home loan EMI/rent planning."
                            ),
                            recommendation_note=(
                                "Verify registered completion milestone on state RERA web portal. "
                                "Check if grace period compensation applies from the earlier date."
                            ),
                            primary_evidence=paired["primary_evidence"],
                            secondary_evidence=paired["secondary_evidence"],
                            detected_at=datetime.utcnow(),
                        )
                    )
                    return findings

        return findings


class PricingDiscrepancyEvaluator(BaseDiscrepancyEvaluator):
    """Detects total price or consideration discrepancies between allotment letters and agreements."""

    def evaluate(
        self,
        bundle_id: str,
        documents: List[Document],
        attributes: List[ExtractedAttribute],
    ) -> List[Finding]:
        doc_map = {d.id: d for d in documents}
        price_attrs = [a for a in attributes if a.attribute_key == "total_price"]
        if len(price_attrs) < 2:
            return []

        findings: List[Finding] = []

        for i in range(len(price_attrs)):
            for j in range(i + 1, len(price_attrs)):
                pr1 = price_attrs[i]
                pr2 = price_attrs[j]
                if pr1.document_id == pr2.document_id:
                    continue

                try:
                    val1 = float(pr1.normalized_value)
                    val2 = float(pr2.normalized_value)
                except (ValueError, TypeError):
                    continue

                diff = val1 - val2
                if abs(diff) > 1000.0:  # Discrepancy > ₹1,000
                    doc1 = doc_map.get(pr1.document_id)
                    doc2 = doc_map.get(pr2.document_id)

                    paired = evidence_pairing_service.pair_discrepancy_evidence(
                        doc_a=doc1,
                        attr_a=pr1,
                        doc_b=doc2,
                        attr_b=pr2,
                    )

                    findings.append(
                        Finding(
                            id=f"inc-price-{uuid.uuid4().hex[:6]}",
                            bundle_id=bundle_id,
                            finding_type="INCONSISTENCY",
                            category="PRICING",
                            severity="HIGH",
                            title="Total Consideration Mismatch",
                            description=(
                                f"Total price difference of ₹ {abs(diff):,.2f} detected between "
                                f"{doc1.file_name if doc1 else 'Doc 1'} (₹ {val1:,.2f}) and "
                                f"{doc2.file_name if doc2 else 'Doc 2'} (₹ {val2:,.2f})."
                            ),
                            impact="Unexplained financial cost inflation between preliminary allotment and final agreement.",
                            recommendation_note="Request an itemized breakdown reconciling base price, parking, PLC, GST, and maintenance deposits.",
                            primary_evidence=paired["primary_evidence"],
                            secondary_evidence=paired["secondary_evidence"],
                            detected_at=datetime.utcnow(),
                        )
                    )
                    return findings

        return findings


class UnitDiscrepancyEvaluator(BaseDiscrepancyEvaluator):
    """Detects unit or tower number discrepancies across documents."""

    def evaluate(
        self,
        bundle_id: str,
        documents: List[Document],
        attributes: List[ExtractedAttribute],
    ) -> List[Finding]:
        doc_map = {d.id: d for d in documents}
        unit_attrs = [a for a in attributes if a.attribute_key == "unit_number"]
        if len(unit_attrs) < 2:
            return []

        findings: List[Finding] = []
        for i in range(len(unit_attrs)):
            for j in range(i + 1, len(unit_attrs)):
                u1 = unit_attrs[i]
                u2 = unit_attrs[j]
                if u1.document_id == u2.document_id:
                    continue

                if u1.normalized_value and u2.normalized_value:
                    if u1.normalized_value != u2.normalized_value:
                        doc1 = doc_map.get(u1.document_id)
                        doc2 = doc_map.get(u2.document_id)
                        paired = evidence_pairing_service.pair_discrepancy_evidence(
                            doc_a=doc1, attr_a=u1, doc_b=doc2, attr_b=u2
                        )
                        findings.append(
                            Finding(
                                id=f"inc-unit-{uuid.uuid4().hex[:6]}",
                                bundle_id=bundle_id,
                                finding_type="INCONSISTENCY",
                                category="SPECIFICATION",
                                severity="CRITICAL",
                                title="Unit Number Mismatch",
                                description=(
                                    f"Different unit numbers identified: {u1.attribute_value} vs {u2.attribute_value}."
                                ),
                                impact="Severe legal ambiguity regarding the physical property being purchased.",
                                recommendation_note="Immediately halt signing until exact apartment identifier is rectified in all documents.",
                                primary_evidence=paired["primary_evidence"],
                                secondary_evidence=paired["secondary_evidence"],
                                detected_at=datetime.utcnow(),
                            )
                        )
                        return findings
        return findings
