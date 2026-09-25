import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.transaction import TransactionBundle
from app.models.document import Document, DocumentPage
from app.models.clause import Clause
from app.models.finding import Finding
from app.models.attribute import ExtractedAttribute
from app.intelligence.cross_doc_engine import cross_document_engine
from app.services.timeline_service import timeline_service
from app.services.transaction_intelligence_orchestrator import transaction_intelligence_orchestrator
from app.services.copilot_service import transaction_copilot_service
from app.schemas.copilot import CopilotQueryRequestSchema
from app.services.transaction_brief_service import transaction_brief_service
from app.rag.rag_service import TransactionRAGService

rag_service = TransactionRAGService()


@pytest.mark.asyncio
async def test_harbor_crest_validation_and_novel_transaction_roundtrip(db_session: AsyncSession, client: AsyncClient):
    """
    MANUAL VALIDATION SPEC:
    1. Analyze Harbor Crest transaction tx-ed009c5a.
    2. Verify no old/demo values appear (1380, 1450, 2026, 28.5L, 20% earnest).
    3. Create a SECOND completely different transaction (Emerald Bay Suites).
    4. Verify it produces only its own intelligence.
    5. Return to Harbor Crest.
    6. Verify Harbor Crest still shows only Harbor Crest intelligence.
    """

    # -------------------------------------------------------------
    # 1. SETUP HARBOR CREST RESIDENCES (tx-ed009c5a)
    # -------------------------------------------------------------
    hc_bundle = TransactionBundle(
        id="tx-ed009c5a",
        title="Harbor Crest Residences — Tower C, Flat C-1708",
        project="Harbor Crest Residences",
        developer="Apex Habitat Developers Pvt. Ltd.",
        unit="Tower C, Flat C-1708",
        tower="Tower C",
        floor=17,
        location="Pune, Maharashtra",
        sale_price=11875000.0,
        carpet_area_sqft=1245.0,
        super_area_sqft=1620.0,
        advertised_carpet_area_sqft=1310.0,
        possession_date="2029-03-31",
        grace_period_months=0,
        status="ACTIVE",
    )
    db_session.add(hc_bundle)

    doc_bba = Document(
        id="doc-hc-agreement",
        bundle_id=hc_bundle.id,
        file_name="Harbor_Crest_Agreement_For_Sale.pdf",
        document_type="BUILDER_BUYER_AGREEMENT",
    )
    doc_allotment = Document(
        id="doc-hc-allotment",
        bundle_id=hc_bundle.id,
        file_name="Harbor_Crest_Allotment_Letter.pdf",
        document_type="ALLOTMENT_LETTER",
    )
    doc_marketing = Document(
        id="doc-hc-brochure",
        bundle_id=hc_bundle.id,
        file_name="Harbor_Crest_Sales_Brochure.pdf",
        document_type="BROCHURE",
    )
    db_session.add_all([doc_bba, doc_allotment, doc_marketing])

    # Harbor Crest Extracted Attributes
    hc_attrs = [
        ExtractedAttribute(
            id="hc-attr-1",
            bundle_id=hc_bundle.id,
            document_id=doc_bba.id,
            attribute_key="carpet_area",
            attribute_value="1,245 sq.ft",
            normalized_value="1245.0",
            unit="sq.ft",
            source_page=14,
            raw_excerpt="The Apartment has a RERA Carpet Area of 1,245 sq. ft. (115.66 sq. m.)",
        ),
        ExtractedAttribute(
            id="hc-attr-2",
            bundle_id=hc_bundle.id,
            document_id=doc_bba.id,
            attribute_key="possession_date",
            attribute_value="31 March 2029",
            normalized_value="2029-03-31",
            unit="date:DAY",
            source_page=22,
            raw_excerpt="The Promoter commits to complete and offer possession on or before 31 March 2029.",
        ),
        ExtractedAttribute(
            id="hc-attr-3",
            bundle_id=hc_bundle.id,
            document_id=doc_bba.id,
            attribute_key="base_price",
            attribute_value="₹1,18,75,000",
            normalized_value="11875000.0",
            unit="INR",
            source_page=8,
            raw_excerpt="Total Sale Consideration for Flat C-1708 is Rs. 1,18,75,000/-",
        ),
        ExtractedAttribute(
            id="hc-attr-4",
            bundle_id=hc_bundle.id,
            document_id=doc_allotment.id,
            attribute_key="carpet_area",
            attribute_value="1,245 sq.ft",
            normalized_value="1245.0",
            unit="sq.ft",
            source_page=1,
            raw_excerpt="Allotted unit C-1708 admeasuring RERA carpet area of 1,245 sq.ft.",
        ),
        ExtractedAttribute(
            id="hc-attr-5",
            bundle_id=hc_bundle.id,
            document_id=doc_allotment.id,
            attribute_key="possession_date",
            attribute_value="15 September 2028",
            normalized_value="2028-09-15",
            unit="date:DAY",
            source_page=2,
            raw_excerpt="Anticipated date of possession handover is 15 September 2028.",
        ),
        ExtractedAttribute(
            id="hc-attr-6",
            bundle_id=hc_bundle.id,
            document_id=doc_marketing.id,
            attribute_key="carpet_area",
            attribute_value="1,310 sq.ft",
            normalized_value="1310.0",
            unit="sq.ft",
            source_page=4,
            raw_excerpt="Spacious 3BHK residences featuring 1,310 sq.ft carpet area.",
        ),
        ExtractedAttribute(
            id="hc-attr-7",
            bundle_id=hc_bundle.id,
            document_id=doc_marketing.id,
            attribute_key="possession_date",
            attribute_value="2028",
            normalized_value="2028-12-31",
            unit="date:YEAR",
            source_page=3,
            raw_excerpt="Target handover during 2028.",
        ),
    ]
    db_session.add_all(hc_attrs)

    # Add Pages and Clauses for RAG & Copilot
    p_bba = DocumentPage(
        id="p-hc-bba-14",
        document_id=doc_bba.id,
        page_number=14,
        raw_text="The Apartment has a RERA Carpet Area of 1,245 sq. ft. Total consideration is Rs. 1,18,75,000.",
    )
    p_mkt = DocumentPage(
        id="p-hc-mkt-4",
        document_id=doc_marketing.id,
        page_number=4,
        raw_text="Spacious 3BHK residences featuring 1,310 sq.ft carpet area. Target handover during 2028.",
    )
    db_session.add_all([p_bba, p_mkt])

    c_bba = Clause(
        id="cl-hc-1",
        bundle_id=hc_bundle.id,
        document_id=doc_bba.id,
        clause_number="Clause 4.1",
        title="Total Consideration & Payment",
        category="Payment & Consideration",
        status="VERIFIED",
        preview_text="Total consideration for Flat C-1708 is Rs. 1,18,75,000.",
        full_excerpt="The Allottee agrees that the total sale consideration for Flat C-1708 having RERA carpet area 1,245 sq.ft is Rs. 1,18,75,000.",
        analysis_summary="Total sale consideration Rs. 1,18,75,000.",
        page_number=14,
    )
    db_session.add(c_bba)
    await db_session.commit()

    # 1. Run Cross-Document Intelligence Engine
    await cross_document_engine.analyze_transaction(db_session, hc_bundle.id)

    # 2. Ingest RAG Chunks
    await rag_service.index_document(db_session, hc_bundle.id, doc_bba.id)
    await rag_service.index_document(db_session, hc_bundle.id, doc_marketing.id)

    # 3. Query Intelligence Services
    hc_cc = await transaction_intelligence_orchestrator.get_command_center(db_session, hc_bundle.id)
    hc_timeline = await timeline_service.get_reconciled_timeline(db_session, hc_bundle.id)
    hc_brief = await transaction_brief_service.generate_brief(db_session, hc_bundle.id)
    hc_copilot = await transaction_copilot_service.query_copilot(
        db_session,
        hc_bundle.id,
        CopilotQueryRequestSchema(query="What is the carpet area and total consideration?"),
    )
    hc_rag = await rag_service.query_transaction(
        db_session,
        hc_bundle.id,
        "What is the consideration amount?",
    )

    # 4. Assert Harbor Crest factual values
    assert hc_cc.projectName == "Harbor Crest Residences"
    assert hc_cc.unitNumber == "Tower C, Flat C-1708"
    assert hc_cc.financialExposure.baseConsideration == 11875000.0
    assert hc_cc.financialExposure.baseConsiderationFormatted == "₹1.19 Cr"

    # Timeline assertions
    event_dates = [e.eventDate for e in hc_timeline.events]
    assert "2029-03-31" in event_dates
    assert "2028-09-15" in event_dates
    mkt_event = next((e for e in hc_timeline.events if e.dateType == "MARKETING"), None)
    if mkt_event:
        assert mkt_event.precision == "YEAR"
        assert mkt_event.rawEvidence == "2028"

    # Copilot & RAG assertions
    assert "1,245" in hc_copilot.answer or "1245" in hc_copilot.answer or "1,18,75,000" in hc_copilot.answer
    assert "1,18,75,000" in hc_rag.answer or "11875000" in hc_rag.answer or "Harbor Crest" in hc_rag.answer

    # 5. Assert ZERO Stale SkyView Data in Harbor Crest
    all_hc_str = (
        str(hc_cc.dict()) +
        str(hc_timeline.dict()) +
        str(hc_brief.dict()) +
        hc_copilot.answer +
        hc_rag.answer
    )
    stale_values = [
        "1,380", "1380",
        "1,450", "1450",
        "SkyView", "A-1204", "Skyline Urban",
        "₹28.5L", "28.5 Lakhs", "2850000",
        "December 2026", "2026-12-31"
    ]
    for sv in stale_values:
        assert sv not in all_hc_str, f"Stale SkyView token '{sv}' leaked into Harbor Crest intelligence!"


    # -------------------------------------------------------------
    # 2. CREATE NOVEL TRANSACTION (Emerald Bay Suites, tx-emerald-001)
    # -------------------------------------------------------------
    eb_bundle = TransactionBundle(
        id="tx-emerald-001",
        title="Emerald Bay Suites — Flat B-402",
        project="Emerald Bay Suites",
        developer="Solitaire Living Corp",
        unit="Flat B-402",
        tower="Tower B",
        floor=4,
        location="Panaji, Goa",
        sale_price=8500000.0,
        carpet_area_sqft=950.0,
        super_area_sqft=1250.0,
        possession_date="2027-11-30",
        grace_period_months=0,
        status="ACTIVE",
    )
    db_session.add(eb_bundle)

    doc_eb = Document(
        id="doc-eb-agreement",
        bundle_id=eb_bundle.id,
        file_name="Emerald_Bay_Agreement.pdf",
        document_type="BUILDER_BUYER_AGREEMENT",
    )
    db_session.add(doc_eb)

    eb_attrs = [
        ExtractedAttribute(
            id="eb-attr-1",
            bundle_id=eb_bundle.id,
            document_id=doc_eb.id,
            attribute_key="carpet_area",
            attribute_value="950 sq.ft",
            normalized_value="950.0",
            unit="sq.ft",
            source_page=5,
            raw_excerpt="Unit B-402 with RERA carpet area of 950 sq.ft.",
        ),
        ExtractedAttribute(
            id="eb-attr-2",
            bundle_id=eb_bundle.id,
            document_id=doc_eb.id,
            attribute_key="possession_date",
            attribute_value="30 November 2027",
            normalized_value="2027-11-30",
            unit="date:DAY",
            source_page=12,
            raw_excerpt="Possession handover scheduled for 30 November 2027.",
        ),
        ExtractedAttribute(
            id="eb-attr-3",
            bundle_id=eb_bundle.id,
            document_id=doc_eb.id,
            attribute_key="base_price",
            attribute_value="₹85,00,000",
            normalized_value="8500000.0",
            unit="INR",
            source_page=3,
            raw_excerpt="Total consideration Rs. 85,00,000/- only.",
        ),
    ]
    db_session.add_all(eb_attrs)

    p_eb = DocumentPage(
        id="p-eb-1",
        document_id=doc_eb.id,
        page_number=5,
        raw_text="Emerald Bay Suites Flat B-402 with RERA carpet area of 950 sq.ft. Consideration Rs. 85,00,000.",
    )
    db_session.add(p_eb)
    await db_session.commit()

    # Analyze Transaction B
    await cross_document_engine.analyze_transaction(db_session, eb_bundle.id)
    await rag_service.index_document(db_session, eb_bundle.id, doc_eb.id)

    eb_cc = await transaction_intelligence_orchestrator.get_command_center(db_session, eb_bundle.id)
    eb_timeline = await timeline_service.get_reconciled_timeline(db_session, eb_bundle.id)
    eb_brief = await transaction_brief_service.generate_brief(db_session, eb_bundle.id)
    eb_copilot = await transaction_copilot_service.query_copilot(
        db_session,
        eb_bundle.id,
        CopilotQueryRequestSchema(query="What is the price and carpet area?"),
    )

    all_eb_str = (
        str(eb_cc.dict()) +
        str(eb_timeline.dict()) +
        str(eb_brief.dict()) +
        eb_copilot.answer
    )

    # Assert Emerald Bay facts
    assert "Emerald Bay Suites" in all_eb_str
    assert "8500000" in all_eb_str or "85,00,000" in all_eb_str
    assert "950" in all_eb_str

    # Assert ZERO Harbor Crest leakage into Emerald Bay
    harbor_crest_tokens = [
        "Harbor Crest", "C-1708", "Apex Habitat",
        "1,245", "1245", "1,310", "1310",
        "1,18,75,000", "11875000", "2029-03-31", "2028-09-15"
    ]
    for hct in harbor_crest_tokens:
        assert hct not in all_eb_str, f"Harbor Crest token '{hct}' leaked into Emerald Bay!"

    # Assert ZERO SkyView leakage into Emerald Bay
    for sv in stale_values:
        assert sv not in all_eb_str, f"SkyView token '{sv}' leaked into Emerald Bay!"


    # -------------------------------------------------------------
    # 3. RETURN TO HARBOR CREST (tx-ed009c5a) AND RE-QUERY
    # -------------------------------------------------------------
    hc_cc_re = await transaction_intelligence_orchestrator.get_command_center(db_session, hc_bundle.id)
    hc_timeline_re = await timeline_service.get_reconciled_timeline(db_session, hc_bundle.id)
    hc_brief_re = await transaction_brief_service.generate_brief(db_session, hc_bundle.id)
    hc_copilot_re = await transaction_copilot_service.query_copilot(
        db_session,
        hc_bundle.id,
        CopilotQueryRequestSchema(query="What is the carpet area and total consideration?"),
    )

    all_hc_re_str = (
        str(hc_cc_re.dict()) +
        str(hc_timeline_re.dict()) +
        str(hc_brief_re.dict()) +
        hc_copilot_re.answer
    )

    # Must still contain Harbor Crest facts
    assert "Harbor Crest Residences" in all_hc_re_str
    assert "11875000" in all_hc_re_str or "1,18,75,000" in all_hc_re_str
    assert "1,245" in all_hc_re_str or "1245" in all_hc_re_str

    # Must NOT contain Emerald Bay facts
    emerald_tokens = ["Emerald Bay", "B-402", "Solitaire", "85,00,000", "8500000", "950"]
    for ebt in emerald_tokens:
        assert ebt not in all_hc_re_str, f"Emerald Bay token '{ebt}' leaked back into Harbor Crest!"

    # Must NOT contain SkyView facts
    for sv in stale_values:
        assert sv not in all_hc_re_str, f"SkyView token '{sv}' leaked back into Harbor Crest!"
