import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.clause import Clause
from app.models.finding import Finding
from app.models.transaction import TransactionBundle
from app.intelligence.risk_scorer import transaction_risk_scorer
from app.intelligence.document_checklist import document_checklist_auditor
from app.intelligence.summary_synthesizer import executive_summary_synthesizer
from app.reports.report_service import report_service


# ==============================================================================
# 1. RISK SCORER & CHECKLIST UNIT TESTS
# ==============================================================================


def test_risk_scorer_category_breakdown():
    clauses = [
        Clause(
            id="c1",
            bundle_id="b1",
            document_id="d1",
            clause_number="Clause 5.3",
            title="Late Payment Interest",
            category="Payment Milestones & Delay Interest",
            full_excerpt="Allottee shall pay delay interest at 18% per annum compounded monthly.",
        ),
        Clause(
            id="c2",
            bundle_id="b1",
            document_id="d1",
            clause_number="Clause 6.2",
            title="Earnest Money Forfeiture",
            category="Cancellation & Earnest Money Forfeiture",
            full_excerpt="Promoter shall forfeit 20% of the total consideration upon default.",
        ),
    ]

    findings = [
        Finding(
            id="f1",
            bundle_id="b1",
            finding_type="RISK",
            category="PENALTY",
            severity="CRITICAL",
            title="Asymmetrical Delay Penalties",
            primary_evidence={},
        ),
        Finding(
            id="f2",
            bundle_id="b1",
            finding_type="INCONSISTENCY",
            category="AREA",
            severity="HIGH",
            title="Carpet Area Discrepancy",
            primary_evidence={},
        ),
    ]

    scores = transaction_risk_scorer.compute_category_scores(clauses, findings)
    assert len(scores) == 5

    penalty_cat = next(s for s in scores if s.category == "Penalty & Delay Interest")
    assert penalty_cat.riskLevel == "CRITICAL"
    assert penalty_cat.score <= 40

    area_cat = next(s for s in scores if s.category == "Carpet Area Integrity")
    assert area_cat.riskLevel in ("HIGH", "MEDIUM")
    assert area_cat.score <= 60

    forfeit_cat = next(s for s in scores if s.category == "Cancellation & Earnest Money Forfeiture")
    assert forfeit_cat.riskLevel in ("HIGH", "CRITICAL")


def test_document_checklist_auditor():
    docs = [
        Document(id="d1", bundle_id="b1", file_name="BBA_SkyView.pdf", document_type="BUILDER_BUYER_AGREEMENT"),
        Document(id="d2", bundle_id="b1", file_name="Allotment_Letter.pdf", document_type="ALLOTMENT_LETTER"),
    ]

    checklist = document_checklist_auditor.audit_documents(docs)
    assert len(checklist) >= 5

    bba_item = next(i for i in checklist if i.documentType == "BUILDER_BUYER_AGREEMENT")
    assert bba_item.status == "PRESENT"
    assert bba_item.fileName == "BBA_SkyView.pdf"

    plan_item = next(i for i in checklist if i.documentType == "SANCTIONED_BUILDING_PLAN")
    assert plan_item.status in ("MISSING", "RECOMMENDED")
    assert plan_item.impactOfMissing is not None


def test_summary_synthesizer():
    bundle = TransactionBundle(
        id="b-test",
        title="SkyView Flat A-1204",
        project="SkyView Residency",
        unit="Flat A-1204",
        developer="Skyline Urban Developers",
        city="Gurugram",
        location="Sector 65, Gurugram",
        property_type="Residential Apartment",
        carpet_area_sqft=1380.0,
        super_area_sqft=1850.0,
        sale_price=14200000.0,
        possession_date="2027-12-31",
        grace_period_months=6,
    )

    findings = [
        Finding(
            id="f1",
            bundle_id="b-test",
            finding_type="INCONSISTENCY",
            category="AREA",
            severity="HIGH",
            title="Carpet Area Discrepancy",
            description="Brochure mentions 1,450 sq.ft, agreement sets 1,380 sq.ft.",
            primary_evidence={},
        ),
        Finding(
            id="f2",
            bundle_id="b-test",
            finding_type="RISK",
            category="PENALTY",
            severity="CRITICAL",
            title="Asymmetrical Delay Penalties",
            description="Buyer default 18% vs builder delay Rs 5/sq.ft.",
            primary_evidence={},
        ),
    ]

    summary = executive_summary_synthesizer.synthesize_summary(bundle, findings, missing_doc_count=2)

    assert "Flat A-1204" in summary.transactionProfile
    assert "SkyView Residency" in summary.transactionProfile
    assert "1,380" in summary.transactionProfile
    assert "Carpet Area Discrepancy" in summary.keyFindingsNarrative
    assert "Asymmetrical Delay Penalties" in summary.criticalRisksNarrative
    assert len(summary.recommendedActions) >= 3


# ==============================================================================
# 2. REPORT SERVICE & PDF GENERATION TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_build_audit_report_json(db_session: AsyncSession):
    report = await report_service.build_audit_report(db_session, "skyview-a1204")

    assert report.bundleId == "skyview-a1204"
    assert report.healthScore == 74
    assert "SkyView" in report.projectTitle
    assert len(report.documentChecklist) >= 5
    assert len(report.categoryRiskScores) == 5
    assert len(report.inconsistencies) >= 2
    assert len(report.risks) >= 2
    assert "LEGAL ADVICE" in report.disclaimer


@pytest.mark.asyncio
async def test_generate_audit_report_pdf_bytes(db_session: AsyncSession):
    pdf_bytes = await report_service.generate_audit_report_pdf(db_session, "skyview-a1204")

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    # PDF magic header
    assert pdf_bytes.startswith(b"%PDF-")


# ==============================================================================
# 3. REST API TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_report_api_endpoints(client: AsyncClient):
    # 1. JSON Report endpoint
    res_json = await client.get("/api/v1/transactions/skyview-a1204/report")
    assert res_json.status_code == 200
    data = res_json.json()
    assert data["bundleId"] == "skyview-a1204"
    assert "executiveSummary" in data
    assert "documentChecklist" in data
    assert "categoryRiskScores" in data
    assert "disclaimer" in data

    # 2. PDF Download endpoint
    res_pdf = await client.get("/api/v1/transactions/skyview-a1204/report/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert "attachment;" in res_pdf.headers["content-disposition"]
    assert res_pdf.content.startswith(b"%PDF-")

    # 3. Checklist endpoint
    res_chk = await client.get("/api/v1/transactions/skyview-a1204/checklist")
    assert res_chk.status_code == 200
    checklist_data = res_chk.json()
    assert isinstance(checklist_data, list)
    assert len(checklist_data) >= 5
