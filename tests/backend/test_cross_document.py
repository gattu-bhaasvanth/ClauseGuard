import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.transaction import TransactionBundle
from app.models.document import Document
from app.models.attribute import ExtractedAttribute
from app.models.finding import Finding
from app.intelligence.evaluators import (
    AreaDiscrepancyEvaluator,
    PossessionDiscrepancyEvaluator,
    PricingDiscrepancyEvaluator,
    UnitDiscrepancyEvaluator,
)
from app.intelligence.alignment_matrix import alignment_matrix_builder
from app.intelligence.cross_doc_engine import cross_document_engine


# ==============================================================================
# 1. EVALUATOR UNIT TESTS
# ==============================================================================


def test_area_discrepancy_evaluator():
    evaluator = AreaDiscrepancyEvaluator()

    doc_brochure = Document(
        id="doc-b-01",
        bundle_id="b-test",
        file_name="Brochure.pdf",
        document_type="MARKETING_BROCHURE",
    )
    doc_agreement = Document(
        id="doc-a-01",
        bundle_id="b-test",
        file_name="BBA.pdf",
        document_type="BUILDER_BUYER_AGREEMENT",
    )
    docs = [doc_brochure, doc_agreement]

    attr_brochure = ExtractedAttribute(
        id="a1",
        bundle_id="b-test",
        document_id="doc-b-01",
        attribute_key="carpet_area",
        attribute_value="1,450 sq.ft",
        normalized_value="1450.0",
        unit="sq.ft",
        source_page=4,
        raw_excerpt="Spacious 3BHK residences with 1,450 sq.ft carpet area.",
    )
    attr_agreement = ExtractedAttribute(
        id="a2",
        bundle_id="b-test",
        document_id="doc-a-01",
        attribute_key="carpet_area",
        attribute_value="1,380 sq. ft.",
        normalized_value="1380.0",
        unit="sq.ft",
        source_page=12,
        source_clause="Clause 4.1",
        raw_excerpt="The Allottee agrees that the Apartment has a RERA Carpet Area of 1,380 sq. ft.",
    )

    findings = evaluator.evaluate(
        bundle_id="b-test",
        documents=docs,
        attributes=[attr_brochure, attr_agreement],
    )

    assert len(findings) == 1
    f = findings[0]
    assert f.finding_type == "INCONSISTENCY"
    assert f.category == "AREA"
    assert f.severity == "HIGH"
    assert "Carpet Area Discrepancy" in f.title
    assert "70.0 sq.ft" in f.description
    assert f.primary_evidence["documentName"] == "Brochure.pdf"
    assert f.secondary_evidence["documentName"] == "BBA.pdf"
    assert f.secondary_evidence["clauseNumber"] == "Clause 4.1"


def test_possession_discrepancy_evaluator():
    evaluator = PossessionDiscrepancyEvaluator()

    doc_allotment = Document(
        id="doc-al-01",
        bundle_id="b-test",
        file_name="Allotment_Letter.pdf",
        document_type="ALLOTMENT_LETTER",
    )
    doc_agreement = Document(
        id="doc-bba-01",
        bundle_id="b-test",
        file_name="Agreement_Sale.pdf",
        document_type="BUILDER_BUYER_AGREEMENT",
    )
    docs = [doc_allotment, doc_agreement]

    attr_allotment = ExtractedAttribute(
        id="p1",
        bundle_id="b-test",
        document_id="doc-al-01",
        attribute_key="possession_date",
        attribute_value="30th June 2027",
        normalized_value="2027-06-30",
        unit="date",
        source_page=2,
        raw_excerpt="Possession is projected for 30th June 2027.",
    )
    attr_agreement = ExtractedAttribute(
        id="p2",
        bundle_id="b-test",
        document_id="doc-bba-01",
        attribute_key="possession_date",
        attribute_value="31st December 2027",
        normalized_value="2027-12-31",
        unit="date",
        source_page=19,
        source_clause="Clause 11.2",
        raw_excerpt="Complete construction of the Apartment by 31st December 2027.",
    )

    findings = evaluator.evaluate(
        bundle_id="b-test",
        documents=docs,
        attributes=[attr_allotment, attr_agreement],
    )

    assert len(findings) == 1
    f = findings[0]
    assert f.category == "POSSESSION"
    assert "Possession Date Shift" in f.title
    assert "2027-06-30" in f.description
    assert "2027-12-31" in f.description


