import pytest
import re
from datetime import datetime
from typing import List

from app.models.document import Document
from app.models.attribute import ExtractedAttribute
from app.models.chunk import DocumentChunk
from app.intelligence.entity_normalizer import (
    AreaNormalizer,
    CurrencyNormalizer,
    DateNormalizer,
    PercentageNormalizer,
    RERANormalizer,
)
from app.intelligence.entity_extractor import (
    TransactionEntityExtractor,
    ExtractedEntity,
)
from app.intelligence.segmenter import ClauseBoundaryDetector
from app.intelligence.evaluators import (
    AreaDiscrepancyEvaluator,
    PossessionDiscrepancyEvaluator,
    PricingDiscrepancyEvaluator,
    UnitDiscrepancyEvaluator,
)
from app.rag.rag_service import TransactionRAGService
from app.rag.retriever import RankedChunkResult
from app.services.timeline_service import TimelineService
from app.models.transaction import TransactionBundle


# ==============================================================================
# 1. GENERALIZED DATE INTELLIGENCE TESTS (Phase 3)
# ==============================================================================

def test_date_intelligence_precision_preservation():
    """
    Ensures DateNormalizer strictly preserves precision:
    - DAY: '31 December 2027', '30 June 2027', '31/12/2027', '2027-12-31'
    - MONTH: 'June 2027', '12/2027'
    - YEAR: '2027' (NEVER hallucinated into 31 Dec 2027 or 31 Dec 2026)
    """
    # Exact Day Representations
    day_cases = [
        ("31 December 2027", "2027-12-31", "DAY"),
        ("31 Dec 2027", "2027-12-31", "DAY"),
        ("30 June 2027", "2027-06-30", "DAY"),
        ("30 Jun 2027", "2027-06-30", "DAY"),
        ("31/12/2027", "2027-12-31", "DAY"),
        ("30/06/2027", "2027-06-30", "DAY"),
        ("2027-12-31", "2027-12-31", "DAY"),
        ("2027-06-30", "2027-06-30", "DAY"),
        ("31-Dec-2027", "2027-12-31", "DAY"),
        ("18th day of September 2026", "2026-09-18", "DAY"),
    ]
    for raw, expected_val, expected_prec in day_cases:
        res = DateNormalizer.normalize_with_precision(raw)
        assert res is not None, f"Failed to normalize {raw}"
        assert res[0] == expected_val, f"Wrong normalized value for {raw}: got {res[0]}, expected {expected_val}"
        assert res[1] == expected_prec, f"Wrong precision for {raw}: got {res[1]}, expected {expected_prec}"

    # Month Precision
    month_cases = [
        ("June 2027", "2027-06", "MONTH"),
        ("Jun 2027", "2027-06", "MONTH"),
        ("December 2027", "2027-12", "MONTH"),
        ("06/2027", "2027-06", "MONTH"),
    ]
    for raw, expected_val, expected_prec in month_cases:
        res = DateNormalizer.normalize_with_precision(raw)
        assert res is not None, f"Failed to normalize {raw}"
        assert res[0] == expected_val
        assert res[1] == expected_prec

    # Year Precision (Anti-Hallucination Gate)
    year_cases = [
        ("target handover in 2027", "2027", "YEAR"),
        ("handover by 2028", "2028", "YEAR"),
        ("2027", "2027", "YEAR"),
    ]
    for raw, expected_val, expected_prec in year_cases:
        res = DateNormalizer.normalize_with_precision(raw)
        assert res is not None, f"Failed to normalize {raw}"
        assert res[0] == expected_val, f"Invented date for {raw}: {res[0]}"
        assert res[1] == expected_prec
        # NON-NEGOTIABLE: Never invent 31 December or 30 June for a year-only expression
        assert not res[0].endswith("-12-31"), "Illegal hallucination of exact day from year expression"
        assert not res[0].endswith("-06-30"), "Illegal hallucination of exact day from year expression"


# ==============================================================================
# 2. GENERALIZED AREA & FINANCIAL EXTRACTION (Phase 4)
# ==============================================================================

