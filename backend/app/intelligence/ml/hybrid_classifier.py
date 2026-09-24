"""
ClauseGuard Phase 9: Hybrid Clause Classifier
Coordinates between the local ML inference engine and the Phase 4 deterministic classifier.
Preserves 100% deterministic fallback and statutory risk evaluation rules.
"""

import logging
from typing import Optional, List, Dict, Any

from app.intelligence.classifier import ClauseClassifier, ClassificationResult
from app.intelligence.taxonomy import ClauseCategory
from app.intelligence.ml.local_inference_engine import local_intelligence_engine, MLPrediction

logger = logging.getLogger(__name__)

# Minimum calibrated confidence threshold required to adopt ML prediction
CONFIDENCE_THRESHOLD = 0.60


class HybridClauseClassifier:
    """
    Dual-engine real-estate clause intelligence coordinator.
    - Utilizes local ML semantic manifold prototype inference when confidence >= 0.60.
    - Transparently falls back to Phase 4 keyword/regex heuristics when ML is uncertain or unavailable.
    - Retains deterministic statutory risk evaluation rules (_evaluate_risk) at all times.
    """

    def __init__(self):
        self.heuristic_classifier = ClauseClassifier()
        self.ml_engine = local_intelligence_engine

    def classify_clause(self, title: str, text: str) -> ClassificationResult:
        # 1. Attempt local ML inference
        ml_prediction: Optional[MLPrediction] = None
        try:
            ml_prediction = self.ml_engine.predict(title, text)
        except Exception as e:
            logger.warning(f"ML classification failed, falling back to heuristics: {e}")
            ml_prediction = None

        # 2. Check if ML prediction meets acceptance criteria
        if ml_prediction is not None and ml_prediction.confidence >= CONFIDENCE_THRESHOLD:
            try:
                # Map category string to ClauseCategory enum
                ml_cat = ClauseCategory(ml_prediction.primary_category)

                # 3. Always apply Phase 4 statutory risk evaluation
                risk_result = self.heuristic_classifier._evaluate_risk(
                    category=ml_cat,
                    confidence=ml_prediction.confidence,
                    text=text,
                )

                # Return enhanced ML result with statutory risk assessment
                return ClassificationResult(
                    category=ml_cat,
                    confidence=ml_prediction.confidence,
                    status=risk_result.status,
                    severity=risk_result.severity,
                    analysis_summary=risk_result.analysis_summary,
                    risk_details=risk_result.risk_details,
                    classification_source="ML_TRANSFORMER",
                    model_version=ml_prediction.model_version,
                    dataset_version=ml_prediction.dataset_version,
                    top_alternatives=ml_prediction.top_alternatives,
                    explanation_notes=ml_prediction.explanation_notes,
                )
            except ValueError:
                logger.warning(f"Unrecognized category '{ml_prediction.primary_category}', falling back to heuristics.")

        # 4. Safe Fallback: Execute Phase 4 Deterministic Classifier
        fallback_res = self.heuristic_classifier.classify_clause(title, text)
        fallback_res.classification_source = "DETERMINISTIC_HEURISTIC"
        fallback_res.model_version = "heuristic-v1"
        fallback_res.dataset_version = "taxonomy-v1"
        fallback_res.top_alternatives = []
        fallback_res.explanation_notes = (
            f"Classified using Phase 4 deterministic keyword heuristics (confidence < {CONFIDENCE_THRESHOLD*100:.0f}% or ML unavailable)."
        )
        return fallback_res


hybrid_clause_classifier = HybridClauseClassifier()