def test_pricing_and_unit_discrepancy_evaluators():
    doc1 = Document(id="d1", bundle_id="b-test", file_name="Doc1.pdf", document_type="ALLOTMENT_LETTER")
    doc2 = Document(id="d2", bundle_id="b-test", file_name="Doc2.pdf", document_type="BUILDER_BUYER_AGREEMENT")
    docs = [doc1, doc2]

    # Price Discrepancy
    price1 = ExtractedAttribute(
        id="pr1", bundle_id="b-test", document_id="d1",
        attribute_key="total_price", attribute_value="₹ 1.35 Cr", normalized_value="13500000.0",
        unit="INR", source_page=1, raw_excerpt="Total price ₹ 1.35 Cr"
    )
    price2 = ExtractedAttribute(
        id="pr2", bundle_id="b-test", document_id="d2",
        attribute_key="total_price", attribute_value="₹ 1.42 Cr", normalized_value="14200000.0",
        unit="INR", source_page=5, raw_excerpt="Total consideration ₹ 1.42 Cr"
    )
    price_eval = PricingDiscrepancyEvaluator()
    price_findings = price_eval.evaluate("b-test", docs, [price1, price2])
    assert len(price_findings) == 1
    assert price_findings[0].category == "PRICING"
    assert "Total Consideration Mismatch" in price_findings[0].title

    # Unit Discrepancy
    u1 = ExtractedAttribute(
        id="u1", bundle_id="b-test", document_id="d1",
        attribute_key="unit_number", attribute_value="A-1204", normalized_value="A-1204",
        source_page=1
    )
    u2 = ExtractedAttribute(
        id="u2", bundle_id="b-test", document_id="d2",
        attribute_key="unit_number", attribute_value="B-1204", normalized_value="B-1204",
        source_page=1
    )
    unit_eval = UnitDiscrepancyEvaluator()
    unit_findings = unit_eval.evaluate("b-test", docs, [u1, u2])
    assert len(unit_findings) == 1
    assert unit_findings[0].severity == "CRITICAL"
    assert "Unit Number Mismatch" in unit_findings[0].title


# ==============================================================================
# 2. ALIGNMENT MATRIX TESTS
# ==============================================================================


def test_document_alignment_matrix():
    doc1 = Document(id="d1", bundle_id="b-matrix", file_name="Brochure.pdf", document_type="MARKETING_BROCHURE")
    doc2 = Document(id="d2", bundle_id="b-matrix", file_name="Agreement.pdf", document_type="BUILDER_BUYER_AGREEMENT")
    docs = [doc1, doc2]

    attrs = [
        # Inconsistent Carpet Area
        ExtractedAttribute(
            id="a1", bundle_id="b-matrix", document_id="d1",
            attribute_key="carpet_area", attribute_value="1450 sqft", normalized_value="1450.0",
            source_page=1
        ),
        ExtractedAttribute(
            id="a2", bundle_id="b-matrix", document_id="d2",
            attribute_key="carpet_area", attribute_value="1380 sqft", normalized_value="1380.0",
            source_page=12
        ),
        # Consistent Unit Number
        ExtractedAttribute(
            id="a3", bundle_id="b-matrix", document_id="d1",
            attribute_key="unit_number", attribute_value="A-1204", normalized_value="A-1204",
            source_page=1
        ),
        ExtractedAttribute(
            id="a4", bundle_id="b-matrix", document_id="d2",
            attribute_key="unit_number", attribute_value="A-1204", normalized_value="A-1204",
            source_page=1
        ),
    ]

    matrix_res = alignment_matrix_builder.build_matrix("b-matrix", docs, attrs)

    assert matrix_res.bundleId == "b-matrix"
    assert matrix_res.totalAttributesCompared == 2
    assert matrix_res.inconsistentAttributesCount == 1

    # Carpet Area should be flagged inconsistent and sorted first
    item0 = matrix_res.matrix[0]
    assert item0.attributeKey == "carpet_area"
    assert item0.isConsistent is False
    assert len(item0.valuesByDocument) == 2

    # Unit Number is consistent
    item1 = matrix_res.matrix[1]
    assert item1.attributeKey == "unit_number"
    assert item1.isConsistent is True