def test_area_wording_variations():
    """
    Tests diverse area terminology variations:
    'carpet area', 'RERA carpet area', 'carpet area admeasuring',
    'area of the apartment', 'unit area', 'net carpet area'.
    """
    extractor = TransactionEntityExtractor()

    phrases = [
        ("The carpet area of the unit is 1,380 sq.ft.", "1380.0"),
        ("RERA carpet area admeasuring 1,380 sq.ft.", "1380.0"),
        ("The total area of the apartment is 1380 sqft.", "1380.0"),
        ("Unit area admeasuring 1380 sft.", "1380.0"),
        ("The brochure advertises a carpet area of 1450 sq.ft.", "1450.0"),
        ("Allotted carpet area: 1380 square feet", "1380.0"),
    ]

    for text, expected in phrases:
        ents = extractor._extract_from_text(text, page_number=1, clause_number=None)
        area_ents = [e for e in ents if e.attribute_key == "carpet_area"]
        assert len(area_ents) > 0, f"Failed to extract carpet area from: '{text}'"
        assert area_ents[0].normalized_value == expected, f"Extracted {area_ents[0].normalized_value}, expected {expected}"


def test_possession_wording_variations():
    """
    Tests diverse possession phrasing:
    'possession', 'handover', 'delivery', 'expected possession',
    'date of handing over', 'scheduled handover', 'target handover'.
    """
    extractor = TransactionEntityExtractor()

    phrases = [
        ("The scheduled handover date is 31 December 2027.", "2027-12-31", "DAY"),
        ("Promoter expects delivery on or before 30 June 2027.", "2027-06-30", "DAY"),
        ("Expected possession date of 30/06/2027.", "2027-06-30", "DAY"),
        ("The date of handing over the flat is 31 Dec 2027.", "2027-12-31", "DAY"),
        ("Marketing material projects target handover in 2027.", "2027", "YEAR"),
        ("Target 2027 handover.", "2027", "YEAR"),
    ]

    for text, expected_val, expected_prec in phrases:
        ents = extractor._extract_from_text(text, page_number=1, clause_number=None)
        poss_ents = [e for e in ents if e.attribute_key == "possession_date"]
        assert len(poss_ents) > 0, f"Failed to extract possession from: '{text}'"
        assert poss_ents[0].normalized_value == expected_val, f"Wrong value for '{text}': {poss_ents[0].normalized_value}"
        assert poss_ents[0].unit == f"date:{expected_prec}", f"Wrong precision unit for '{text}': {poss_ents[0].unit}"


def test_unit_number_cleanliness_and_no_false_positives():
    """
    Guarantees English words ('substantially', 'subject', 'plans')
    are never misidentified as unit numbers.
    """
    extractor = TransactionEntityExtractor()

    # Text with potential false positive triggers
    false_pos_text = (
        "The developer may modify the apartment substantially according to statutory plans. "
        "All terms are subject to applicable conditions."
    )
    ents = extractor._extract_from_text(false_pos_text, page_number=1, clause_number=None)
    unit_ents = [e for e in ents if e.attribute_key == "unit_number"]
    assert len(unit_ents) == 0, f"False positive unit number extracted: {[u.normalized_value for u in unit_ents]}"

    # Text with genuine unit numbers in different styles
    valid_texts = [
        ("The Allottee is allotted Flat B-204 on Floor 2.", "B-204"),
        ("Apartment No. A-1204 in Tower 1", "A-1204"),
        ("Unit B - 204", "B-204"),
        ("Flat 301 in Wing C", "301"),
    ]
    for text, expected in valid_texts:
        ents = extractor._extract_from_text(text, page_number=1, clause_number=None)
        units = [e for e in ents if e.attribute_key == "unit_number"]
        assert len(units) > 0, f"Failed to extract valid unit from: '{text}'"
        assert expected in units[0].normalized_value


# ==============================================================================
# 3. CROSS-DOCUMENT VERIFICATION TESTS (Phase 6)
# ==============================================================================

