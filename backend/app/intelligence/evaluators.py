from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import uuid
import re

from app.models.document import Document
from app.models.attribute import ExtractedAttribute
from app.models.finding import Finding
from app.intelligence.evidence_pairing import evidence_pairing_service
from app.intelligence.entity_normalizer import DateNormalizer


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
    """Detects area differences between marketing brochures, allotment letters, and agreements for the same area type."""

    def evaluate(
        self,
        bundle_id: str,
        documents: List[Document],
        attributes: List[ExtractedAttribute],
    ) -> List[Finding]:
        doc_map = {d.id: d for d in documents}
        findings: List[Finding] = []

        # Evaluate discrepancies independently per area type (do NOT mix carpet area with built-up or super area)
        for area_key, area_label in [
            ("carpet_area", "Carpet Area"),
            ("built_up_area", "Built-Up Area"),
            ("super_area", "Super Built-Up Area"),
        ]:
            area_attrs = [a for a in attributes if a.attribute_key == area_key]
            if len(area_attrs) < 2:
                continue

            found_for_key = False
            for i in range(len(area_attrs)):
                if found_for_key:
                    break
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
                                title=f"{area_label} Discrepancy",
                                description=(
                                    f"Discrepancy detected between documents: {p_name} mentions "
                                    f"{primary_attr.attribute_value}, whereas {s_name} stipulates "
                                    f"{sec_attr.attribute_value} (variance of {abs(diff):.1f} sq.ft)."
                                ),
                                impact=(
                                    f"Potential net reduction of {abs(diff):.1f} sq.ft between pre-contract "
                                    f"representations and binding agreement specifications."
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
                        found_for_key = True
                        break  # One discrepancy per area type is sufficient
        return findings


class PossessionDiscrepancyEvaluator(BaseDiscrepancyEvaluator):
    """Detects promised possession date shifts and grace period extensions between documents."""

    @staticmethod
    def _are_dates_conflicting(val1: str, prec1: str, val2: str, prec2: str) -> bool:
        if not val1 or not val2 or val1 == val2:
            return False
        p1 = "DAY" if prec1 in ("DAY", "EXACT_DATE") else ("MONTH" if prec1 in ("MONTH", "MONTH_YEAR") else prec1)
        p2 = "DAY" if prec2 in ("DAY", "EXACT_DATE") else ("MONTH" if prec2 in ("MONTH", "MONTH_YEAR") else prec2)
        if p1 == "YEAR" or p2 == "YEAR":
            return val1[:4] != val2[:4]
        if p1 == "MONTH" or p2 == "MONTH":
            return val1[:7] != val2[:7]
        return val1 != val2

    def evaluate(
        self,
        bundle_id: str,
        documents: List[Document],
        attributes: List[ExtractedAttribute],
    ) -> List[Finding]:
        doc_map = {d.id: d for d in documents}

        # 1. Filter out negated or omitted references
        possession_attrs = [
            a for a in attributes
            if a.attribute_key == "possession_date" and not DateNormalizer.is_negated_context(a.raw_excerpt)
        ]
        if len(possession_attrs) < 2:
            return []

        # Deduplicate per document
        doc_attrs: Dict[str, ExtractedAttribute] = {}
        for a in possession_attrs:
            if a.document_id not in doc_attrs:
                doc_attrs[a.document_id] = a
            else:
                existing = doc_attrs[a.document_id]
                if (a.source_clause and not existing.source_clause) or (a.confidence > existing.confidence):
                    doc_attrs[a.document_id] = a

        findings: List[Finding] = []

        # Separate contractual vs marketing
        contractual_attrs: List[ExtractedAttribute] = []
        marketing_attrs: List[ExtractedAttribute] = []

        for doc_id, attr in doc_attrs.items():
            doc = doc_map.get(doc_id)
            doc_type = (doc.document_type or "").upper() if doc else "DOCUMENT"
            doc_name = (doc.file_name or "").lower() if doc else ""
            is_marketing = (
                "BROCHURE" in doc_type or
                "brochure" in doc_name or
                "marketing" in doc_name or
                "prospectus" in doc_name
            )
            if is_marketing:
                marketing_attrs.append(attr)
            else:
                contractual_attrs.append(attr)

        # 1. Contractual vs Contractual Discrepancy (Binding Delivery Shift)
        found_contractual = False
        for i in range(len(contractual_attrs)):
            if found_contractual:
                break
            for j in range(i + 1, len(contractual_attrs)):
                p1 = contractual_attrs[i]
                p2 = contractual_attrs[j]
                if p1.document_id == p2.document_id:
                    continue

                d1_str = p1.normalized_value or ""
                d2_str = p2.normalized_value or ""
                p1_prec = getattr(p1, "precision", None) or (p1.unit.replace("date:", "") if (p1.unit and p1.unit.startswith("date:")) else ("YEAR" if len(d1_str) == 4 else "DAY"))
                p2_prec = getattr(p2, "precision", None) or (p2.unit.replace("date:", "") if (p2.unit and p2.unit.startswith("date:")) else ("YEAR" if len(d2_str) == 4 else "DAY"))

                if self._are_dates_conflicting(d1_str, p1_prec, d2_str, p2_prec):
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
                    found_contractual = True
                    break

        # 2. Marketing vs Contractual Discrepancy
        # Only flag if marketing contradicts ALL contractual milestones
        for m_attr in marketing_attrs:
            m_val = m_attr.normalized_value or ""
            m_prec = getattr(m_attr, "precision", None) or (m_attr.unit.replace("date:", "") if (m_attr.unit and m_attr.unit.startswith("date:")) else ("YEAR" if len(m_val) == 4 else "DAY"))

            if contractual_attrs:
                # Check compatibility with all contractual milestones
                compatible = any(
                    not self._are_dates_conflicting(
                        m_val,
                        m_prec,
                        c.normalized_value or "",
                        getattr(c, "precision", None) or (c.unit.replace("date:", "") if (c.unit and c.unit.startswith("date:")) else "DAY"),
                    )
                    for c in contractual_attrs
                )
                if not compatible:
                    # Marketing contradicts all contractual documents (promotional variance)
                    ref_c = min(contractual_attrs, key=lambda c: c.normalized_value or "9999")
                    m_doc = doc_map.get(m_attr.document_id)
                    c_doc = doc_map.get(ref_c.document_id)
                    m_name = m_doc.file_name if m_doc else "Marketing Document"
                    c_name = c_doc.file_name if c_doc else "Contractual Document"

                    paired = evidence_pairing_service.pair_discrepancy_evidence(
                        doc_a=m_doc,
                        attr_a=m_attr,
                        doc_b=c_doc,
                        attr_b=ref_c,
                    )
                    findings.append(
                        Finding(
                            id=f"inc-possession-mkt-{uuid.uuid4().hex[:6]}",
                            bundle_id=bundle_id,
                            finding_type="INCONSISTENCY",
                            category="POSSESSION",
                            severity="LOW",
                            title="Advertised Handover Date Variance",
                            description=(
                                f"{m_name} advertised handover by {m_attr.attribute_value} ({m_val}), "
                                f"whereas {c_name} stipulates completion by {ref_c.attribute_value} ({ref_c.normalized_value})."
                            ),
                            impact="Marketing representations reflect earlier completion projections than formal transaction instruments.",
                            recommendation_note="Verify binding RERA registration timeline against marketing claims.",
                            primary_evidence=paired["primary_evidence"],
                            secondary_evidence=paired["secondary_evidence"],
                            detected_at=datetime.utcnow(),
                        )
                    )

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
                    clean1 = re.sub(r"[^A-Za-z0-9]", "", u1.normalized_value).upper()
                    clean2 = re.sub(r"[^A-Za-z0-9]", "", u2.normalized_value).upper()
                    if clean1 and clean2 and clean1 != clean2:
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
