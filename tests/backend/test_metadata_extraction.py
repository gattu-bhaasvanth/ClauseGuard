import pytest
from pathlib import Path
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document, DocumentPage
from app.models.attribute import ExtractedAttribute
from app.intelligence.entity_normalizer import (
    AreaNormalizer,
    CurrencyNormalizer,
    DateNormalizer,
    PercentageNormalizer,
    RERANormalizer,
)
from app.intelligence.entity_extractor import TransactionEntityExtractor
from app.intelligence.metadata_engine import metadata_engine


@pytest.fixture
def samples_dir():
    return Path(__file__).resolve().parent.parent.parent / "data" / "samples"


# ==============================================================================
# 1. NORMALIZER UNIT TESTS
# ==============================================================================


def test_area_normalizer():
    # 1. Standard sq.ft with comma
    res1 = AreaNormalizer.normalize("1,380 sq. ft.")
    assert res1 is not None
    assert res1[0] == 1380.0
    assert res1[1] == "sq.ft"

    # 2. sqft attached
    res2 = AreaNormalizer.normalize("1450sqft")
    assert res2 is not None
    assert res2[0] == 1450.0

    # 3. Square meters converted to square feet (128.20 sqm * 10.7639 ~= 1379.93)
    res3 = AreaNormalizer.normalize("128.20 sq. m.")
    assert res3 is not None
    assert 1379.0 < res3[0] < 1381.0
    assert res3[1] == "sq.ft"

    # 4. Spelled out square feet
    res4 = AreaNormalizer.normalize("3,100 square feet")
    assert res4 is not None
    assert res4[0] == 3100.0


def test_currency_normalizer():
    # 1. Crores with symbol
    res_cr = CurrencyNormalizer.normalize("₹ 1.42 Cr")
    assert res_cr is not None
    assert res_cr[0] == 14200000.0
    assert res_cr[1] == "INR"

    # 2. Spelled out Crores
    res_crores = CurrencyNormalizer.normalize("Rs. 3.85 Crores")
    assert res_crores is not None
    assert res_crores[0] == 38500000.0

    # 3. Lakhs
    res_lakh = CurrencyNormalizer.normalize("45 Lakhs")
    assert res_lakh is not None
    assert res_lakh[0] == 4500000.0

    # 4. Full comma-formatted numeral
    res_full = CurrencyNormalizer.normalize("Rs. 1,42,00,000/-")
    assert res_full is not None
    assert res_full[0] == 14200000.0


def test_date_and_timeline_normalizers():
    # 1. Textual date (DD Month YYYY)
    d1 = DateNormalizer.normalize("31st December 2027")
    assert d1 == "2027-12-31"

    # 2. Textual date with 'day of'
    d2 = DateNormalizer.normalize("18th day of September 2026")
    assert d2 == "2026-09-18"

    # 3. Textual reverse (Month DD, YYYY)
    d3 = DateNormalizer.normalize("June 30, 2027")
    assert d3 == "2027-06-30"

    # 4. DD/MM/YYYY
    d4 = DateNormalizer.normalize("30/06/2027")
    assert d4 == "2027-06-30"

    # 5. ISO format
    d5 = DateNormalizer.normalize("2027-12-31")
    assert d5 == "2027-12-31"

    # 6. Grace period days to months
    gp1 = DateNormalizer.normalize_grace_period("180 days")
    assert gp1 == (6, "months")

    # 7. Grace period months
    gp2 = DateNormalizer.normalize_grace_period("3 months")
    assert gp2 == (3, "months")


def test_percentage_and_rera_normalizers():
    # 1. Delayed interest rate
    p1 = PercentageNormalizer.normalize("18% per annum")
    assert p1 == 18.0

    # 2. Variation percentage
    p2 = PercentageNormalizer.normalize("±3%")
    assert p2 == 3.0

    # 3. Clean RERA registration code
    r1 = RERANormalizer.normalize("HARERA REGISTRATION NO: HRERA-PKL-GGM-1248-2023")
    assert r1 == "HRERA-PKL-GGM-1248-2023"

    r2 = RERANormalizer.normalize("RERA NO. PRM/KA/RERA/1251/310/PR/171015/000456")
    assert "PRM/KA/RERA" in (r2 or "")


# ==============================================================================
# 2. ENTITY EXTRACTOR UNIT TESTS
# ==============================================================================


def test_entity_extractor_real_estate_text():
    extractor = TransactionEntityExtractor()

    contract_text = (
        "This Agreement for Sale is executed between SKYLINE URBAN DEVELOPERS PVT. LTD. "
        "and ALLOTTEE PURCHASER for Unit No. A-1204 in Tower A.\n"
        "HARERA REGISTRATION NO: HRERA-PKL-GGM-1248-2023.\n\n"
        "ARTICLE IV: MEASUREMENT & SPECIFICATIONS\n"
        "The Allottee agrees that the Apartment has a RERA Carpet Area of 1,380 sq. ft.\n"
        "Total Consideration of Rs. 1,42,00,000/- payable as per milestone schedule.\n"
        "The Promoter proposes to complete construction of the Apartment by 31st December 2027.\n"
        "The Promoter shall be entitled to an unconditional grace period of 180 days thereafter.\n"
        "Delay in payments by Allottee attracts interest on delayed payment at the rate of 18% per annum."
    )

    pages = [(1, contract_text)]
    entities = extractor.extract_from_clauses_and_pages(pages=pages)

    assert len(entities) >= 6

    keys = {e.attribute_key: e for e in entities}
    assert "carpet_area" in keys
    assert keys["carpet_area"].normalized_value == "1380.0"
    assert keys["carpet_area"].unit == "sq.ft"
    assert "1,380 sq. ft." in keys["carpet_area"].raw_excerpt

    assert "total_price" in keys
    assert keys["total_price"].normalized_value == "14200000.0"

    assert "possession_date" in keys
    assert keys["possession_date"].normalized_value == "2027-12-31"

    assert "grace_period_months" in keys
    assert keys["grace_period_months"].normalized_value == "6"

    assert "delayed_payment_interest_rate" in keys
    assert keys["delayed_payment_interest_rate"].normalized_value == "18.0"

    assert "rera_registration_number" in keys
    assert "HRERA-PKL-GGM-1248-2023" in keys["rera_registration_number"].normalized_value


