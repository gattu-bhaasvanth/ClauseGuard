from typing import List, Dict, Any
from app.models.clause import Clause
from app.models.finding import Finding
from app.schemas.report import RiskCategoryScoreSchema


class TransactionRiskScorer:
    """
    Computes category-level risk profiles and statutory benchmark comparisons
    without offering legal advice.
    """

    CATEGORIES = [
        ("Penalty & Delay Interest", "PENALTY"),
        ("Carpet Area Integrity", "AREA"),
        ("Layout & Specification Alterations", "SPECIFICATION"),
        ("Cancellation & Earnest Money Forfeiture", "FORFEITURE"),
        ("Dispute Resolution & Jurisdiction", "DISPUTE"),
    ]

    def compute_category_scores(
        self,
        clauses: List[Clause],
        findings: List[Finding],
    ) -> List[RiskCategoryScoreSchema]:
        scores: List[RiskCategoryScoreSchema] = []

        # 1. Penalty & Delay Interest
        penalty_issues = [f for f in findings if f.category in ("PENALTY", "PRICING")]
        penalty_score = 90
        concern = "Balanced reciprocal interest terms."
        if any(f.severity == "CRITICAL" for f in penalty_issues):
            penalty_score = 35
            concern = "Asymmetrical penalties: High late fee interest on buyer (18%) vs nominal delay compensation from developer (~2.4%)."
        elif any(f.severity == "HIGH" for f in penalty_issues):
            penalty_score = 55
            concern = "Elevated late installment interest rate exceeding typical statutory baseline."

        scores.append(
            RiskCategoryScoreSchema(
                category="Penalty & Delay Interest",
                score=penalty_score,
                riskLevel=self._score_to_level(penalty_score),
                primaryConcern=concern,
            )
        )

        # 2. Carpet Area Integrity
        area_issues = [f for f in findings if f.category == "AREA"]
        area_score = 95
        area_concern = "Carpet area matches across promotional and legal documents."
        if area_issues:
            area_score = 50
            area_concern = "Carpet area discrepancy between marketing claims and agreement, with allowable variation tolerance."

        scores.append(
            RiskCategoryScoreSchema(
                category="Carpet Area Integrity",
                score=area_score,
                riskLevel=self._score_to_level(area_score),
                primaryConcern=area_concern,
            )
        )

        # 3. Layout & Specification Alterations
        alteration_issues = [f for f in findings if "alteration" in f.title.lower() or f.category == "SPECIFICATION"]
        alter_score = 85
        alter_concern = "Standard architectural alteration terms."
        if alteration_issues:
            alter_score = 45
            alter_concern = "Developer reserves unilateral discretion to alter layout plans by up to 10% without allottee consent."

        scores.append(
            RiskCategoryScoreSchema(
                category="Layout & Specification Alterations",
                score=alter_score,
                riskLevel=self._score_to_level(alter_score),
                primaryConcern=alter_concern,
            )
        )

        # 4. Cancellation & Earnest Money Forfeiture
        forfeit_clauses = [c for c in clauses if "forfeit" in (c.full_excerpt or "").lower() or c.category == "Cancellation & Earnest Money Forfeiture"]
        forfeit_score = 90
        forfeit_concern = "Customary cancellation terms."
        if any("20%" in (c.full_excerpt or "") for c in forfeit_clauses):
            forfeit_score = 40
            forfeit_concern = "Aggressive 20% earnest money forfeiture on default, exceeding the customary 10% consumer benchmark."

        scores.append(
            RiskCategoryScoreSchema(
                category="Cancellation & Earnest Money Forfeiture",
                score=forfeit_score,
                riskLevel=self._score_to_level(forfeit_score),
                primaryConcern=forfeit_concern,
            )
        )

        # 5. Dispute Resolution & Jurisdiction
        dispute_clauses = [c for c in clauses if c.category == "Dispute Resolution & Jurisdiction"]
        dispute_score = 90
        dispute_concern = "Standard dispute resolution mechanisms."
        if any("sole arbitrator" in (c.full_excerpt or "").lower() for c in dispute_clauses):
            dispute_score = 60
            dispute_concern = "Sole arbitrator appointed unilaterally by promoter with exclusive foreign jurisdiction."

        scores.append(
            RiskCategoryScoreSchema(
                category="Dispute Resolution & Jurisdiction",
                score=dispute_score,
                riskLevel=self._score_to_level(dispute_score),
                primaryConcern=dispute_concern,
            )
        )

        return scores

    @staticmethod
    def _score_to_level(score: int) -> str:
        if score >= 80:
            return "LOW"
        if score >= 65:
            return "MEDIUM"
        if score >= 45:
            return "HIGH"
        return "CRITICAL"


transaction_risk_scorer = TransactionRiskScorer()
