import pytest
import re
import fitz
from datetime import datetime
from typing import List
from httpx import AsyncClient

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

    events, conflict_summary = timeline_service._build_dynamic_timeline_events(bundle, 7_500_000.0)

    # Must contain both possession dates
    dates = [e.eventDate for e in events]
    assert "2027-06-30" in dates, "Allotment possession date missing in timeline"
    assert "2027-12-31" in dates, "BBA contractual possession date missing in timeline"
    assert "2027" in dates, "Brochure year milestone missing in timeline"

    # Conflicting dates must be marked between Allotment and BBA
    allot_event = next(e for e in events if e.eventDate == "2027-06-30")
    bba_event = next(e for e in events if e.eventDate == "2027-12-31")
    assert allot_event.conflictingDate == "2027-12-31", "Allotment should conflict with BBA 2027-12-31"
    assert bba_event.conflictingDate == "2027-06-30", "BBA should conflict with Allotment 2027-06-30"

    # Brochure has precision YEAR (2027), which is COMPATIBLE with 2027-06-30 and 2027-12-31
    broch_event = next(e for e in events if e.eventDate == "2027")
    assert broch_event.conflictingDate is None, "Year 2027 should NOT be flagged as conflicting with same-year 2027 exact dates"
    assert broch_event.precision == "YEAR"
    assert broch_event.isDerived is False
    assert broch_event.documentName == "Brochure.pdf"

    # Conflict summary must describe the genuine conflict between Allotment and Agreement, without inventing 2026
    assert conflict_summary is not None
    assert "Allotment.pdf" in conflict_summary
    assert "Agreement.pdf" in conflict_summary
    assert "2026" not in conflict_summary

    # Grace period event (2027-12-31 + 6 months = 2028-06-30)
    grace_event = next((e for e in events if "Grace Period" in e.title), None)
    assert grace_event is not None
    assert grace_event.eventDate == "2028-06-30"
    assert grace_event.dateType == "INFERRED"
    assert grace_event.isDerived is True
    assert grace_event.sourceDocument == "Agreement.pdf"

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


# ==============================================================================
# 6. UNSEEN NOVEL REAL-ESTATE TRANSACTION FULL LIFECYCLE E2E TEST
# ==============================================================================