def test_payment_milestones_extractor():
    extractor = TransactionEntityExtractor()
    schedule_text = (
        "PAYMENT PLAN SCHEDULE\n"
        "1. On Booking / Advance: 10%\n"
        "2. On Execution of Sale Agreement: 10%\n"
        "3. On Completion of Foundation: 10%\n"
        "4. On Completion of 4th Slab: 10%\n"
        "5. On Completion of Superstructure: 20%\n"
        "6. On Offer of Possession: 40%\n"
    )

    milestones = extractor.extract_payment_milestones(schedule_text)
    assert len(milestones) == 6
    assert milestones[0]["percentage"] == 10.0
    assert "Booking" in milestones[0]["milestone"]
    assert milestones[4]["percentage"] == 20.0
    assert milestones[5]["percentage"] == 40.0


# ==============================================================================
# 3. METADATA ENGINE & DATABASE PERSISTENCE TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_metadata_engine_process_and_persistence(db_session: AsyncSession):
    doc_id = "doc-meta-test-01"
    bundle_id = "skyview-a1204"

    # Add test doc
    test_doc = Document(
        id=doc_id,
        bundle_id=bundle_id,
        file_name="Meta_Test_Doc.pdf",
        document_type="BUILDER_BUYER_AGREEMENT",
        ocr_status="NOT_REQUIRED",
        page_count=1,
    )
    db_session.add(test_doc)

    page1 = DocumentPage(
        id="page-meta-test-01",
        document_id=doc_id,
        page_number=1,
        raw_text=(
            "HARERA REGISTRATION NO: HRERA-PKL-GGM-1248-2023\n"
            "Unit No. A-1204, Tower A.\n"
            "RERA Carpet Area of 1,380 sq. ft.\n"
            "Total Consideration of Rs. 1,42,00,000/-.\n"
            "Possession date is projected for 31st December 2027 with a grace period of 180 days."
        ),
    )
    db_session.add(page1)
    await db_session.commit()

    # Run metadata extraction
    persisted_attrs = await metadata_engine.process_document_metadata(
        session=db_session, bundle_id=bundle_id, document_id=doc_id
    )

    assert len(persisted_attrs) >= 4
    keys = {a.attribute_key for a in persisted_attrs}
    assert "carpet_area" in keys
    assert "total_price" in keys
    assert "possession_date" in keys

    # Verify attributes in database
    db_attrs_query = await db_session.execute(
        select(ExtractedAttribute).filter_by(document_id=doc_id)
    )
    db_attrs = db_attrs_query.scalars().all()
    assert len(db_attrs) == len(persisted_attrs)

    # Re-running process_document_metadata should update without duplicate primary keys
    persisted_attrs_rerun = await metadata_engine.process_document_metadata(
        session=db_session, bundle_id=bundle_id, document_id=doc_id
    )
    assert len(persisted_attrs_rerun) == len(persisted_attrs)


# ==============================================================================
# 4. REST API ENDPOINT TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_metadata_api_endpoints(client: AsyncClient, samples_dir: Path):
    # 1. Upload sample agreement PDF
    pdf_path = samples_dir / "sample_digital_agreement.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    files = {"file": ("Sample_Meta_Agreement.pdf", file_bytes, "application/pdf")}
    data = {"document_type": "BUILDER_BUYER_AGREEMENT"}

    upload_res = await client.post(
        "/api/v1/transactions/skyview-a1204/documents/upload",
        files=files,
        data=data,
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["documentId"]

    # 2. Call document extract-metadata POST API
    extract_res = await client.post(
        f"/api/v1/transactions/skyview-a1204/documents/{doc_id}/extract-metadata"
    )
    assert extract_res.status_code == 200
    meta_data = extract_res.json()
    assert meta_data["documentId"] == doc_id
    assert meta_data["attributeCount"] >= 3
    assert len(meta_data["attributes"]) == meta_data["attributeCount"]

    attr_keys = [a["attributeKey"] for a in meta_data["attributes"]]
    assert "carpet_area" in attr_keys or "unit_number" in attr_keys

    # 3. Call document metadata GET API
    get_doc_meta = await client.get(
        f"/api/v1/transactions/skyview-a1204/documents/{doc_id}/metadata"
    )
    assert get_doc_meta.status_code == 200
    assert get_doc_meta.json()["attributeCount"] == meta_data["attributeCount"]

    # 4. Call transaction unified metadata GET API
    unified_res = await client.get("/api/v1/transactions/skyview-a1204/metadata")
    assert unified_res.status_code == 200
    unified_data = unified_res.json()
    assert unified_data["bundleId"] == "skyview-a1204"
    assert unified_data["carpetAreaSqft"] is not None
    assert unified_data["totalAttributesExtracted"] >= meta_data["attributeCount"]
