import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.transaction_intelligence_orchestrator import transaction_intelligence_orchestrator


@pytest.mark.asyncio
async def test_orchestrator_command_center(db_session: AsyncSession):
    """Verifies that the orchestrator synthesizes command center intelligence from the knowledge graph."""
    res = await transaction_intelligence_orchestrator.get_command_center(db_session, "skyview-a1204")
    
    assert res.bundleId == "skyview-a1204"
    assert res.projectName == "SkyView Residency"
    assert res.unitNumber == "Flat A-1204"
    assert res.healthScore == 74
    assert res.riskLevel in ("LOW", "MEDIUM", "HIGH")

    # Financial Exposure Verifications
    fin = res.financialExposure
    assert fin.baseConsideration == 14250000.0
    assert fin.earnestMoneyForfeitRisk == 2850000.0
    assert fin.statutoryForfeitLimit == 1425000.0
    assert fin.excessForfeitExposure == 1425000.0
    assert fin.delayInterestRateBuyer == 18.0
    assert fin.delayCompensationRateDeveloper > 0.0
    assert fin.monthlyAsymmetryCost > 0.0
    assert fin.areaDiscrepancyCostImpact > 0.0
    assert fin.totalFinancialAtRisk > fin.excessForfeitExposure
    assert "₹" in fin.totalFinancialAtRiskFormatted

    # 5 Risk Vectors Verification
    assert len(res.riskVectors) == 5
    vector_ids = [v.id for v in res.riskVectors]
    assert "financial_exposure" in vector_ids
    assert "contractual_asymmetry" in vector_ids
    assert "timeline_delivery" in vector_ids
    assert "dimensional_variance" in vector_ids
    assert "document_completeness" in vector_ids

    # Priority Action Items
    assert len(res.priorityActions) >= 5
    critical_actions = [a for a in res.priorityActions if a.severity == "CRITICAL"]
    assert len(critical_actions) >= 2
    for action in res.priorityActions:
        assert action.title
        assert action.recommendedAction
        assert action.category in ("NEGOTIATION", "DOCUMENT_REQUEST", "LEGAL_REVIEW", "PAYMENT_HOLD")


@pytest.mark.asyncio
async def test_orchestrator_explainable_risk(db_session: AsyncSession):
    """Verifies explainable risk detail generation with 5-tier lineage and statutory benchmarks."""
    # Test penalty risk (risk-01)
    risk_res = await transaction_intelligence_orchestrator.get_explainable_risk(
        db_session, "skyview-a1204", "risk-01"
    )
    assert risk_res.findingId == "risk-01"
    assert "Section 18" in risk_res.statutoryBenchmark or "RERA" in risk_res.statutoryBenchmark
    assert "74,000" in risk_res.quantifiedImpact or "penalty" in risk_res.quantifiedImpact.lower()
    assert risk_res.lineage.documentName == "Builder_Buyer_Agreement_SkyView_A1204.pdf"
    assert risk_res.lineage.pageNumber == 15
    assert "Clause 8.2" in (risk_res.lineage.clauseNumber or "")
    assert len(risk_res.lineage.verbatimExcerpt) > 10
    assert risk_res.recommendedNegotiationScript != ""

    # Test area discrepancy (inc-01)
    area_res = await transaction_intelligence_orchestrator.get_explainable_risk(
        db_session, "skyview-a1204", "inc-01"
    )
    assert area_res.findingId == "inc-01"
    assert "Section 14" in area_res.statutoryBenchmark or "RERA" in area_res.statutoryBenchmark
    assert "70 sq.ft" in area_res.quantifiedImpact or "4,63,950" in area_res.quantifiedImpact


@pytest.mark.asyncio
async def test_orchestrator_nonexistent_bundle(db_session: AsyncSession):
    """Verifies orchestrator raises ValueError on non-existent bundle."""
    with pytest.raises(ValueError) as exc:
        await transaction_intelligence_orchestrator.get_command_center(db_session, "invalid-bundle-id")
    assert "not found" in str(exc.value).lower()