@pytest.mark.asyncio
async def test_completely_unseen_document_e2e_workflow(client: AsyncClient):
    """
    Generalization test: Verifies that an unseen real-estate project with novel wording,
    new developer, novel unit format, and previously unseen filenames executes the
    full intelligence pipeline correctly:
    - Ingests unseen documents
    - Extracts numbered clauses
    - Detects genuine area discrepancy (2,150 vs 2,250 sq.ft.)
    - Refuses false pricing discrepancies
    - Respects document-scoped RAG queries
    - Strictly triggers anti-hallucination refusal for ungrounded queries
    - Dynamically synthesizes timeline with marketing (approximate) and contractual milestones
    """
    # 1. Build 2 novel PDFs in memory using fitz
    pdf1 = fitz.open()
    page1 = pdf1.new_page()
    text1 = '''SERENE MEADOWS LUXURY VILLAS
AGREEMENT FOR SALE AND ALLOTMENT

1. Property & Allotted Area
The Developer hereby allots Villa 14 having unit area
admeasuring 2,150 sq.ft. of carpet area in Sector 5.

2. Total Consideration
The total agreed consideration for the property is
Rupees One Crore Twenty Lakh only (INR 1,20,00,000/-).

3. Delivery of Possession
The Developer covenants to complete construction and
effect delivery of the unit by 30th September 2028.

4. Promoter Grace Period
The Promoter shall be entitled to an unconditional grace period
of 90 days from the scheduled date of delivery.
'''
    page1.insert_textbox(fitz.Rect(50, 50, 550, 750), text1, fontsize=11)
    bytes1 = pdf1.write()
    pdf1.close()

    pdf2 = fitz.open()
    page2 = pdf2.new_page()
    text2 = '''SERENE MEADOWS LUXURY RESIDENCES
OFFICIAL PROJECT BROCHURE

Exquisite private villas offering a luxurious carpet area of 2,250 sq.ft.
Target handover in 2028.
Ultra-luxury clubhouse with temperature-controlled swimming pools.
'''
    page2.insert_textbox(fitz.Rect(50, 50, 550, 750), text2, fontsize=11)
    bytes2 = pdf2.write()
    pdf2.close()

    # 2. Create novel transaction
    tx_res = await client.post('/api/v1/transactions', json={
        'projectName': 'Serene Meadows',
        'unit': 'Villa 14',
        'developer': 'Meadowlands Realty LLP',
        'city': 'Bengaluru, Karnataka',
        'approxPrice': 12000000.0,
        'carpetAreaSqFt': 2150.0,
        'superAreaSqFt': 2800.0
    })
    assert tx_res.status_code == 201
    tx_id = tx_res.json()['id']

    # 3. Upload both novel PDFs
    u1 = await client.post(
        f'/api/v1/transactions/{tx_id}/documents/upload',
        files={'file': ('Novel_Villa_Agreement.pdf', bytes1, 'application/pdf')},
        data={'document_type': 'agreement_sale', 'auto_extract_clauses': 'true'}
    )
    assert u1.status_code == 201

    u2 = await client.post(
        f'/api/v1/transactions/{tx_id}/documents/upload',
        files={'file': ('Novel_Brochure.pdf', bytes2, 'application/pdf')},
        data={'document_type': 'sales_brochure', 'auto_extract_clauses': 'true'}
    )
    assert u2.status_code == 201

    # 4. Analyze cross-document inconsistencies
    ana_res = await client.post(f'/api/v1/transactions/{tx_id}/analyze')
    assert ana_res.status_code == 200
    inconsistencies = ana_res.json().get('inconsistencies', [])

    area_inc = next((i for i in inconsistencies if i.get('category') == 'AREA'), None)
    assert area_inc is not None, 'Area discrepancy must be detected between 2150 and 2250 sq.ft'
    assert '2,150' in area_inc.get('description') or '2150' in area_inc.get('description')
    assert '2,250' in area_inc.get('description') or '2250' in area_inc.get('description')

    price_inc = next((i for i in inconsistencies if i.get('category') == 'PRICING'), None)
    assert price_inc is None, 'Matching consideration should trigger no false discrepancy'

    # 5. Index RAG
    idx_res = await client.post(f'/api/v1/transactions/{tx_id}/rag/index-all')
    assert idx_res.status_code == 200

    # 6. Scoped RAG query 1 (Villa Agreement)
    rag1 = await client.post(f'/api/v1/transactions/{tx_id}/rag/query', json={
        'query': 'What is the delivery date in the Villa Agreement?'
    })
    assert rag1.status_code == 200
    d1 = rag1.json()
    assert any('Agreement' in c.get('documentName', '') for c in d1.get('citations', []))
    assert '2028-09-30' in d1.get('answer') or 'September' in d1.get('answer')

    # Scoped RAG query 2 (Brochure)
    rag2 = await client.post(f'/api/v1/transactions/{tx_id}/rag/query', json={
        'query': 'What is the carpet area in the brochure?'
    })
    assert rag2.status_code == 200
    d2 = rag2.json()
    assert any('Brochure' in c.get('documentName', '') for c in d2.get('citations', []))
    assert '2,250' in d2.get('answer') or '2250' in d2.get('answer')

    # Anti-hallucination refusal query
    rag3 = await client.post(f'/api/v1/transactions/{tx_id}/rag/query', json={
        'query': 'What is the pet policy for dogs in the villa complex?'
    })
    assert rag3.status_code == 200
    d3 = rag3.json()
    assert d3.get('grounded') is False
    assert 'no verified mention' in d3.get('answer').lower() or 'insufficient' in d3.get('answer').lower()

    # 7. Timeline derivation
    t_res = await client.get(f'/api/v1/transactions/{tx_id}/copilot/timeline')
    assert t_res.status_code == 200
    t_data = t_res.json()
    events = t_data.get('events', [])
    assert any(ev.get('eventDate') == '2028-09-30' and ev.get('dateType') == 'CONTRACTUAL' for ev in events)
    assert any(ev.get('eventDate') == '2028' and ev.get('dateType') == 'MARKETING' for ev in events)
    # Compatible 2028 year with 2028-09-30 must produce 0 false conflicts
    assert t_data.get('conflictingEventsCount') == 0
    assert t_data.get('conflictSummary') is None


# ==============================================================================
# 8. GENERALIZED TIMELINE PRECISION, PROVENANCE & CONFLICT SUITE
# ==============================================================================

