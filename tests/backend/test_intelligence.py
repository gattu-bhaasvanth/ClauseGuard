import pytest
from pathlib import Path
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document, DocumentPage
from app.models.clause import Clause
from app.intelligence.taxonomy import ClauseCategory
from app.intelligence.segmenter import ClauseBoundaryDetector
from app.intelligence.classifier import ClauseClassifier
from app.intelligence.obligation_extractor import ObligationExtractor
from app.intelligence.clause_engine import clause_intelligence_engine


@pytest.fixture
def samples_dir():
    return Path(__file__).resolve().parent.parent.parent / "data" / "samples"


# ==============================================================================
# 1. CLAUSE BOUNDARY DETECTOR TESTS
# ==============================================================================


def test_clause_boundary_detector_standard_headers():
    detector = ClauseBoundaryDetector()

    pages = [
        (
            1,
            "PREAMBLE\nThis agreement is made between Developer and Allottee.\n\n"
            "ARTICLE IV: MEASUREMENT & SPECIFICATIONS\n"
            "The following specifications shall govern the unit.\n\n"
            "Clause 4.1: Permissible Variation in Carpet Area\n"
            "The Allottee agrees that the Apartment has a RERA Carpet Area of 1,380 sq. ft.\n"
            "The Promoter reserves the right to make variations of up to ±3%.\n",
        ),
        (
            2,
            "ARTICLE V - PAYMENT TERMS & DEFAULT\n"
            "Clause 5.3: Delayed Payment Interest Rate\n"
            "If the Allottee fails to pay any installment on or before the due date, the Allottee\n"
            "shall be liable to pay interest on delayed payment at the rate of 18% per annum compounded monthly.\n\n"
            "8.2. Delayed Possession Compensation\n"
            "In the event of delay in offering possession of the Apartment beyond the agreed date,\n"
            "the Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft.\n\n"
            "SCHEDULE A: SPECIFICATIONS OF FINISHES\n"
            "Vitrified tiles in living room, wooden laminate in master bedroom.\n",
        ),
    ]

    chunks = detector.segment_pages(pages)
    assert len(chunks) >= 5

    clause_nums = [c.clause_number for c in chunks]
    assert "Article IV" in clause_nums
    assert "Clause 4.1" in clause_nums
    assert "Article V" in clause_nums
    assert "Clause 5.3" in clause_nums
    assert "Clause 8.2" in clause_nums
    assert "Schedule A" in clause_nums

    # Verify chunk structure
    c41 = next(c for c in chunks if c.clause_number == "Clause 4.1")
    assert "Permissible Variation" in c41.title
    assert c41.page_number == 1
    assert "1,380 sq. ft." in c41.full_excerpt
    assert len(c41.preview_text) > 0


def test_clause_boundary_detector_unstructured_fallback():
    detector = ClauseBoundaryDetector()

    # Document without any formal clause headers (e.g. casual letter)
    pages = [
        (1, "Dear Sir, regarding our discussion yesterday on the payment dates.\nBest regards."),
        (2, "Enclosed please find the signed receipt for booking advance.\nThank you."),
    ]

    chunks = detector.segment_pages(pages)
    assert len(chunks) == 2
    assert chunks[0].clause_number == "Page 1"
    assert chunks[1].clause_number == "Page 2"
    assert "discussion yesterday" in chunks[0].full_excerpt


# ==============================================================================
# 2. CLAUSE CLASSIFIER & HEURISTICS TESTS
# ==============================================================================


