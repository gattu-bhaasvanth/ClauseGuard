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
