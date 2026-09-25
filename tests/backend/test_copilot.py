import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.copilot_service import transaction_copilot_service, REFUSAL_MESSAGE
from app.schemas.copilot import CopilotQueryRequestSchema


@pytest.mark.asyncio
async def test_copilot_summary_intent(db_session: AsyncSession):
    """Verifies copilot summary synthesis with citations."""
    req = CopilotQueryRequestSchema(query="Summarize this transaction bundle and unit details")
    res = await transaction_copilot_service.query_copilot(db_session, "skyview-a1204", req)

    assert res.bundleId == "skyview-a1204"
    assert res.grounded is True
    assert res.refused is False
    assert res.intent == "SUMMARY"
    assert "SkyView Residency" in res.answer
    assert "Flat A-1204" in res.answer
    assert len(res.citations) >= 1
    assert res.citations[0].documentName != ""
    assert res.citations[0].pageNumber >= 1


@pytest.mark.asyncio
async def test_copilot_delay_penalties_intent(db_session: AsyncSession):
    """Verifies grounded answer for delayed handover penalties and RERA Section 18 citations."""
    req = CopilotQueryRequestSchema(query="What happens if the builder delays handover beyond December 2027?")
    res = await transaction_copilot_service.query_copilot(db_session, "skyview-a1204", req)

    assert res.grounded is True
    assert res.refused is False
    assert res.intent == "DELAY_PENALTIES"
    assert "Clause 8.2" in res.answer
    assert "5" in res.answer  # Rs 5 per sq ft
    assert "18%" in res.answer
    assert len(res.citations) >= 1
    assert res.citations[0].clauseNumber == "Clause 8.2"
    assert "delay" in res.citations[0].excerpt.lower()


@pytest.mark.asyncio
async def test_copilot_date_conflicts_intent(db_session: AsyncSession):
    """Verifies detection of delivery date discrepancies between brochure and agreement."""
    req = CopilotQueryRequestSchema(query="Are there conflicting dates between brochure and contract?")
    res = await transaction_copilot_service.query_copilot(db_session, "skyview-a1204", req)

    assert res.grounded is True
    assert res.refused is False
    assert res.intent == "DATE_CONFLICTS"
    assert "2026" not in res.answer
    assert "2027" in res.answer
    assert "30 June 2027" in res.answer
    assert "31 December 2027" in res.answer
    assert len(res.citations) >= 2


@pytest.mark.asyncio
async def test_copilot_top_risks_intent(db_session: AsyncSession):
    """Verifies top risk aggregation across the bundle."""
    req = CopilotQueryRequestSchema(query="What are my biggest risks and red flags?")
    res = await transaction_copilot_service.query_copilot(db_session, "skyview-a1204", req)

    assert res.grounded is True
    assert res.refused is False
    assert res.intent == "TOP_RISKS"
    assert "Asymmetrical Delay Compensation" in res.answer
    assert "Earnest Money Forfeiture" in res.answer
    assert len(res.citations) >= 1


@pytest.mark.asyncio
async def test_copilot_amendments_intent(db_session: AsyncSession):
    """Verifies actionable builder negotiation recommendations."""
    req = CopilotQueryRequestSchema(query="What clauses should I negotiate before signing?")
    res = await transaction_copilot_service.query_copilot(db_session, "skyview-a1204", req)

    assert res.grounded is True
    assert res.refused is False
    assert res.intent == "AMENDMENT_RECOMMENDATIONS"
    assert "Clause 8.2" in res.answer
    assert "Clause 6.1" in res.answer
    assert len(res.citations) >= 1


@pytest.mark.asyncio
async def test_copilot_strict_refusal_guardrail(db_session: AsyncSession):
    """Verifies strict refusal when an out-of-scope or unevidenced question is asked."""
    req = CopilotQueryRequestSchema(
        query="What is the current stock market share price of the developer's parent holding company?"
    )
    res = await transaction_copilot_service.query_copilot(db_session, "skyview-a1204", req)

    assert res.grounded is False
    assert res.refused is True
    assert res.citations == []
    assert res.answer == REFUSAL_MESSAGE
    assert len(res.suggestedNextQuestions) > 0
