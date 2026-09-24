import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.timeline_service import timeline_service


@pytest.mark.asyncio
async def test_timeline_reconciliation(db_session: AsyncSession):
    """Verifies chronological reconciliation and 5 date certainty classifications."""
    res = await timeline_service.get_reconciled_timeline(db_session, "skyview-a1204")

    assert res.bundleId == "skyview-a1204"
    assert res.totalEvents >= 6
    assert res.contractualEventsCount >= 1
    assert res.marketingEventsCount >= 1
    assert res.inferredEventsCount >= 1
    assert res.uncertainEventsCount >= 1
    assert res.conflictingEventsCount >= 1

    date_types = {e.dateType for e in res.events}
    assert "CONTRACTUAL" in date_types
    assert "INFERRED" in date_types
    assert "MARKETING" in date_types
    assert "UNCERTAIN" in date_types

    # Verify conflict flags
    conflicted = [e for e in res.events if e.conflictingDate is not None]
    assert len(conflicted) >= 2
    assert any("2026-12-31" in (e.eventDate or "") for e in conflicted)

    # Verify milestone payment linkage
    obligations = [e for e in res.events if e.linkedObligationAmount is not None]
    assert len(obligations) >= 2
    for ob in obligations:
        assert ob.linkedObligationAmount > 0
        assert "₹" in (ob.linkedObligationFormatted or "")
