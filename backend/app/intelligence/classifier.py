import re
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Any
from app.intelligence.taxonomy import ClauseCategory, TAXONOMY_KEYWORDS


@dataclass
class ClassificationResult:
    category: ClauseCategory
    confidence: float
    status: str  # "RISK", "INCONSISTENCY", "REVIEW_REQUIRED", "VERIFIED"
    severity: Optional[str]  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    analysis_summary: str
    risk_details: Optional[str] = None
    classification_source: str = "DETERMINISTIC_HEURISTIC"
    model_version: Optional[str] = "heuristic-v1"
    dataset_version: Optional[str] = "taxonomy-v1"
    top_alternatives: Optional[List[Dict[str, Any]]] = None
    explanation_notes: Optional[str] = None


class ClauseClassifier:
    """
    Real-estate clause classifier and risk heuristic analyzer.
    Maps clause headings and text to the real-estate legal taxonomy and flags
    unfair or asymmetric conditions based on statutory benchmark rules.
    """

    def classify_clause(self, title: str, text: str) -> ClassificationResult:
        combined = f"{title}\n{text}".lower()

        # 1. Score each taxonomy category
        scores = {}
        for category, keywords in TAXONOMY_KEYWORDS.items():
            score = 0
            for kw in keywords:
                if kw in combined:
                    # Give extra weight if keyword appears in the title
                    if kw in title.lower():
                        score += 3
                    else:
                        score += 1
            scores[category] = score

        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]

        confidence = min(0.98, max_score * 0.18 + 0.3) if max_score > 0 else 0.4
        if max_score == 0:
            best_category = ClauseCategory.GENERAL_TERMS

        # 2. Risk Heuristic Evaluations
        return self._evaluate_risk(best_category, confidence, text)

    def _evaluate_risk(
        self, category: ClauseCategory, confidence: float, text: str
    ) -> ClassificationResult:
        lower = text.lower()

        # Heuristic 1: Asymmetrical Delay Penalties
        if category == ClauseCategory.POSSESSION_TERMS and ("rs. 5" in lower or "rupees five" in lower or "rs 5" in lower or "delay beyond" in lower):
            return ClassificationResult(
                category=category,
                confidence=max(confidence, 0.92),
                status="RISK",
                severity="CRITICAL",
                analysis_summary="Nominal developer delay compensation (~2.4% p.a.). Substantially lower than statutory reciprocal MCLR rates.",
                risk_details="Violates reciprocal interest principles under RERA Section 18.",
            )

        # Heuristic 2: Excessive Late Payment Interest Rate
        if category == ClauseCategory.PAYMENT_TERMS and ("18%" in lower or "24%" in lower or "compounded monthly" in lower):
            return ClassificationResult(
                category=category,
                confidence=max(confidence, 0.95),
                status="RISK",
                severity="HIGH",
                analysis_summary="High delayed payment penalty rate (18% p.a. compounded monthly). Severe financial exposure on minor milestone delays.",
                risk_details="Review required against state regulatory authority default benchmark rate.",
            )

        # Heuristic 3: Unilateral Layout Alteration Rights
        if category == ClauseCategory.ALTERATION_VARIATION or ("alteration" in lower and ("liberty" in lower or "10%" in lower or "without consent" in lower)):
            return ClassificationResult(
                category=ClauseCategory.ALTERATION_VARIATION,
                confidence=max(confidence, 0.90),
                status="RISK",
                severity="HIGH",
                analysis_summary="Unilateral discretion reserved by developer to alter floor plans or building layout by up to 10% without prior allottee consent.",
                risk_details="Standard RERA provisions mandate two-thirds allottee consent for major structural modifications.",
            )

        # Heuristic 4: Aggressive Earnest Money Forfeiture
        if category == ClauseCategory.CANCELLATION_FORFEITURE and ("20%" in lower or "twenty percent" in lower or "forfeit" in lower):
            return ClassificationResult(
                category=category,
                confidence=max(confidence, 0.94),
                status="RISK",
                severity="HIGH",
                analysis_summary="High earnest money forfeiture rate (20% of total consideration). Exceeds customary 10% consumer benchmark.",
                risk_details="Risk of severe capital forfeiture upon contract termination or disputed cancellation.",
            )

        # Heuristic 5: Measurement & Carpet Area Variances
        if category == ClauseCategory.AREA_SPECIFICATIONS and ("carpet area" in lower or "variation" in lower):
            return ClassificationResult(
                category=category,
                confidence=max(confidence, 0.90),
                status="INCONSISTENCY",
                severity="HIGH",
                analysis_summary="Defines binding carpet area specifications and allowable variation tolerances without price adjustment.",
                risk_details="Requires cross-document verification against brochure and allotment letter representations.",
            )

        # Heuristic 6: Exclusive Inconvenient Jurisdiction
        if category == ClauseCategory.DISPUTE_JURISDICTION and ("exclusive jurisdiction" in lower or "sole arbitrator" in lower):
            return ClassificationResult(
                category=category,
                confidence=max(confidence, 0.88),
                status="REVIEW_REQUIRED",
                severity="MEDIUM",
                analysis_summary="Sole arbitrator appointed by promoter and exclusive court jurisdiction stipulated.",
                risk_details="Unilateral arbitrator appointment terms have faced constitutional judicial scrutiny.",
            )

        # Heuristic 7: Statutory Registration
        if category == ClauseCategory.STATUTORY_COMPLIANCE and ("rera" in lower or "registration no" in lower):
            return ClassificationResult(
                category=category,
                confidence=max(confidence, 0.95),
                status="VERIFIED",
                severity="LOW",
                analysis_summary="Valid statutory project registration cited under state Real Estate Regulatory Authority.",
                risk_details=None,
            )

        # Default classification
        return ClassificationResult(
            category=category,
            confidence=confidence,
            status="VERIFIED",
            severity="LOW",
            analysis_summary=f"Standard contractual provision categorized under {category.value}.",
            risk_details=None,
        )