def test_cross_document_conflict_detection():
    """
    Verifies that:
    1. Area 1,380 vs 1,450 sq.ft -> triggers discrepancy finding.
    2. Possession 30 June 2027 vs 31 Dec 2027 -> triggers discrepancy finding.
    3. Consideration ₹75,00,000 across multiple documents -> NO false discrepancy.
    4. Unit B-204 across multiple documents -> NO false discrepancy.
    """
    doc_allot = Document(id="d-allot", bundle_id="b-gen", file_name="Custom_Allotment.pdf", document_type="ALLOTMENT_LETTER")
    doc_bba = Document(id="d-bba", bundle_id="b-gen", file_name="Custom_Agreement.pdf", document_type="BUILDER_BUYER_AGREEMENT")
    doc_broch = Document(id="d-broch", bundle_id="b-gen", file_name="Custom_Brochure.pdf", document_type="BROCHURE")
    docs = [doc_allot, doc_bba, doc_broch]

    # 1. Area discrepancy: Brochure 1450 vs Agreement 1380
    area_attrs = [
        ExtractedAttribute(id="a1", bundle_id="b-gen", document_id="d-broch", attribute_key="carpet_area", attribute_value="1,450 sq.ft", normalized_value="1450.0", unit="sq.ft", source_page=1),
        ExtractedAttribute(id="a2", bundle_id="b-gen", document_id="d-bba", attribute_key="carpet_area", attribute_value="1,380 sq.ft", normalized_value="1380.0", unit="sq.ft", source_page=2),
    ]
    area_eval = AreaDiscrepancyEvaluator()
    area_findings = area_eval.evaluate("b-gen", docs, area_attrs)
    assert len(area_findings) == 1
    assert area_findings[0].category == "AREA"
    assert ("1,450" in area_findings[0].description or "1450" in area_findings[0].description) and ("1,380" in area_findings[0].description or "1380" in area_findings[0].description)

    # 2. Possession discrepancy: Allotment (2027-06-30) vs BBA (2027-12-31)
    poss_attrs = [
        ExtractedAttribute(id="p1", bundle_id="b-gen", document_id="d-allot", attribute_key="possession_date", attribute_value="30 June 2027", normalized_value="2027-06-30", unit="date:DAY", source_page=1),
        ExtractedAttribute(id="p2", bundle_id="b-gen", document_id="d-bba", attribute_key="possession_date", attribute_value="31 December 2027", normalized_value="2027-12-31", unit="date:DAY", source_page=3),
        ExtractedAttribute(id="p3", bundle_id="b-gen", document_id="d-broch", attribute_key="possession_date", attribute_value="2027", normalized_value="2027", unit="date:YEAR", source_page=1),
    ]
    poss_eval = PossessionDiscrepancyEvaluator()
    poss_findings = poss_eval.evaluate("b-gen", docs, poss_attrs)
    assert len(poss_findings) == 1
    assert poss_findings[0].category == "POSSESSION"
    assert "Promised Possession Date Shift" in poss_findings[0].title
    assert "2027-06-30" in poss_findings[0].description and "2027-12-31" in poss_findings[0].description

    # 3. Consideration match: ₹75,00,000 across documents -> NO discrepancy
    price_attrs = [
        ExtractedAttribute(id="pr1", bundle_id="b-gen", document_id="d-allot", attribute_key="total_price", attribute_value="₹ 75,00,000", normalized_value="7500000.0", unit="INR", source_page=1),
        ExtractedAttribute(id="pr2", bundle_id="b-gen", document_id="d-bba", attribute_key="total_price", attribute_value="₹ 75,00,000", normalized_value="7500000.0", unit="INR", source_page=2),
    ]
    price_eval = PricingDiscrepancyEvaluator()
    price_findings = price_eval.evaluate("b-gen", docs, price_attrs)
    assert len(price_findings) == 0, "False pricing discrepancy triggered when amounts are equal!"

    # 4. Unit match: B-204 across documents -> NO discrepancy
    unit_attrs = [
        ExtractedAttribute(id="u1", bundle_id="b-gen", document_id="d-allot", attribute_key="unit_number", attribute_value="Flat B-204", normalized_value="B-204", source_page=1),
        ExtractedAttribute(id="u2", bundle_id="b-gen", document_id="d-bba", attribute_key="unit_number", attribute_value="Unit B - 204", normalized_value="B-204", source_page=1),
    ]
    unit_eval = UnitDiscrepancyEvaluator()
    unit_findings = unit_eval.evaluate("b-gen", docs, unit_attrs)
    assert len(unit_findings) == 0, "False unit mismatch triggered when unit IDs match!"