# ==============================================================================
# 3. CROSS-DOCUMENT ENGINE INTEGRATION TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_cross_document_engine_integration(db_session: AsyncSession):
    # Setup test bundle with multiple documents and conflicting attributes
    bundle_id = "test-cross-bundle"
    bundle = TransactionBundle(
        id=bundle_id,
        title="Test Inconsistency Project",
        project="Test Project",
        unit="A-101",
        developer="Test Developer",
        health_score=100,
        status="ANALYSIS_COMPLETE",
    )
    db_session.add(bundle)

    d_brochure = Document(
        id="d-test-brochure", bundle_id=bundle_id, file_name="Brochure.pdf",
        document_type="MARKETING_BROCHURE"
    )
    d_agreement = Document(
        id="d-test-agreement", bundle_id=bundle_id, file_name="Agreement.pdf",
        document_type="BUILDER_BUYER_AGREEMENT"
    )
    db_session.add_all([d_brochure, d_agreement])

    # Conflicting carpet areas (1450 vs 1380)
    attr1 = ExtractedAttribute(
        id="attr-t-1", bundle_id=bundle_id, document_id="d-test-brochure",
        attribute_key="carpet_area", attribute_value="1450 sqft", normalized_value="1450.0",
        unit="sq.ft", source_page=2, raw_excerpt="Brochure mentions 1450 sqft."
    )
    attr2 = ExtractedAttribute(
        id="attr-t-2", bundle_id=bundle_id, document_id="d-test-agreement",
        attribute_key="carpet_area", attribute_value="1380 sqft", normalized_value="1380.0",
        unit="sq.ft", source_page=10, source_clause="Clause 4.1", raw_excerpt="Contract fixes 1380 sqft."
    )
    db_session.add_all([attr1, attr2])
    await db_session.commit()

    # Run cross-document engine
    analysis = await cross_document_engine.analyze_transaction(
        session=db_session, bundle_id=bundle_id
    )

    assert analysis.bundleId == bundle_id
    assert analysis.inconsistenciesCount >= 1
    assert analysis.totalIssues >= 1
    # Health score should be deducted for the HIGH severity inconsistency (100 - 10 = 90)
    assert analysis.healthScore <= 90

    # Verify bundle in database has updated score and status
    bundle_query = await db_session.execute(select(TransactionBundle).filter_by(id=bundle_id))
    updated_bundle = bundle_query.scalar_one()
    assert updated_bundle.health_score == analysis.healthScore

    # Verify findings in database
    findings_query = await db_session.execute(
        select(Finding).filter_by(bundle_id=bundle_id, finding_type="INCONSISTENCY")
    )
    persisted_findings = findings_query.scalars().all()
    assert len(persisted_findings) == analysis.inconsistenciesCount


# ==============================================================================
# 4. REST API TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_cross_document_api_endpoints(client: AsyncClient):
    # 1. Trigger transaction analysis API on skyview-a1204
    analyze_res = await client.post("/api/v1/transactions/skyview-a1204/analyze")
    assert analyze_res.status_code == 200
    data = analyze_res.json()
    assert data["bundleId"] == "skyview-a1204"
    assert "healthScore" in data
    assert "status" in data
    assert "inconsistencies" in data
    assert "risks" in data
    assert len(data["inconsistencies"]) >= 0

    # 2. Get inconsistencies endpoint
    inc_res = await client.get("/api/v1/transactions/skyview-a1204/inconsistencies")
    assert inc_res.status_code == 200
    inconsistencies = inc_res.json()
    assert isinstance(inconsistencies, list)

    # 3. Get comparison matrix endpoint
    matrix_res = await client.get("/api/v1/transactions/skyview-a1204/matrix")
    assert matrix_res.status_code == 200
    matrix_data = matrix_res.json()
    assert matrix_data["bundleId"] == "skyview-a1204"
    assert "totalAttributesCompared" in matrix_data
    assert "matrix" in matrix_data
    assert isinstance(matrix_data["matrix"], list)
