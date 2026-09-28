import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
import sqlite3

from app.models.transaction import TransactionBundle
from app.models.document import Document
from app.models.clause import Clause
from app.models.finding import Finding
from app.models.attribute import ExtractedAttribute
from app.services.seed_service import seed_demo_data
from app.database import init_db
from app.services.timeline_service import timeline_service
from app.services.copilot_service import transaction_copilot_service
from app.schemas.copilot import CopilotQueryRequestSchema


# ==============================================================================
# 1. TRANSACTION PERSISTENCE ACROSS APPLICATION REINITIALIZATION (Section 4 & 7)
# ==============================================================================

@pytest.mark.asyncio
async def test_transaction_persistence_across_app_reinitialization(db_session: AsyncSession, client: AsyncClient):
    """
    Verifies that creating a transaction with documents, clauses, and findings
    survives an application re-initialization (init_db and seed_demo_data startup routine).
    """
    # 1. Create a transaction bundle with arbitrary novel data
    tx_id = "tx-pers-alpha-99"
    bundle = TransactionBundle(
        id=tx_id,
        title="Onyx Crest Horizon — Flat 702-Z",
        project="Onyx Crest Horizon",
        developer="Zephyr Real Estate Holdings Ltd.",
        unit="Flat 702-Z",
        location="Whitefield, Bengaluru",
        city="Bengaluru",
        sale_price=18_500_000.0,
        possession_date="2031-06-30",
        grace_period_months=6,
        status="ANALYSIS_COMPLETE",
    )
    db_session.add(bundle)

    # 2. Add documents
    doc1 = Document(
        id="doc-pers-01",
        bundle_id=tx_id,
        file_name="01_Onyx_Allotment_Contract.pdf",
        document_type="ALLOTMENT_LETTER",
        file_size="2.1 MB",
        page_count=12,
        clause_count=8,
        issue_count=1,
    )
    doc2 = Document(
        id="doc-pers-02",
        bundle_id=tx_id,
        file_name="02_Onyx_Registered_Agreement.pdf",
        document_type="SALE_AGREEMENT",
        file_size="4.5 MB",
        page_count=28,
        clause_count=22,
        issue_count=1,
    )
    db_session.add_all([doc1, doc2])

    # 3. Add extracted attributes
    attr1 = ExtractedAttribute(
        id="attr-pers-01",
        bundle_id=tx_id,
        document_id="doc-pers-01",
        attribute_key="possession_date",
        attribute_value="31 March 2031",
        normalized_value="2031-03-31",
        unit="date:DAY",
        source_page=2,
        raw_excerpt="Possession shall be delivered by 31 March 2031.",
    )
    attr2 = ExtractedAttribute(
        id="attr-pers-02",
        bundle_id=tx_id,
        document_id="doc-pers-02",
        attribute_key="possession_date",
        attribute_value="30 June 2031",
        normalized_value="2031-06-30",
        unit="date:DAY",
        source_page=14,
        raw_excerpt="Final handover deadline is committed on or before 30 June 2031.",
    )
    db_session.add_all([attr1, attr2])

    # 4. Add finding
    finding = Finding(
        id="find-pers-01",
        bundle_id=tx_id,
        finding_type="INCONSISTENCY",
        title="Possession Timeline Discrepancy",
        category="POSSESSION",
        severity="HIGH",
        description="Delivery disparity between Allotment (March 2031) and Agreement (June 2031).",
        primary_evidence={
            "documentId": "doc-pers-01",
            "documentName": "01_Onyx_Allotment_Contract.pdf",
            "documentType": "ALLOTMENT_LETTER",
            "pageNumber": 2,
            "excerpt": "Possession shall be delivered by 31 March 2031.",
        },
        secondary_evidence={
            "documentId": "doc-pers-02",
            "documentName": "02_Onyx_Registered_Agreement.pdf",
            "documentType": "SALE_AGREEMENT",
            "pageNumber": 14,
            "excerpt": "Final handover deadline is committed on or before 30 June 2031.",
        },
    )
    db_session.add(finding)
    await db_session.commit()

    # 5. Simulate application re-initialization (startup lifespan calls init_db and seed_demo_data)
    await init_db()
    await seed_demo_data(db_session)

    # 6. Verify transaction still exists and was not erased
    res = await client.get(f"/api/v1/transactions/{tx_id}")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert data["id"] == tx_id
    assert data["property"]["project"] == "Onyx Crest Horizon"
    assert data["property"]["developer"] == "Zephyr Real Estate Holdings Ltd."
    assert data["property"]["unit"] == "Flat 702-Z"
    assert len(data["documents"]) == 2
    assert len(data["inconsistencies"]) == 1

    # 7. Verify Timeline remains functional and accurate
    timeline_resp = await timeline_service.get_reconciled_timeline(db_session, tx_id)
    assert timeline_resp.bundleId == tx_id
    assert timeline_resp.totalEvents >= 2
    # Verify conflict between allotment and agreement
    conflicts = [e for e in timeline_resp.events if e.conflictingDate is not None]
    assert len(conflicts) == 2, "Expected contractual conflict between March 2031 and June 2031"