# ==============================================================================
# 4. DOCUMENT-SCOPED RAG & ANTI-HALLUCINATION TESTS (Phase 5 & 8)
# ==============================================================================

def test_rag_target_document_identification():
    """
    Verifies that user queries specifying a document target are correctly scoped.
    """
    rag_service = TransactionRAGService()

    doc_allot = Document(id="d-allot", bundle_id="b-1", file_name="03_Allotment_Letter.pdf", document_type="ALLOTMENT_LETTER")
    doc_bba = Document(id="d-bba", bundle_id="b-1", file_name="01_Builder_Buyer_Agreement.pdf", document_type="BUILDER_BUYER_AGREEMENT")
    doc_broch = Document(id="d-broch", bundle_id="b-1", file_name="05_Marketing_Brochure.pdf", document_type="BROCHURE")
    all_docs = [doc_allot, doc_bba, doc_broch]

    # Query 1: Single document (Allotment)
    t1 = rag_service._identify_target_documents("What is the possession date in the Allotment Letter?", all_docs)
    assert len(t1) == 1
    assert t1[0].id == "d-allot"

    # Query 2: Single document (BBA)
    t2 = rag_service._identify_target_documents("What is the possession date in the BBA?", all_docs)
    assert len(t2) == 1
    assert t2[0].id == "d-bba"

    # Query 3: Multi-document scope (BBA and Allotment)
    t3 = rag_service._identify_target_documents("What are the possession dates in the BBA and Allotment Letter?", all_docs)
    assert len(t3) == 2
    ids = {d.id for d in t3}
    assert "d-allot" in ids and "d-bba" in ids

    # Query 4: General query (no specific document)
    t4 = rag_service._identify_target_documents("What is the possession date?", all_docs)
    assert len(t4) == 0


def test_rag_anti_hallucination_guardrail():
    """
    Tests strict refusal when evidence is absent (e.g. swimming pool, helipad).
    """
    rag_service = TransactionRAGService()

    # Mock chunk about legal delay compensation
    chunk = DocumentChunk(
        id="c1",
        bundle_id="b-1",
        document_id="d-1",
        page_number=1,
        chunk_text="In the event of delay, promoter shall pay compensation at Rs. 5 per sq.ft per month.",
    )
    # Low dense score (0.10) and 0 lexical overlap
    fake_result = RankedChunkResult(
        chunk=chunk,
        dense_score=0.10,
        lexical_score=0.0,
        rrf_score=0.01,
        combined_confidence=0.15,
    )

    is_grounded = rag_service._verify_grounding("What is the Olympic swimming pool size?", [fake_result])
    assert is_grounded is False, "Anti-hallucination guardrail failed: accepted absent topic"

    refusal = rag_service._refusal_response("What is the Olympic swimming pool size?", "b-1")
    assert refusal.grounded is False
    assert refusal.status == "INSUFFICIENT_EVIDENCE"
    assert "no verified mention" in refusal.answer


# ==============================================================================
# 5. DYNAMIC TIMELINE GENERATION TESTS (Phase 7)
# ==============================================================================