def test_generalized_timeline_precision_provenance_and_conflicts():
    """
    Exhaustive test for generalized timeline reconciliation:
    1. Year-only dates (e.g. 2029) remain YEAR precision and NEVER invent exact days.
    2. Month/Year dates (e.g. 2029-03) remain MONTH precision.
    3. Exact dates (e.g. 2029-03-31 vs 2029-09-30) detect genuine conflicts with provenance.
    4. Year-only dates within the same year do NOT conflict with exact dates.
    5. Different-year marketing dates (e.g. 2028 vs 2029) DO trigger conflicts.
    6. Derived grace periods are only derived from exact contractual dates and carry isDerived=True.
    7. Year-only contractual dates never invent an exact derived grace period day.
    """
    ts = TimelineService()

    doc_broch = Document(id="d-orchard-broch", bundle_id="b-orchard", file_name="Prospectus_The_Orchard.pdf", document_type="BROCHURE")
    doc_allot = Document(id="d-orchard-allot", bundle_id="b-orchard", file_name="Confirmation_Slip_Unit_7A.pdf", document_type="ALLOTMENT_LETTER")
    doc_sale = Document(id="d-orchard-sale", bundle_id="b-orchard", file_name="Bilateral_Sale_Agreement.pdf", document_type="BUILDER_BUYER_AGREEMENT")

    # Scenario A: Competing exact dates (March 2029 vs September 2029) + Year-only brochure (2029)
    bundle_a = TransactionBundle(
        id="b-orchard",
        title="The Orchard Acquisition",
        sale_price=12_000_000.0,
        possession_date="2029-09-30",
        grace_period_months=6,
    )
    bundle_a.documents = [doc_broch, doc_allot, doc_sale]
    bundle_a.extracted_attributes = [
        ExtractedAttribute(id="at-1", bundle_id="b-orchard", document_id="d-orchard-broch", attribute_key="possession_date", attribute_value="target 2029 handover", normalized_value="2029", unit="date:YEAR", source_page=2),
        ExtractedAttribute(id="at-2", bundle_id="b-orchard", document_id="d-orchard-allot", attribute_key="possession_date", attribute_value="31 March 2029", normalized_value="2029-03-31", unit="date:DAY", source_page=1),
        ExtractedAttribute(id="at-3", bundle_id="b-orchard", document_id="d-orchard-sale", attribute_key="possession_date", attribute_value="30 September 2029", normalized_value="2029-09-30", unit="date:DAY", source_page=8),
    ]

    events_a, summary_a = ts._build_dynamic_timeline_events(bundle_a, 12_000_000.0)

    # 1. Brochure precision & absence of false conflict
    ev_broch = next(e for e in events_a if e.documentName == "Prospectus_The_Orchard.pdf")
    assert ev_broch.eventDate == "2029"
    assert ev_broch.precision == "YEAR"
    assert ev_broch.conflictingDate is None, "Year 2029 is compatible with 2029 dates and must not conflict"
    assert ev_broch.isDerived is False
    assert "exact day not specified" in ev_broch.description

    # 2. Allotment vs Sale Agreement genuine conflict
    ev_allot = next(e for e in events_a if e.documentName == "Confirmation_Slip_Unit_7A.pdf")
    ev_sale = next(e for e in events_a if e.documentName == "Bilateral_Sale_Agreement.pdf")
    assert ev_allot.conflictingDate == "2029-09-30"
    assert "6-month delivery disparity" in ev_allot.conflictDetails
    assert ev_sale.conflictingDate == "2029-03-31"
    assert "6-month delivery disparity" in ev_sale.conflictDetails

    # 3. Dynamic conflict summary
    assert summary_a is not None
    assert "Confirmation_Slip_Unit_7A.pdf specifies 31 March 2029" in summary_a
    assert "Bilateral_Sale_Agreement.pdf stipulates 30 September 2029" in summary_a
    assert "2026" not in summary_a

    # 4. Grace period derived event
    ev_grace = next((e for e in events_a if "Grace Period" in e.title), None)
    assert ev_grace is not None
    assert ev_grace.eventDate == "2030-03-30"
    assert ev_grace.isDerived is True
    assert ev_grace.sourceDocument == "Bilateral_Sale_Agreement.pdf"

    # Scenario B: Year-only contractual date (e.g. Agreement only states 2029)
    # Must NOT derive an exact day grace period
    bundle_b = TransactionBundle(id="b-approx", title="Approximate Deal", sale_price=5_000_000.0, grace_period_months=6)
    bundle_b.documents = [doc_sale]
    bundle_b.extracted_attributes = [
        ExtractedAttribute(id="at-b", bundle_id="b-approx", document_id="d-orchard-sale", attribute_key="possession_date", attribute_value="2029", normalized_value="2029", unit="date:YEAR", source_page=3),
    ]
    events_b, summary_b = ts._build_dynamic_timeline_events(bundle_b, 5_000_000.0)
    grace_b = next((e for e in events_b if "Grace Period" in e.title), None)
    assert grace_b is None, "Must never derive an exact grace period date from a year-only contractual source"
    assert summary_b is None, "Single document with year-only date has 0 conflicts"


