import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_command_center(client: AsyncClient):
    """Tests GET /api/v1/transactions/{id}/copilot/command-center."""
    res = await client.get("/api/v1/transactions/skyview-a1204/copilot/command-center")
    assert res.status_code == 200
    data = res.json()
    assert data["bundleId"] == "skyview-a1204"
    assert data["healthScore"] == 74
    assert len(data["riskVectors"]) == 5
    assert len(data["priorityActions"]) >= 5
    assert data["financialExposure"]["baseConsideration"] == 14250000.0


@pytest.mark.asyncio
async def test_api_copilot_query_grounded(client: AsyncClient):
    """Tests POST /api/v1/transactions/{id}/copilot/query with grounded question."""
    payload = {"query": "What happens if the builder delays handover beyond December 2027?"}
    res = await client.post("/api/v1/transactions/skyview-a1204/copilot/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["grounded"] is True
    assert data["refused"] is False
    assert len(data["citations"]) >= 1
    assert "Clause 8.2" in data["answer"]


@pytest.mark.asyncio
async def test_api_copilot_query_refused(client: AsyncClient):
    """Tests POST /api/v1/transactions/{id}/copilot/query with unevidenced question triggers refusal."""
    payload = {"query": "What is the developer's CEO personal home address and phone number?"}
    res = await client.post("/api/v1/transactions/skyview-a1204/copilot/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["grounded"] is False
    assert data["refused"] is True
    assert data["citations"] == []
    assert "could not find evidence" in data["answer"]


@pytest.mark.asyncio
async def test_api_explain_risk(client: AsyncClient):
    """Tests GET /api/v1/transactions/{id}/copilot/explain-risk/{finding_id}."""
    res = await client.get("/api/v1/transactions/skyview-a1204/copilot/explain-risk/risk-01")
    assert res.status_code == 200
    data = res.json()
    assert data["findingId"] == "risk-01"
    assert "Section 18" in data["statutoryBenchmark"] or "RERA" in data["statutoryBenchmark"]
    assert data["lineage"]["documentName"] == "Builder_Buyer_Agreement_SkyView_A1204.pdf"
    assert data["lineage"]["pageNumber"] == 15


@pytest.mark.asyncio
async def test_api_timeline(client: AsyncClient):
    """Tests GET /api/v1/transactions/{id}/copilot/timeline."""
    res = await client.get("/api/v1/transactions/skyview-a1204/copilot/timeline")
    assert res.status_code == 200
    data = res.json()
    assert data["totalEvents"] >= 6
    assert data["contractualEventsCount"] >= 1
    assert data["marketingEventsCount"] >= 1
    assert data["conflictingEventsCount"] >= 1


@pytest.mark.asyncio
async def test_api_brief_and_pdf(client: AsyncClient):
    """Tests GET /api/v1/transactions/{id}/copilot/brief and brief/pdf."""
    # JSON Brief
    res_json = await client.get("/api/v1/transactions/skyview-a1204/copilot/brief")
    assert res_json.status_code == 200
    brief = res_json.json()
    assert len(brief["sections"]) == 7

    # PDF Download
    res_pdf = await client.get("/api/v1/transactions/skyview-a1204/copilot/brief/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 1000
    assert res_pdf.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_api_nonexistent_transaction(client: AsyncClient):
    """Tests 404 response on invalid transaction ID."""
    res = await client.get("/api/v1/transactions/nonexistent-bundle/copilot/command-center")
    assert res.status_code == 404
