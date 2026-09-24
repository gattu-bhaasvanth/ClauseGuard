"""
Unit tests for ClauseGuard Phase 9: Hybrid Intelligence Engine & Local Inference.
Verifies:
1. Normal ML classification with calibrated confidence and top alternatives.
2. Deterministic Phase 4 risk protection preservation.
3. Fallback when confidence is below 0.60 threshold.
4. Fallback when model file is missing/corrupted.
5. Live FastAPI intelligence API endpoints (/engine-status, /benchmarks, /classify).
"""

from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.intelligence.ml.hybrid_classifier import HybridClauseClassifier, hybrid_clause_classifier
from app.intelligence.taxonomy import ClauseCategory
from app.intelligence.ml.local_inference_engine import MLPrediction


@pytest.fixture
def client():
    return TestClient(app)


def test_hybrid_classifier_normal_inference():
    """Test high-confidence classification via Candidate C prototype model."""
    title = "Clause 8.2: Delivery of Possession and Handover"
    text = (
        "The Promoter shall complete construction of the Apartment and offer physical "
        "possession to the Allottee on or before 31st December 2026, with a grace period of 6 months."
    )
    result = hybrid_clause_classifier.classify_clause(title, text)

    assert result.category == ClauseCategory.POSSESSION_TERMS or result.category.value == "Possession & Handover"
    assert result.confidence is not None
    assert result.confidence >= 0.60
    assert result.classification_source == "ML_TRANSFORMER"
    assert result.model_version in ["v1.0.0", "cg-intel-v1.0.0"]
    assert result.dataset_version == "cg-statutory-corpus-v1.0"
    assert isinstance(result.top_alternatives, list)
    assert len(result.top_alternatives) > 0
    for alt in result.top_alternatives:
        assert "category" in alt
        assert "probability" in alt
    assert result.explanation_notes is not None


def test_deterministic_statutory_risk_preservation():
    """
    Ensure the deterministic Phase 4 statutory risk engine cannot be bypassed by ML.
    Asymmetric late fee (18% p.a.) must still trigger RISK and HIGH severity.
    """
    title = "Clause 5.3: Payment Default & Interest Rate"
    text = (
        "If the Allottee fails to pay any installment on or before the due date, the Allottee "
        "shall be liable to pay interest on delayed payment at the rate of 18% per annum compounded monthly."
    )
    result = hybrid_clause_classifier.classify_clause(title, text)

    assert result.category == ClauseCategory.PAYMENT_TERMS or result.category.value == "Payment Milestones & Delay Interest"
    assert result.status == "RISK"
    assert result.severity == "HIGH"
    assert "18% p.a." in (result.analysis_summary or "")
    assert "benchmark" in (result.risk_details or "").lower()


def test_deterministic_delay_penalty_risk_preservation():
    """
    Builder delay penalty of Rs. 5/sq.ft/month must be flagged as CRITICAL risk.
    """
    title = "Clause 8.2: Possession Handover & Delay Penalty"
    text = (
        "In the event of delay in offering possession of the Apartment beyond the agreed date "
        "and grace period of 180 days, the Promoter shall pay compensation at the rate of Rs. 5/- "
        "per sq. ft. of super area per month for the period of delay."
    )
    result = hybrid_clause_classifier.classify_clause(title, text)

    assert result.status == "RISK"
    assert result.severity == "CRITICAL"
    assert "reciprocal" in (result.risk_details or "").lower()


def test_low_confidence_fallback_to_heuristics():
    """
    When ML prediction confidence is below the 0.60 threshold, system must fall back
    to Phase 4 heuristics with deterministic attribution.
    """
    classifier = HybridClauseClassifier()
    low_conf_pred = MLPrediction(
        primary_category="Possession & Handover",
        confidence=0.45,
        top_alternatives=[],
        explanation_notes="Uncertain match",
        model_version="cg-intel-v1.0.0",
        dataset_version="cg-statutory-corpus-v1.0",
        latency_ms=0.01,
    )

    with patch.object(classifier.ml_engine, "predict", return_value=low_conf_pred):
        title = "Clause 14.1: Cancellation and Refund"
        text = (
            "In case of cancellation or termination of this Agreement by the Allottee, "
            "the Promoter shall forfeit twenty percent (20%) of the Total Consideration."
        )
        result = classifier.classify_clause(title, text)

        assert result.classification_source == "DETERMINISTIC_HEURISTIC"
        assert result.model_version == "heuristic-v1"
        assert "Phase 4 deterministic keyword heuristics" in (result.explanation_notes or "")


def test_missing_model_graceful_fallback():
    """
    If the model file fails to load or inference raises an exception,
    the hybrid classifier must cleanly fall back to Phase 4 heuristics with zero crashes.
    """
    classifier = HybridClauseClassifier()
    # Mock inference engine to simulate a failure
    with patch.object(classifier.ml_engine, "predict", side_effect=RuntimeError("Model file missing")):
        title = "Clause 18.4: Dispute Resolution & Jurisdiction"
        text = (
            "Any dispute arising out of this Agreement shall be referred to sole arbitration "
            "appointed by the Promoter. Courts at New Delhi alone shall have exclusive jurisdiction."
        )
        result = classifier.classify_clause(title, text)

        assert result.classification_source == "DETERMINISTIC_HEURISTIC"
        assert result.category == ClauseCategory.DISPUTE_JURISDICTION or result.category.value == "Dispute Resolution & Jurisdiction"
        assert "Phase 4 deterministic keyword heuristics" in (result.explanation_notes or "")


def test_api_intelligence_engine_status(client):
    """Test GET /api/v1/intelligence/engine-status endpoint."""
    res = client.get("/api/v1/intelligence/engine-status")
    assert res.status_code == 200
    data = res.json()
    assert data["active_engine"] == "HYBRID_ML_PROTOTYPE"
    assert data["fallback_available"] is True
    assert data["baseline_macro_f1"] == 0.572
    assert round(data["current_macro_f1"], 4) == 0.8788
    assert data["improvement_delta_f1"] == 0.3068
    assert len(data["categories"]) == 11


def test_api_intelligence_benchmarks(client):
    """Test GET /api/v1/intelligence/benchmarks endpoint."""
    res = client.get("/api/v1/intelligence/benchmarks")
    assert res.status_code == 200
    data = res.json()
    assert "candidates" in data
    assert data["promotion_gate_passed"] is True
    assert data["selected_model"] == "candidate_c_prototype"
    assert data["improvement_delta_f1"] == 0.3068


def test_api_intelligence_classify_preview(client):
    """Test POST /api/v1/intelligence/classify live interactive sandbox."""
    payload = {
        "title": "Clause 4.1: Variation in Carpet Area",
        "text": (
            "The Allottee agrees that the Apartment has a RERA Carpet Area of 1,380 sq. ft. "
            "The Promoter reserves the right to make architectural adjustments resulting in "
            "up to ±3% variation in carpet area without alteration to the agreed Total Consideration."
        ),
    }
    res = client.post("/api/v1/intelligence/classify", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["primary_category"] == "Carpet Area & Measurement Adjustments"
    assert data["confidence"] >= 0.60
    assert len(data["top_alternatives"]) > 0
    assert data["classification_source"] == "ML_TRANSFORMER"