def test_dynamic_timeline_generation():
    """
    Tests that TimelineService builds dynamic milestones with full provenance
    and marks conflicting dates when competing milestones exist.
    """
    timeline_service = TimelineService()

    doc_allot = Document(id="d-allot", bundle_id="b-dyn", file_name="Allotment.pdf", document_type="ALLOTMENT_LETTER")
    doc_bba = Document(id="d-bba", bundle_id="b-dyn", file_name="Agreement.pdf", document_type="BUILDER_BUYER_AGREEMENT")
    doc_broch = Document(id="d-broch", bundle_id="b-dyn", file_name="Brochure.pdf", document_type="BROCHURE")

    bundle = TransactionBundle(
        id="b-dyn",
        title="Custom Transaction Bundle",
        sale_price=7_500_000.0,
        possession_date="2027-12-31",
        grace_period_months=6,
    )
    bundle.documents = [doc_allot, doc_bba, doc_broch]
    bundle.extracted_attributes = [
        ExtractedAttribute(id="a1", bundle_id="b-dyn", document_id="d-allot", attribute_key="possession_date", attribute_value="30 June 2027", normalized_value="2027-06-30", unit="date:DAY", source_page=1),
        ExtractedAttribute(id="a2", bundle_id="b-dyn", document_id="d-bba", attribute_key="possession_date", attribute_value="31 December 2027", normalized_value="2027-12-31", unit="date:DAY", source_page=3),
        ExtractedAttribute(id="a3", bundle_id="b-dyn", document_id="d-broch", attribute_key="possession_date", attribute_value="2027", normalized_value="2027", unit="date:YEAR", source_page=1),
    ]

    events = timeline_service._build_dynamic_timeline_events(bundle, 7_500_000.0)

    # Must contain both possession dates
    dates = [e.eventDate for e in events]
    assert "2027-06-30" in dates, "Allotment possession date missing in timeline"
    assert "2027-12-31" in dates, "BBA contractual possession date missing in timeline"
    assert "2027" in dates, "Brochure year milestone missing in timeline"

    # Conflicting dates must be marked
    allot_event = next(e for e in events if e.eventDate == "2027-06-30")
    bba_event = next(e for e in events if e.eventDate == "2027-12-31")
    assert allot_event.conflictingDate is not None, "Conflicting date not flagged on Allotment event"
    assert bba_event.conflictingDate is not None, "Conflicting date not flagged on BBA event"

    # Grace period event (2027-12-31 + 6 months = 2028-06-30)
    grace_event = next((e for e in events if "Grace Period" in e.title), None)
    assert grace_event is not None
    assert grace_event.eventDate == "2028-06-30"
    assert grace_event.dateType == "INFERRED"

    # Uncertain final milestone
    uncertain_event = next((e for e in events if e.dateType == "UNCERTAIN"), None)
    assert uncertain_event is not None
    assert uncertain_event.eventDate is None


# ==============================================================================
# 6. FIVE-PDF SYNTHETIC REGRESSION TEST (Phase 12)
# ==============================================================================

