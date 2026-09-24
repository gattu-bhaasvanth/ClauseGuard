import pytest
from httpx import AsyncClient
import io


@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    """Verify production security headers are set on all responses."""
    res = await client.get("/api/v1/health")
    assert res.status_code == 200
    headers = res.headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("x-xss-protection") == "1; mode=block"
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"


@pytest.mark.asyncio
async def test_health_readiness_and_liveness_probes(client: AsyncClient):
    """Verify readiness and liveness endpoints for production orchestrators."""
    live_res = await client.get("/api/v1/health/live")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "alive"

    ready_res = await client.get("/api/v1/health/ready")
    assert ready_res.status_code == 200
    ready_data = ready_res.json()
    assert ready_data["ready"] is True
    assert ready_data["database"] == "ready"
    assert ready_data["storage"] == "ready"


@pytest.mark.asyncio
async def test_upload_validation_empty_file(client: AsyncClient):
    """Verify uploading an empty file is rejected with 400 Bad Request."""
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    data = {"document_type": "OTHER", "auto_extract_clauses": "false"}
    res = await client.post("/api/v1/transactions/skyview-a1204/documents/upload", files=files, data=data)
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_validation_unsupported_format(client: AsyncClient):
    """Verify uploading an unsupported file format (.exe, .zip) is rejected with 400 Bad Request."""
    files = {"file": ("malicious.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload")}
    data = {"document_type": "OTHER", "auto_extract_clauses": "false"}
    res = await client.post("/api/v1/transactions/skyview-a1204/documents/upload", files=files, data=data)
    assert res.status_code == 400
    assert "unsupported" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_validation_corrupt_pdf_magic_bytes(client: AsyncClient):
    """Verify uploading a non-PDF disguised as .pdf is rejected by magic byte validation."""
    files = {"file": ("corrupt.pdf", b"NOT_A_REAL_PDF_HEADER_12345", "application/pdf")}
    data = {"document_type": "OTHER", "auto_extract_clauses": "false"}
    res = await client.post("/api/v1/transactions/skyview-a1204/documents/upload", files=files, data=data)
    assert res.status_code == 400
    assert "magic header" in res.json()["detail"].lower() or "invalid" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_transaction_isolation_foreign_document(client: AsyncClient):
    """
    Verify cross-transaction isolation:
    A user requesting a document ID belonging to a different transaction bundle receives 404.
    """
    # Create a secondary test bundle
    create_payload = {
        "projectName": "Isolated Tower",
        "unit": "Unit B-999",
        "developer": "Isolated Builders",
        "city": "Bengaluru",
        "propertyType": "Residential Apartment",
        "approxPrice": 15000000.0,
    }
    create_res = await client.post("/api/v1/transactions", json=create_payload)
    assert create_res.status_code == 201
    bundle_b_id = create_res.json()["id"]

    # Attempt to query skyview-a1204's documents through bundle_b_id
    foreign_doc_id = "doc-bba-001"
    res_pages = await client.get(f"/api/v1/transactions/{bundle_b_id}/documents/{foreign_doc_id}/pages")
    assert res_pages.status_code == 404
    assert "not found" in res_pages.json()["detail"].lower()

    res_clauses = await client.get(f"/api/v1/transactions/{bundle_b_id}/documents/{foreign_doc_id}/clauses")
    assert res_clauses.status_code == 404

    res_meta = await client.get(f"/api/v1/transactions/{bundle_b_id}/documents/{foreign_doc_id}/metadata")
    assert res_meta.status_code == 404


@pytest.mark.asyncio
async def test_transaction_isolation_foreign_risk_finding(client: AsyncClient):
    """Verify explain-risk rejects finding IDs that do not belong to the transaction bundle."""
    res = await client.get("/api/v1/transactions/skyview-a1204/copilot/explain-risk/non-existent-risk-999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_ml_resilience_missing_model_fallback():
    """Verify that if the ML model is missing or fails, classification seamlessly falls back to heuristics."""
    from pathlib import Path
    from app.intelligence.taxonomy import ClauseCategory
    from app.intelligence.ml.local_inference_engine import LocalClauseIntelligenceEngine
    from app.intelligence.ml.hybrid_classifier import HybridClauseClassifier

    # Create engine instance with non-existent model path
    dummy_engine = LocalClauseIntelligenceEngine(model_path=Path("/tmp/non_existent_model_12345.json"))
    assert dummy_engine.is_loaded is False

    hybrid = HybridClauseClassifier()
    # Temporarily substitute ml engine with dummy
    orig_engine = hybrid.ml_engine
    try:
        hybrid.ml_engine = dummy_engine
        result = hybrid.classify_clause(
            title="Clause 11: Possession and Handover",
            text="The promoter shall complete construction and deliver physical possession of the apartment by Dec 2027.",
        )
        assert result is not None
        assert result.classification_source == "DETERMINISTIC_HEURISTIC"
        assert result.category == ClauseCategory.POSSESSION_TERMS
    finally:
        hybrid.ml_engine = orig_engine
