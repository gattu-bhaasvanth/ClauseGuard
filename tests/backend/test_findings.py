import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_findings(client: AsyncClient):
    response = await client.get("/api/v1/transactions/skyview-a1204/findings")
    assert response.status_code == 200
    data = response.json()
    assert "inconsistencies" in data
    assert "risks" in data
    assert len(data["inconsistencies"]) == 2
    # Verify carpet area inconsistency
    area_inc = next(i for i in data["inconsistencies"] if i["category"] == "AREA")
    assert area_inc["title"] == "Carpet Area Discrepancy"
    assert "1450 sq.ft" in area_inc["primaryEvidence"]["excerpt"]
    assert "1,380 sq. ft." in area_inc["secondaryEvidence"]["excerpt"]


@pytest.mark.asyncio
async def test_get_clauses(client: AsyncClient):
    response = await client.get("/api/v1/transactions/skyview-a1204/clauses")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    clause_numbers = [c["clauseNumber"] for c in data]
    assert "Clause 8.2" in clause_numbers
    assert "Clause 5.3" in clause_numbers