def test_clause_classifier_categories_and_risk():
    classifier = ClauseClassifier()

    # 1. Possession delay penalty (Nominal Rs 5/sqft) -> RISK, CRITICAL
    res_possession = classifier.classify_clause(
        title="Delayed Possession Compensation",
        text="In the event of delay in offering possession beyond the grace period, "
        "the Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft. per month.",
    )
    assert res_possession.category == ClauseCategory.POSSESSION_TERMS
    assert res_possession.status == "RISK"
    assert res_possession.severity == "CRITICAL"
    assert "RERA Section 18" in (res_possession.risk_details or "")

    # 2. Delayed payment interest (18% compounded monthly) -> RISK, HIGH
    res_payment = classifier.classify_clause(
        title="Default in Payment of Installments",
        text="Allottee fails to pay any installment when due shall attract interest on delayed "
        "payment at the rate of 18% per annum compounded monthly.",
    )
    assert res_payment.category == ClauseCategory.PAYMENT_TERMS
    assert res_payment.status == "RISK"
    assert res_payment.severity == "HIGH"

    # 3. Unilateral alteration rights -> RISK, HIGH
    res_alter = classifier.classify_clause(
        title="Alteration of Plans",
        text="The Developer shall be at liberty to effect alteration and modification of building plans "
        "up to 10% variation without prior consent of allottees.",
    )
    assert res_alter.category == ClauseCategory.ALTERATION_VARIATION
    assert res_alter.status == "RISK"
    assert res_alter.severity == "HIGH"

    # 4. Forfeiture of earnest money -> RISK, HIGH
    res_forfeit = classifier.classify_clause(
        title="Cancellation & Forfeiture",
        text="Upon cancellation by allottee, promoter shall forfeit twenty percent (20%) of the total consideration.",
    )
    assert res_forfeit.category == ClauseCategory.CANCELLATION_FORFEITURE
    assert res_forfeit.status == "RISK"
    assert res_forfeit.severity == "HIGH"

    # 5. Carpet area variation -> INCONSISTENCY, HIGH
    res_area = classifier.classify_clause(
        title="Carpet Area & Measurement Adjustments",
        text="Apartment has RERA carpet area of 1,380 sq.ft with allowable variation in area of +-3%.",
    )
    assert res_area.category == ClauseCategory.AREA_SPECIFICATIONS
    assert res_area.status == "INCONSISTENCY"

    # 6. Exclusive jurisdiction -> REVIEW_REQUIRED, MEDIUM
    res_dispute = classifier.classify_clause(
        title="Arbitration & Dispute Resolution",
        text="All disputes shall be referred to a sole arbitrator appointed solely by promoter with exclusive jurisdiction at New Delhi.",
    )
    assert res_dispute.category == ClauseCategory.DISPUTE_JURISDICTION
    assert res_dispute.status == "REVIEW_REQUIRED"
    assert res_dispute.severity == "MEDIUM"

    # 7. Statutory registration -> VERIFIED, LOW
    res_rera = classifier.classify_clause(
        title="Statutory Approvals & Compliance",
        text="The project is duly registered with RERA Authority under registration no HRERA-PKL-GGM-1248-2023.",
    )
    assert res_rera.category == ClauseCategory.STATUTORY_COMPLIANCE
    assert res_rera.status == "VERIFIED"
    assert res_rera.severity == "LOW"


# ==============================================================================
# 3. OBLIGATION EXTRACTOR TESTS
# ==============================================================================


def test_obligation_extractor():
    extractor = ObligationExtractor()

    # Buyer obligation
    buyer_text = (
        "The Allottee shall be liable to pay interest on delayed payment at 18% per annum. "
        "Purchaser agrees to pay all stamp duty and registration expenses."
    )
    ob_buyer = extractor.extract_obligation_details("Payment Default", buyer_text)
    assert ob_buyer.party == "BUYER"
    assert ob_buyer.action_type == "PAYMENT"
    assert ob_buyer.target_date_or_rate == "18% p.a."

    # Developer obligation
    dev_text = (
        "The Promoter shall handover possession of the apartment by scheduled completion date. "
        "In case of delay in offering possession, developer shall pay compensation of Rs. 5 per sq.ft."
    )
    ob_dev = extractor.extract_obligation_details("Handover of Possession", dev_text)
    assert ob_dev.party == "DEVELOPER"
    assert ob_dev.action_type == "DELIVERY"
    assert ob_dev.target_date_or_rate == "Rs. 5/sq.ft/month"

    # Rectification obligation
    rect_text = "The Developer will rectify any structural defect or workmanship flaw within five years at its own cost."
    ob_rect = extractor.extract_obligation_details("Defects Liability", rect_text)
    assert ob_rect.party == "DEVELOPER"
    assert ob_rect.action_type == "RECTIFICATION"
    assert ob_rect.target_date_or_rate == "5 Years"

    # Mutual / balanced terms
    mutual_text = "Both parties agree that these general terms shall govern the interpretation of this agreement."
    party_mutual = extractor.extract_party(mutual_text)
    assert party_mutual == "MUTUAL"