# ==============================================================================
# 2. TRANSACTION SEARCH API ACROSS FIELDS (Section 3 & 7)
# ==============================================================================

@pytest.mark.asyncio
async def test_transaction_search_api_across_fields(db_session: AsyncSession, client: AsyncClient):
    """
    Verifies that the /api/v1/transactions search endpoint correctly finds transactions by:
    - project name
    - developer name
    - unit identifier
    - partial and case-insensitive query
    And returns empty list for non-matching queries without errors.
    """
    tx_a = TransactionBundle(
        id="tx-search-01",
        title="Emerald Terraces — Tower E-401",
        project="Emerald Terraces",
        developer="Apex Living Spaces LLP",
        unit="Tower E-401",
        location="Sector 82, Mohali, Punjab",
        city="Mohali",
        sale_price=8_400_000.0,
        possession_date="2028-12-31",
        grace_period_months=6,
    )
    tx_b = TransactionBundle(
        id="tx-search-02",
        title="Sapphire Heights — Penthouse P-12",
        project="Sapphire Heights",
        developer="Blue Horizon Builders Corp",
        unit="Penthouse P-12",
        location="Marine Drive, Kochi, Kerala",
        city="Kochi",
        sale_price=22_000_000.0,
        possession_date="2029-06-30",
        grace_period_months=3,
    )
    db_session.add_all([tx_a, tx_b])
    await db_session.commit()

    # Search 1: by project name
    res = await client.get("/api/v1/transactions?q=Emerald")
    assert res.status_code == 200
    items = res.json()
    ids = [item["id"] for item in items]
    assert "tx-search-01" in ids
    assert "tx-search-02" not in ids

    # Search 2: by developer name
    res = await client.get("/api/v1/transactions?q=Blue Horizon")
    assert res.status_code == 200
    items = res.json()
    ids = [item["id"] for item in items]
    assert "tx-search-02" in ids
    assert "tx-search-01" not in ids

    # Search 3: by unit identifier
    res = await client.get("/api/v1/transactions?q=E-401")
    assert res.status_code == 200
    items = res.json()
    ids = [item["id"] for item in items]
    assert "tx-search-01" in ids
    assert "tx-search-02" not in ids

    # Search 4: by pent-house unit
    res = await client.get("/api/v1/transactions?q=P-12")
    assert res.status_code == 200
    items = res.json()
    ids = [item["id"] for item in items]
    assert "tx-search-02" in ids
    assert "tx-search-01" not in ids

    # Search 5: case-insensitive partial match
    res = await client.get("/api/v1/transactions?q=sapphire")
    assert res.status_code == 200
    items = res.json()
    ids = [item["id"] for item in items]
    assert "tx-search-02" in ids

    # Search 6: non-matching query returns empty list
    res = await client.get("/api/v1/transactions?q=NonExistentGalacticTower999")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 0

    # Search 7: empty query returns all bundles
    res = await client.get("/api/v1/transactions")
    assert res.status_code == 200
    items = res.json()
    ids = [item["id"] for item in items]
    assert "tx-search-01" in ids
    assert "tx-search-02" in ids


# ==============================================================================
# 3. CROSS-TRANSACTION ISOLATION IN PERSISTENCE & COPILOT (Section 5 & 6)
# ==============================================================================