def test_five_synthetic_pdfs_regression():
    """
    Mandatory Phase 12 Regression Suite on the 5 synthetic PDFs:
    - 01_Builder_Buyer_Agreement.pdf
    - 02_Sale_Agreement.pdf
    - 03_Allotment_Letter.pdf
    - 04_Payment_Schedule.pdf
    - 05_Marketing_Brochure.pdf

    Expected:
    - BBA: Area = 1,380 sq.ft., Possession = 31 Dec 2027
    - Allotment: Possession = 30 Jun 2027
    - Brochure: Area = 1,450 sq.ft., Target handover = 2027 (YEAR precision)
    - Payment: Consideration = ₹75,00,000
    - Area Discrepancy: YES
    - Possession Discrepancy: YES
    - Consideration False Discrepancy: NO
    - Unit False Discrepancy: NO
    - Invented 31 Dec 2026: NEVER
    - Invented exact brochure date: NEVER
    """
    from pathlib import Path
    from app.ingestion.extractors.digital_pdf import DigitalPDFExtractor

    pdf_files = [
        ("bba", "01_Builder_Buyer_Agreement.pdf", Path("data/uploads/e7ed6da0e7_01_Builder_Buyer_Agreement.pdf"), "BUILDER_BUYER_AGREEMENT"),
        ("sale", "02_Sale_Agreement.pdf", Path("data/uploads/1af84f0706_02_Sale_Agreement.pdf"), "SALE_AGREEMENT"),
        ("allot", "03_Allotment_Letter.pdf", Path("data/uploads/37ec5056a3_03_Allotment_Letter.pdf"), "ALLOTMENT_LETTER"),
        ("sched", "04_Payment_Schedule.pdf", Path("data/uploads/4fa6c989b3_04_Payment_Schedule.pdf"), "PAYMENT_SCHEDULE"),
        ("broch", "05_Marketing_Brochure.pdf", Path("data/uploads/8ad20a7639_05_Marketing_Brochure.pdf"), "BROCHURE"),
    ]

    extractor = DigitalPDFExtractor()
    segmenter = ClauseBoundaryDetector()
    entity_extractor = TransactionEntityExtractor()

    all_docs = []
    all_attrs = []
    extracted_by_doc = {}

    for doc_id, fname, fpath, dtype in pdf_files:
        if not fpath.exists():
            pytest.skip(f"Test fixture not found: {fpath}")

        doc = Document(id=doc_id, bundle_id="tx-regression", file_name=fname, document_type=dtype)
        all_docs.append(doc)

        res = extractor.extract_document(fpath)
        page_tuples = [(p.page_number, p.normalized_text) for p in res.pages]
        chunks = segmenter.segment_pages(page_tuples)

        # Ensure numbered clause headings are recognized
        assert len(chunks) == 7, f"{fname} expected 7 segmented clauses, got {len(chunks)}"

        ents = entity_extractor.extract_from_clauses_and_pages(page_tuples, chunks)
        extracted_by_doc[doc_id] = {e.attribute_key: e for e in ents}

        for e in ents:
            all_attrs.append(
                ExtractedAttribute(
                    id=f"{doc_id}-{e.attribute_key}",
                    bundle_id="tx-regression",
                    document_id=doc_id,
                    attribute_key=e.attribute_key,
                    attribute_value=e.attribute_value,
                    normalized_value=e.normalized_value,
                    unit=e.unit,
                    source_page=e.source_page,
                    source_clause=e.source_clause,
                    raw_excerpt=e.raw_excerpt,
                )
            )

    # 1. BBA verification
    bba_facts = extracted_by_doc["bba"]
    assert bba_facts["carpet_area"].normalized_value == "1380.0"
    assert bba_facts["possession_date"].normalized_value == "2027-12-31"
    assert bba_facts["possession_date"].unit == "date:DAY"
    assert bba_facts["total_price"].normalized_value == "7500000.0"
    assert bba_facts["unit_number"].normalized_value == "B-204"

    # 2. Allotment Letter verification
    allot_facts = extracted_by_doc["allot"]
    assert allot_facts["carpet_area"].normalized_value == "1380.0"
    assert allot_facts["possession_date"].normalized_value == "2027-06-30"
    assert allot_facts["possession_date"].unit == "date:DAY"
    assert allot_facts["total_price"].normalized_value == "7500000.0"
    assert allot_facts["unit_number"].normalized_value == "B-204"

    # 3. Marketing Brochure verification
    broch_facts = extracted_by_doc["broch"]
    assert broch_facts["carpet_area"].normalized_value == "1450.0"
    assert broch_facts["possession_date"].normalized_value == "2027"
    assert broch_facts["possession_date"].unit == "date:YEAR"
    # Never hallucinate exact date from brochure
    assert broch_facts["possession_date"].normalized_value != "2027-12-31"
    assert broch_facts["possession_date"].normalized_value != "2026-12-31"

    # 4. Cross-document discrepancy evaluations
    area_findings = AreaDiscrepancyEvaluator().evaluate("tx-regression", all_docs, all_attrs)
    assert len(area_findings) == 1, "Expected exactly 1 carpet area discrepancy finding"
    assert area_findings[0].category == "AREA"
    assert "70.0 sq.ft" in area_findings[0].description

    poss_findings = PossessionDiscrepancyEvaluator().evaluate("tx-regression", all_docs, all_attrs)
    assert len(poss_findings) == 1, "Expected exactly 1 possession date shift finding"
    assert poss_findings[0].category == "POSSESSION"
    assert "2027-06-30" in poss_findings[0].description and "2027-12-31" in poss_findings[0].description

    price_findings = PricingDiscrepancyEvaluator().evaluate("tx-regression", all_docs, all_attrs)
    assert len(price_findings) == 0, f"False pricing discrepancy detected: {price_findings}"

    unit_findings = UnitDiscrepancyEvaluator().evaluate("tx-regression", all_docs, all_attrs)
    assert len(unit_findings) == 0, f"False unit number discrepancy detected: {unit_findings}"

