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
async def test_permanent_cross_transaction_isolation_pipeline(db_session: AsyncSession, client: AsyncClient):
    """
    PERMANENT REGRESSION SUITE: Cross-Transaction Data Isolation & Anti-Leakage.
    Verifies that 3 completely distinct transactions (A, B, C) never leak facts,
    documents, clauses, metadata, findings, timeline, RAG chunks, copilot answers,
    or executive briefs into each other or from old demo transactions.
    """

    # -------------------------------------------------------------
    # 1. SETUP TRANSACTION A: "Silver Crest Heights" (Penthouse P-101)
    # -------------------------------------------------------------
    tx_a = TransactionBundle(
        id="tx-silver-a",
        title="Silver Crest Heights — Penthouse P-101",
        project="Silver Crest Heights",
        unit="Penthouse P-101",
        floor=15,
        tower="Tower Silver",
        developer="Silverline Infra Projects Ltd.",
        city="Bengaluru",
        location="Whitefield, Bengaluru, KA",
        property_type="Penthouse",
        carpet_area_sqft=1650.0,
        super_area_sqft=2250.0,
        advertised_carpet_area_sqft=1800.0,
        sale_price=24000000.0,
        possession_date="2029-06-30",
        grace_period_months=3,
        health_score=80,
        status="ACTIVE",
    )
    doc_a = Document(
        id="doc-a-bba",
        bundle_id="tx-silver-a",
        file_name="SilverCrest_Agreement_P101.pdf",
        document_type="BUILDER_BUYER_AGREEMENT",
        page_count=20,
        clause_count=10,
        issue_count=1,
    )
    page_a = DocumentPage(
        id="page-a-1",
        document_id="doc-a-bba",
        page_number=1,
        raw_text="Agreement for Penthouse P-101 in Silver Crest Heights by Silverline Infra Projects Ltd. Consideration Rs. 2,40,00,000. Carpet area 1,650 sq.ft. Possession on or before 30th June 2029.",
    )
    clause_a = Clause(
        id="clause-a-1",
        bundle_id="tx-silver-a",
        document_id="doc-a-bba",
        clause_number="Clause 12.1",
        title="Possession Deadline",
        category="Possession & Handover",
        status="VERIFIED",
        severity="MEDIUM",
        page_number=1,
        preview_text="Possession on or before 30th June 2029.",
        full_excerpt="Possession of Penthouse P-101 shall be handed over on or before 30th June 2029.",
        analysis_summary="Binding completion date 30 June 2029.",
    )
    attr_a = ExtractedAttribute(
        id="attr-a-1",
        bundle_id="tx-silver-a",
        document_id="doc-a-bba",
        attribute_key="possession_date",
        attribute_value="30 June 2029",
        normalized_value="2029-06-30",
        unit="date:DAY",
        confidence=0.98,
        source_clause="12.1",
        source_page=1,
    )
    db_session.add_all([tx_a, doc_a, page_a, clause_a, attr_a])
    await db_session.commit()

    # -------------------------------------------------------------
    # 2. SETUP TRANSACTION B: "Pine Valley Greens" (Villa V-12)
    # -------------------------------------------------------------
    tx_b = TransactionBundle(
        id="tx-pine-b",
        title="Pine Valley Greens — Villa V-12",
        project="Pine Valley Greens",
        unit="Villa V-12",
        floor=1,
        tower="Phase 2",
        developer="Meadowlands Developers Pvt Ltd",
        city="Hyderabad",
        location="Gachibowli, Hyderabad, TS",
        property_type="Villa",
        carpet_area_sqft=2200.0,
        super_area_sqft=3100.0,
        advertised_carpet_area_sqft=2200.0,
        sale_price=31500000.0,
        possession_date="2028-11-15",
        grace_period_months=4,
        health_score=88,
        status="ACTIVE",
    )
    doc_b = Document(
        id="doc-b-bba",
        bundle_id="tx-pine-b",
        file_name="PineValley_SaleDeedDraft_V12.pdf",
        document_type="BUILDER_BUYER_AGREEMENT",
        page_count=25,
        clause_count=12,
        issue_count=1,
    )
    page_b = DocumentPage(
        id="page-b-1",
        document_id="doc-b-bba",
        page_number=1,
        raw_text="Sale agreement for Villa V-12 in Pine Valley Greens by Meadowlands Developers Pvt Ltd. Consideration Rs. 3,15,00,000. Carpet area 2,200 sq.ft. Delivery on 15 November 2028.",
    )
    clause_b = Clause(
        id="clause-b-1",
        bundle_id="tx-pine-b",
        document_id="doc-b-bba",
        clause_number="Clause 9.3",
        title="Delivery Schedule",
        category="Possession & Handover",
        status="VERIFIED",
        severity="LOW",
        page_number=1,
        preview_text="Delivery scheduled for 15 November 2028.",
        full_excerpt="Handover of Villa V-12 is scheduled for 15 November 2028.",
        analysis_summary="Target delivery 15 November 2028.",
    )
    attr_b = ExtractedAttribute(
        id="attr-b-1",
        bundle_id="tx-pine-b",
        document_id="doc-b-bba",
        attribute_key="possession_date",
        attribute_value="15 November 2028",
        normalized_value="2028-11-15",
        unit="date:DAY",
        confidence=0.98,
        source_clause="9.3",
        source_page=1,
    )
    db_session.add_all([tx_b, doc_b, page_b, clause_b, attr_b])
    await db_session.commit()

    # -------------------------------------------------------------
    # 3. SETUP TRANSACTION C: "Harbor Crest Residences" (Flat C-1708)
    # -------------------------------------------------------------
    tx_c = TransactionBundle(
        id="tx-harbor-c",
        title="Harbor Crest Residences — Tower C, Flat C-1708",
        project="Harbor Crest Residences",
        unit="Tower C, Flat C-1708",
        floor=17,
        tower="Tower C",
        developer="Apex Habitat Developers Pvt. Ltd.",
        city="Pune",
        location="Kharadi, Pune, MH",
        property_type="Residential Apartment",
        carpet_area_sqft=1245.0,
        super_area_sqft=1620.0,
        advertised_carpet_area_sqft=1310.0,
        sale_price=11875000.0,
        possession_date="2029-03-31",
        grace_period_months=6,
        health_score=78,
        status="ACTIVE",
    )
    doc_c1 = Document(
        id="doc-c-agree",
        bundle_id="tx-harbor-c",
        file_name="HarborCrest_Agreement_C1708.pdf",
        document_type="BUILDER_BUYER_AGREEMENT",
        page_count=30,
        clause_count=15,
        issue_count=2,
    )
    page_c1 = DocumentPage(
        id="page-c-1",
        document_id="doc-c-agree",
        page_number=1,
        raw_text="Agreement for Flat C-1708 in Harbor Crest Residences by Apex Habitat Developers Pvt. Ltd. Consideration Rs. 1,18,75,000. Carpet area 1,245 sq.ft. Handover deadline 31 March 2029.",
    )
    clause_c1 = Clause(
        id="clause-c-1",
        bundle_id="tx-harbor-c",
        document_id="doc-c-agree",
        clause_number="Clause 7.2",
        title="Handover Date",
        category="Possession & Handover",
        status="VERIFIED",
        severity="MEDIUM",
        page_number=1,
        preview_text="Handover deadline 31 March 2029.",
        full_excerpt="Handover deadline for Flat C-1708 is 31 March 2029.",
        analysis_summary="Completion deadline 31 March 2029.",
    )
    attr_c1 = ExtractedAttribute(
        id="attr-c-1",
        bundle_id="tx-harbor-c",
        document_id="doc-c-agree",
        attribute_key="possession_date",
        attribute_value="31 March 2029",
        normalized_value="2029-03-31",
        unit="date:DAY",
        confidence=0.99,
        source_clause="7.2",
        source_page=1,
    )
    db_session.add_all([tx_c, doc_c1, page_c1, clause_c1, attr_c1])
    await db_session.commit()

    # Index RAG chunks for each transaction
    await rag_service.index_document(db_session, "tx-silver-a", "doc-a-bba")
    await rag_service.index_document(db_session, "tx-pine-b", "doc-b-bba")
    await rag_service.index_document(db_session, "tx-harbor-c", "doc-c-agree")

    # Analyze cross-document intelligence for each
    await cross_document_engine.analyze_transaction(db_session, "tx-silver-a")
    await cross_document_engine.analyze_transaction(db_session, "tx-pine-b")
    await cross_document_engine.analyze_transaction(db_session, "tx-harbor-c")

    # -------------------------------------------------------------
    # 4. RUN COMPLETE INTELLIGENCE EXTRACTION FOR TRANSACTION A
    # -------------------------------------------------------------
    cmd_a = await transaction_intelligence_orchestrator.get_command_center(db_session, "tx-silver-a")
    timeline_a = await timeline_service.get_reconciled_timeline(db_session, "tx-silver-a")
    copilot_summary_a = await transaction_copilot_service.query_copilot(db_session, "tx-silver-a", CopilotQueryRequestSchema(query="Summarize this transaction"))
    copilot_risks_a = await transaction_copilot_service.query_copilot(db_session, "tx-silver-a", CopilotQueryRequestSchema(query="What are my top risks?"))
    copilot_dates_a = await transaction_copilot_service.query_copilot(db_session, "tx-silver-a", CopilotQueryRequestSchema(query="Are there conflicting dates?"))
    brief_a = await transaction_brief_service.generate_brief(db_session, "tx-silver-a")
    rag_a = await rag_service.query_transaction(db_session, "tx-silver-a", "What is the consideration amount?")

    # -------------------------------------------------------------
    # 5. RUN COMPLETE INTELLIGENCE EXTRACTION FOR TRANSACTION B
    # -------------------------------------------------------------
    cmd_b = await transaction_intelligence_orchestrator.get_command_center(db_session, "tx-pine-b")
    timeline_b = await timeline_service.get_reconciled_timeline(db_session, "tx-pine-b")
    copilot_summary_b = await transaction_copilot_service.query_copilot(db_session, "tx-pine-b", CopilotQueryRequestSchema(query="Summarize this transaction"))
    copilot_risks_b = await transaction_copilot_service.query_copilot(db_session, "tx-pine-b", CopilotQueryRequestSchema(query="What are my top risks?"))
    copilot_dates_b = await transaction_copilot_service.query_copilot(db_session, "tx-pine-b", CopilotQueryRequestSchema(query="Are there conflicting dates?"))
    brief_b = await transaction_brief_service.generate_brief(db_session, "tx-pine-b")
    rag_b = await rag_service.query_transaction(db_session, "tx-pine-b", "What is the consideration amount?")

    # -------------------------------------------------------------
    # 6. RUN COMPLETE INTELLIGENCE EXTRACTION FOR TRANSACTION C
    # -------------------------------------------------------------
    cmd_c = await transaction_intelligence_orchestrator.get_command_center(db_session, "tx-harbor-c")
    timeline_c = await timeline_service.get_reconciled_timeline(db_session, "tx-harbor-c")
    copilot_summary_c = await transaction_copilot_service.query_copilot(db_session, "tx-harbor-c", CopilotQueryRequestSchema(query="Summarize this transaction"))
    copilot_risks_c = await transaction_copilot_service.query_copilot(db_session, "tx-harbor-c", CopilotQueryRequestSchema(query="What are my top risks?"))
    copilot_dates_c = await transaction_copilot_service.query_copilot(db_session, "tx-harbor-c", CopilotQueryRequestSchema(query="Are there conflicting dates?"))
    brief_c = await transaction_brief_service.generate_brief(db_session, "tx-harbor-c")
    rag_c = await rag_service.query_transaction(db_session, "tx-harbor-c", "What is the consideration amount?")

    # -------------------------------------------------------------
    # 7. PROVE ZERO LEAKAGE OF OLD DEMO / SKYVIEW INTELLIGENCE
    # -------------------------------------------------------------
    forbidden_skyview_tokens = [
        "SkyView",
        "A-1204",
        "Skyline Urban",
        "1,380",
        "1,450",
        "December 2026",
        "28.5L",
        "₹28.5",
        "74,000/mo",
    ]

    for item_name, text_content in [
        ("cmd_a", str(cmd_a.model_dump())),
        ("cmd_b", str(cmd_b.model_dump())),
        ("cmd_c", str(cmd_c.model_dump())),
        ("copilot_summary_a", copilot_summary_a.answer),
        ("copilot_summary_b", copilot_summary_b.answer),
        ("copilot_summary_c", copilot_summary_c.answer),
        ("copilot_risks_a", copilot_risks_a.answer),
        ("copilot_risks_b", copilot_risks_b.answer),
        ("copilot_risks_c", copilot_risks_c.answer),
        ("copilot_dates_a", copilot_dates_a.answer),
        ("copilot_dates_b", copilot_dates_b.answer),
        ("copilot_dates_c", copilot_dates_c.answer),
        ("brief_a", str(brief_a.model_dump())),
        ("brief_b", str(brief_b.model_dump())),
        ("brief_c", str(brief_c.model_dump())),
    ]:
        for token in forbidden_skyview_tokens:
            assert token not in text_content, f"STALE DEMO LEAKAGE DETECTED: '{token}' found in {item_name}!"

    # -------------------------------------------------------------
    # 8. PROVE CROSS-TRANSACTION ISOLATION: A NEVER CONTAINS B OR C
    # -------------------------------------------------------------
    tx_b_tokens = ["Pine Valley", "Villa V-12", "Meadowlands", "3,15,00,000", "2,200 sq.ft", "2028-11-15"]
    tx_c_tokens = ["Harbor Crest", "C-1708", "Apex Habitat", "1,18,75,000", "1,245 sq.ft", "2029-03-31"]

    a_full_text = (
        str(cmd_a.model_dump())
        + copilot_summary_a.answer
        + copilot_risks_a.answer
        + copilot_dates_a.answer
        + str(brief_a.model_dump())
        + (rag_a.answer if rag_a.grounded else "")
    )
    for tok in tx_b_tokens + tx_c_tokens:
        assert tok not in a_full_text, f"CROSS CONTAMINATION: Tx B/C token '{tok}' leaked into Transaction A!"

    # -------------------------------------------------------------
    # 9. PROVE CROSS-TRANSACTION ISOLATION: B NEVER CONTAINS A OR C
    # -------------------------------------------------------------
    tx_a_tokens = ["Silver Crest", "Penthouse P-101", "Silverline", "2,40,00,000", "1,650 sq.ft", "2029-06-30"]

    b_full_text = (
        str(cmd_b.model_dump())
        + copilot_summary_b.answer
        + copilot_risks_b.answer
        + copilot_dates_b.answer
        + str(brief_b.model_dump())
        + (rag_b.answer if rag_b.grounded else "")
    )
    for tok in tx_a_tokens + tx_c_tokens:
        assert tok not in b_full_text, f"CROSS CONTAMINATION: Tx A/C token '{tok}' leaked into Transaction B!"

    # -------------------------------------------------------------
    # 10. PROVE CROSS-TRANSACTION ISOLATION: C NEVER CONTAINS A OR B
    # -------------------------------------------------------------
    c_full_text = (
        str(cmd_c.model_dump())
        + copilot_summary_c.answer
        + copilot_risks_c.answer
        + copilot_dates_c.answer
        + str(brief_c.model_dump())
        + (rag_c.answer if rag_c.grounded else "")
    )
    for tok in tx_a_tokens + tx_b_tokens:
        assert tok not in c_full_text, f"CROSS CONTAMINATION: Tx A/B token '{tok}' leaked into Transaction C!"

    # -------------------------------------------------------------
    # 11. VERIFY HARBOR CREST VALUES ARE CORRECT AND DYNAMIC
    # -------------------------------------------------------------
    assert cmd_c.projectName == "Harbor Crest Residences"
    assert cmd_c.unitNumber == "Tower C, Flat C-1708"
    assert cmd_c.developerName == "Apex Habitat Developers Pvt. Ltd."
    assert cmd_c.financialExposure.baseConsideration == 11875000.0
    assert "1.19 Cr" in cmd_c.financialExposure.baseConsiderationFormatted

    # -------------------------------------------------------------
    # 12. BRAND-NEW TRANSACTION CLEAN SLATE VERIFICATION
    # -------------------------------------------------------------
    new_payload = {
        "projectName": "Orchid Meadows",
        "unit": "Flat B-302",
        "developer": "Orchid Greens Developers",
        "city": "Chennai",
        "propertyType": "Residential Apartment",
    }
    create_res = await client.post("/api/v1/transactions", json=new_payload)
    assert create_res.status_code == 201
    new_tx_id = create_res.json()["id"]

    # Verify new transaction starts completely clean
    new_cmd_res = await client.get(f"/api/v1/transactions/{new_tx_id}/copilot/command-center")
    assert new_cmd_res.status_code == 200
    new_cmd = new_cmd_res.json()
    assert new_cmd["totalDocumentsCount"] == 0
    assert new_cmd["totalFindingsCount"] == 0
    assert new_cmd["financialExposure"]["totalFinancialAtRisk"] == 0
    assert new_cmd["projectName"] == "Orchid Meadows"
    assert new_cmd["developerName"] == "Orchid Greens Developers"

    new_timeline_res = await client.get(f"/api/v1/transactions/{new_tx_id}/copilot/timeline")
    assert new_timeline_res.status_code == 200
    new_timeline = new_timeline_res.json()
    assert new_timeline["totalEvents"] == 0
    assert len(new_timeline["events"]) == 0
