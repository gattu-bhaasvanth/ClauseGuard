import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_transaction_documents(client: AsyncClient):
    response = await client.get("/api/v1/transactions/skyview-a1204/documents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4
    file_names = [d["fileName"] for d in data]
    assert "Builder_Buyer_Agreement_SkyView_A1204.pdf" in file_names


@pytest.mark.asyncio
async def test_register_document(client: AsyncClient):
    payload = {
        "file_name": "Sanction_Plan_Approval.pdf",
        "document_type": "NOC_SANCTION_PLAN",
        "file_path": "/data/uploads/Sanction_Plan_Approval.pdf",
        "file_size": "2.4 MB",
        "page_count": 8,
    }
    response = await client.post(
        "/api/v1/transactions/skyview-a1204/documents", json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["fileName"] == "Sanction_Plan_Approval.pdf"
    assert data["documentType"] == "NOC_SANCTION_PLAN"
    assert data["pageCount"] == 8