# ==============================================================================
# 4. DATABASE INTEGRATION & PIPELINE TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_clause_intelligence_engine_integration(db_session: AsyncSession):
    # Setup test document and pages in DB
    doc_id = "doc-test-engine-01"
    bundle_id = "skyview-a1204"

    test_doc = Document(
        id=doc_id,
        bundle_id=bundle_id,
        file_name="Test_Contract.pdf",
        document_type="BUILDER_BUYER_AGREEMENT",
        ocr_status="NOT_REQUIRED",
        page_count=2,
    )
    db_session.add(test_doc)

    page1 = DocumentPage(
        id="page-test-01",
        document_id=doc_id,
        page_number=1,
        raw_text=(
            "ARTICLE IV: MEASUREMENT & SPECIFICATIONS\n"
            "Clause 4.1: Permissible Variations\n"
            "The Allottee agrees that the Apartment has a RERA Carpet Area of 1,380 sq. ft."
        ),
    )
    page2 = DocumentPage(
        id="page-test-02",
        document_id=doc_id,
        page_number=2,
        raw_text=(
            "Clause 5.3: Delayed Payment Default\n"
            "Allottee shall be liable to pay interest on delayed payment at 18% per annum compounded monthly.\n\n"
            "Clause 8.2: Delayed Handover\n"
            "Promoter shall pay compensation of Rs. 5 per sq.ft per month for delay in offering possession."
        ),
    )
    db_session.add_all([page1, page2])
    await db_session.commit()

    # Execute clause engine
    clauses = await clause_intelligence_engine.process_document_clauses(
        session=db_session, bundle_id=bundle_id, document_id=doc_id
    )

    assert len(clauses) >= 3
    clause_nums = [c.clause_number for c in clauses]
    assert "Clause 4.1" in clause_nums
    assert "Clause 5.3" in clause_nums
    assert "Clause 8.2" in clause_nums

    # Verify document entity counts updated
    doc_query = await db_session.execute(select(Document).filter_by(id=doc_id))
    persisted_doc = doc_query.scalar_one()
    assert persisted_doc.clause_count == len(clauses)
    assert persisted_doc.issue_count >= 2


# ==============================================================================
# 5. API ENDPOINT TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_extract_and_retrieve_clauses_api(client: AsyncClient, samples_dir: Path):
    # 1. Upload sample PDF
    pdf_path = samples_dir / "sample_digital_agreement.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    files = {"file": ("Sample_BBA_For_Extraction.pdf", file_bytes, "application/pdf")}
    data = {"document_type": "BUILDER_BUYER_AGREEMENT"}

    upload_res = await client.post(
        "/api/v1/transactions/skyview-a1204/documents/upload",
        files=files,
        data=data,
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["documentId"]

    # 2. Trigger clause extraction API
    extract_res = await client.post(
        f"/api/v1/transactions/skyview-a1204/documents/{doc_id}/extract-clauses"
    )
    assert extract_res.status_code == 200
    clauses_data = extract_res.json()
    assert isinstance(clauses_data, list)
    assert len(clauses_data) >= 3

    # Check clause schema fields
    c = clauses_data[0]
    assert "id" in c
    assert "clauseNumber" in c
    assert "title" in c
    assert "category" in c
    assert "status" in c
    assert "severity" in c
    assert "obligationType" in c
    assert "pageNumber" in c
    assert "previewText" in c
    assert "fullExcerpt" in c

    # Verify risk status flags present
    statuses = [item["status"] for item in clauses_data]
    assert "RISK" in statuses

    # 3. Retrieve extracted clauses via GET endpoint
    get_res = await client.get(
        f"/api/v1/transactions/skyview-a1204/documents/{doc_id}/clauses"
    )
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert len(retrieved) == len(clauses_data)
    assert retrieved[0]["id"] == clauses_data[0]["id"]