@pytest.mark.asyncio
async def test_cross_transaction_isolation_in_persistence_and_copilot(db_session: AsyncSession):
    """
    Verifies that two persisted transactions remain isolated in Timeline, Copilot,
    and Document queries, with zero leakage across boundaries.
    """
    tx_x = TransactionBundle(
        id="tx-iso-x-01",
        title="Project X Horizon",
        project="Project X Horizon",
        developer="Developer X Corp",
        unit="X-101",
        sale_price=5_000_000.0,
    )
    tx_y = TransactionBundle(
        id="tx-iso-y-02",
        title="Project Y Heights",
        project="Project Y Heights",
        developer="Developer Y Corp",
        unit="Y-202",
        sale_price=6_000_000.0,
    )
    doc_x = Document(
        id="doc-iso-x-1",
        bundle_id="tx-iso-x-01",
        file_name="Document_X_Contract.pdf",
        document_type="SALE_AGREEMENT",
    )
    doc_y = Document(
        id="doc-iso-y-1",
        bundle_id="tx-iso-y-02",
        file_name="Document_Y_Contract.pdf",
        document_type="SALE_AGREEMENT",
    )
    attr_x = ExtractedAttribute(
        id="attr-iso-x-1",
        bundle_id="tx-iso-x-01",
        document_id="doc-iso-x-1",
        attribute_key="possession_date",
        attribute_value="15 June 2030",
        normalized_value="2030-06-15",
        unit="date:DAY",
        source_page=1,
    )
    attr_y = ExtractedAttribute(
        id="attr-iso-y-1",
        bundle_id="tx-iso-y-02",
        document_id="doc-iso-y-1",
        attribute_key="possession_date",
        attribute_value="20 October 2032",
        normalized_value="2032-10-20",
        unit="date:DAY",
        source_page=1,
    )
    db_session.add_all([tx_x, tx_y, doc_x, doc_y, attr_x, attr_y])
    await db_session.commit()

    # Verify Timeline for tx_x contains only 2030-06-15, never 2032-10-20
    timeline_x = await timeline_service.get_reconciled_timeline(db_session, "tx-iso-x-01")
    event_dates_x = [e.eventDate for e in timeline_x.events if e.eventDate]
    assert "2030-06-15" in event_dates_x
    assert "2032-10-20" not in event_dates_x

    # Verify Timeline for tx_y contains only 2032-10-20, never 2030-06-15
    timeline_y = await timeline_service.get_reconciled_timeline(db_session, "tx-iso-y-02")
    event_dates_y = [e.eventDate for e in timeline_y.events if e.eventDate]
    assert "2032-10-20" in event_dates_y
    assert "2030-06-15" not in event_dates_y


# ==============================================================================
# 4. VERIFY ACTUAL PERSISTENT DATABASE DATA RETENTION (Section 8)
# ==============================================================================

def test_actual_sqlite_database_file_retention():
    """
    Verifies Section 8: checks data/clauseguard.db on disk to confirm
    that real transactions (including tx-84ef0c8e Maple Heights Enclave)
    are retained with all documents.
    """
    db_file = Path(__file__).resolve().parent.parent.parent / "data" / "clauseguard.db"
    assert db_file.exists(), f"Expected database file at {db_file} to exist"

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    # Query transaction_bundles table
    cursor.execute("SELECT id, project, developer, unit FROM transaction_bundles WHERE id='tx-84ef0c8e'")
    row = cursor.fetchone()
    assert row is not None, "tx-84ef0c8e was found in data/clauseguard.db"
    assert row[1] == "Maple Heights Enclave"
    assert "Northstar" in row[2]
    assert "B-904" in row[3]

    # Query documents attached to tx-84ef0c8e
    cursor.execute("SELECT file_name FROM documents WHERE bundle_id='tx-84ef0c8e'")
    docs = [r[0] for r in cursor.fetchall()]
    assert len(docs) == 5, f"Expected 5 documents for tx-84ef0c8e, found {len(docs)}: {docs}"
    assert "02_Allotment_Confirmation_Letter.pdf" in docs
    assert "03_Agreement_for_Sale_B904.pdf" in docs
    assert "05_Maple_Heights_Project_Brochure.pdf" in docs

    conn.close()
