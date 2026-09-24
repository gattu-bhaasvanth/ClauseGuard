import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_transactions(client: AsyncClient):
    response = await client.get("/api/v1/transactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    # Check that SkyView Residency is present
    titles = [t["title"] for t in data]
    assert any("SkyView" in t for t in titles)


@pytest.mark.asyncio
async def test_get_transaction_by_id(client: AsyncClient):
    response = await client.get("/api/v1/transactions/skyview-a1204")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "skyview-a1204"
    assert data["property"]["project"] == "SkyView Residency"
    assert data["property"]["unit"] == "Flat A-1204"
    assert data["property"]["carpetAreaSqFt"] == 1380.0
    assert data["property"]["advertisedCarpetAreaSqFt"] == 1450.0
    assert data["healthScore"] == 74
    assert len(data["documents"]) == 4
    assert len(data["inconsistencies"]) == 2
    assert len(data["risks"]) >= 2


@pytest.mark.asyncio
async def test_get_nonexistent_transaction(client: AsyncClient):
    response = await client.get("/api/v1/transactions/nonexistent-id")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_create_transaction(client: AsyncClient):
    payload = {
        "projectName": "Emerald Heights",
        "unit": "Tower C-501",
        "developer": "Emerald Developers Ltd.",
        "city": "Pune",
        "propertyType": "Residential Apartment",
        "approxPrice": 12500000.0,
        "carpetAreaSqFt": 1150.0,
        "superAreaSqFt": 1500.0,
    }
    response = await client.post("/api/v1/transactions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "tx-" in data["id"]
    assert data["property"]["project"] == "Emerald Heights"
    assert data["property"]["unit"] == "Tower C-501"
    assert data["property"]["salePrice"] == 12500000.0


@pytest.mark.asyncio
async def test_new_transaction_does_not_inherit_demo_documents(client: AsyncClient):
    """Regression test: new transaction does not inherit demo documents/configuration."""
    payload = {
        "projectName": "Test Residency",
        "unit": "Flat B-204",
        "developer": "Test Developers Pvt. Ltd.",
        "city": "Hyderabad, Telangana",
        "propertyType": "Residential Apartment",
        "approxPrice": 7500000.0,
        "carpetAreaSqFt": 1200.0,
        "superAreaSqFt": 1600.0,
    }
    # 1. Create transaction
    create_res = await client.post("/api/v1/transactions", json=payload)
    assert create_res.status_code == 201
    tx = create_res.json()
    tx_id = tx["id"]

    # Verify new transaction starts with ZERO documents
    assert len(tx["documents"]) == 0
    assert tx["documents"] == []

    # 2. Upload/register 1 custom document
    doc_payload = {
        "file_name": "ClauseGuard_Test_Transaction_Agreement.pdf",
        "document_type": "agreement_sale",
        "file_size": "1.0 MB",
        "page_count": 10,
    }
    doc_res = await client.post(f"/api/v1/transactions/{tx_id}/documents", json=doc_payload)
    assert doc_res.status_code == 201
    doc_data = doc_res.json()
    assert doc_data["fileName"] == "ClauseGuard_Test_Transaction_Agreement.pdf"

    # 3. Retrieve transaction and verify it only has 1 document and no SkyView demo data
    get_res = await client.get(f"/api/v1/transactions/{tx_id}")
    assert get_res.status_code == 200
    tx_updated = get_res.json()
    assert len(tx_updated["documents"]) == 1
    assert tx_updated["documents"][0]["fileName"] == "ClauseGuard_Test_Transaction_Agreement.pdf"
    assert tx_updated["documents"][0]["documentType"] == "agreement_sale"

    # Ensure no SkyView files leaked into the document list
    doc_names = [d["fileName"] for d in tx_updated["documents"]]
    assert "Builder_Buyer_Agreement_SkyView_A1204.pdf" not in doc_names
    assert "Allotment_Letter_Signed_A1204.pdf" not in doc_names
    assert "Sales_Brochure_SkyView_Residency.pdf" not in doc_names

    # 4. Check timeline, command center, and brief do not leak SkyView dates or events
    timeline_res = await client.get(f"/api/v1/transactions/{tx_id}/copilot/timeline")
    assert timeline_res.status_code == 200
    timeline_data = timeline_res.json()
    for ev in timeline_data.get("events", []):
        assert "SkyView" not in ev.get("title", "")
        assert "SkyView" not in ev.get("description", "")

    # 5. Check command center priority actions do not hardcode SkyView documents
    cmd_res = await client.get(f"/api/v1/transactions/{tx_id}/copilot/command-center")
    assert cmd_res.status_code == 200
    cmd_data = cmd_res.json()
    for act in cmd_data.get("priorityActions", []):
        assert "SkyView" not in act.get("targetDocument", "")

    # 6. Check brief sections do not leak SkyView citations
    brief_res = await client.get(f"/api/v1/transactions/{tx_id}/copilot/brief")
    assert brief_res.status_code == 200
    brief_data = brief_res.json()
    assert brief_data["project"] == "Test Residency"
    assert brief_data["unit"] == "Flat B-204"
    for sec in brief_data.get("sections", []):
        for lineage in sec.get("evidenceLineage", []):
            assert "SkyView" not in lineage.get("document", "")

