import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.transaction_brief_service import transaction_brief_service


@pytest.mark.asyncio
async def test_transaction_brief_generation(db_session: AsyncSession):
    """Verifies generation of 7 evidence-traceable executive brief sections and PDF output."""
    brief = await transaction_brief_service.generate_brief(db_session, "skyview-a1204")

    assert brief.bundleId == "skyview-a1204"
    assert brief.project == "SkyView Residency"
    assert brief.unit == "Flat A-1204"
    assert len(brief.sections) == 7

    expected_keys = [
        "PROPERTY_SNAPSHOT",
        "EXECUTIVE_ASSESSMENT",
        "FINANCIAL_EXPOSURE",
        "CONTRACTUAL_MILESTONES",
        "DISCREPANCIES",
        "ASYMMETRIC_CLAUSES",
        "ACTION_PLAN",
    ]
    actual_keys = [s.sectionKey for s in brief.sections]
    assert actual_keys == expected_keys

    # Check evidence lineage on all sections
    for sec in brief.sections:
        assert sec.summary != ""
        assert len(sec.bulletPoints) >= 1
        assert len(sec.evidenceLineage) >= 1
        for ev in sec.evidenceLineage:
            assert "document" in ev
            assert "excerpt" in ev

    # Check PDF export
    pdf_bytes = transaction_brief_service.generate_pdf(brief)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF")
