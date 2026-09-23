from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transaction import TransactionBundle
from app.models.document import Document, DocumentPage
from app.models.clause import Clause
from app.models.finding import Finding
from app.models.attribute import ExtractedAttribute


async def seed_demo_data(session: AsyncSession) -> None:
    """Seeds the database with realistic demo transaction bundles if empty."""
    result = await session.execute(select(TransactionBundle).filter_by(id="skyview-a1204"))
    existing = result.scalar_one_or_none()
    if existing:
        return

    # 1. SkyView Residency Bundle
    skyview = TransactionBundle(
        id="skyview-a1204",
        title="SkyView Residency — Flat A-1204",
        project="SkyView Residency",
        unit="Flat A-1204",
        floor=12,
        tower="Tower A (Oasis Wing)",
        developer="Skyline Urban Developers Pvt. Ltd.",
        city="Gurgaon",
        location="Sector 62, Golf Course Ext., Gurgaon, HR",
        property_type="Residential Apartment",
        carpet_area_sqft=1380.0,
        super_area_sqft=1820.0,
        advertised_carpet_area_sqft=1450.0,
        sale_price=14250000.0,
        possession_date="2027-12-31",
        grace_period_months=6,
        health_score=74,
        status="ANALYSIS_COMPLETE",
        created_at=datetime.fromisoformat("2026-09-18T10:14:00"),
        updated_at=datetime.fromisoformat("2026-09-23T11:45:00"),
    )
    session.add(skyview)

    # SkyView Documents
    bba_doc = Document(
        id="doc-bba-01",
        bundle_id="skyview-a1204",
        file_name="Builder_Buyer_Agreement_SkyView_A1204.pdf",
        document_type="BUILDER_BUYER_AGREEMENT",
        file_size="4.8 MB",
        page_count=38,
        ocr_status="COMPLETED",
        clause_count=42,
        issue_count=5,
        created_at=datetime.fromisoformat("2026-09-18T10:14:00"),
    )
    allotment_doc = Document(
        id="doc-allotment-02",
        bundle_id="skyview-a1204",
        file_name="Allotment_Letter_Signed_A1204.pdf",
        document_type="ALLOTMENT_LETTER",
        file_size="1.2 MB",
        page_count=6,
        ocr_status="COMPLETED",
        clause_count=14,
        issue_count=1,
        created_at=datetime.fromisoformat("2026-09-18T10:15:30"),
    )
    schedule_doc = Document(
        id="doc-schedule-03",
        bundle_id="skyview-a1204",
        file_name="Payment_Schedule_Milestone_Plan.pdf",
        document_type="PAYMENT_SCHEDULE",
        file_size="680 KB",
        page_count=3,
        ocr_status="NOT_REQUIRED",
        clause_count=8,
        issue_count=0,
        created_at=datetime.fromisoformat("2026-09-18T10:16:00"),
    )
    brochure_doc = Document(
        id="doc-brochure-04",
        bundle_id="skyview-a1204",
        file_name="SkyView_Premium_Brochure_Phase2.pdf",
        document_type="PROJECT_BROCHURE",
        file_size="18.4 MB",
        page_count=24,
        ocr_status="COMPLETED",
        clause_count=12,
        issue_count=1,
        created_at=datetime.fromisoformat("2026-09-18T10:18:00"),
    )
    session.add_all([bba_doc, allotment_doc, schedule_doc, brochure_doc])

    # SkyView Inconsistencies & Risks (Findings)
    inc_area = Finding(
        id="inc-01",
        bundle_id="skyview-a1204",
        finding_type="INCONSISTENCY",
        category="AREA",
        severity="HIGH",
        title="Carpet Area Discrepancy",
        description="Marketing brochure specifies 1,450 sq.ft carpet area, while the legally binding Builder-Buyer Agreement defines the carpet area as 1,380 sq.ft (difference of 70 sq.ft / 4.8%).",
        primary_evidence={
            "documentId": "doc-brochure-04",
            "documentName": "SkyView_Premium_Brochure_Phase2.pdf",
            "documentType": "PROJECT_BROCHURE",
            "pageNumber": 4,
            "excerpt": "Type 3BHK Elite Residence: Carpet Area: 1450 sq.ft (134.7 sq.m) | Super Built-up: 1820 sq.ft. Includes expansive 80 sq.ft double-height sundeck balcony.",
        },
        secondary_evidence={
            "documentId": "doc-bba-01",
            "documentName": "Builder_Buyer_Agreement_SkyView_A1204.pdf",
            "documentType": "BUILDER_BUYER_AGREEMENT",
            "pageNumber": 12,
            "clauseNumber": "Clause 4.1",
            "excerpt": "The Allottee agrees that the Apartment has a RERA Carpet Area of 1,380 sq. ft. (128.20 sq. m.), and the Developer reserves the right to make variations of up to ±3% without adjustment in total consideration.",
        },
        detected_at=datetime.fromisoformat("2026-09-18T10:20:00"),
    )

    inc_possession = Finding(
        id="inc-02",
        bundle_id="skyview-a1204",
        finding_type="INCONSISTENCY",
        category="POSSESSION",
        severity="MEDIUM",
        title="Promised Possession Date Shift",
        description="Allotment letter mentions 30 June 2027 handover, but Builder-Buyer Agreement postpones delivery to 31 December 2027 plus an added 180-day grace period.",
        primary_evidence={
            "documentId": "doc-allotment-02",
            "documentName": "Allotment_Letter_Signed_A1204.pdf",
            "documentType": "ALLOTMENT_LETTER",
            "pageNumber": 2,
            "excerpt": "Target possession and handover of Unit A-1204 is projected for 30th June 2027 upon completion of architectural finishes.",
        },
        secondary_evidence={
            "documentId": "doc-bba-01",
            "documentName": "Builder_Buyer_Agreement_SkyView_A1204.pdf",
            "documentType": "BUILDER_BUYER_AGREEMENT",
            "pageNumber": 19,
            "clauseNumber": "Clause 11.2",
            "excerpt": "The Promoter proposes to complete construction of the Apartment by 31st December 2027. The Promoter shall be entitled to an unconditional grace period of one hundred eighty (180) days thereafter.",
        },
        detected_at=datetime.fromisoformat("2026-09-18T10:20:00"),
    )

    risk_penalty = Finding(
        id="risk-01",
        bundle_id="skyview-a1204",
        finding_type="RISK",
        category="PENALTY",
        severity="CRITICAL",
        title="Asymmetrical Delay Penalties",
        impact="High financial penalty on Buyer default (18% p.a.) versus nominal compensation from Developer for delayed possession (~2.4% p.a.).",
        description="Clause 5.3 penalizes late buyer installments at 18% per annum compounded monthly, whereas Clause 8.2 compensates delayed developer handover at only Rs. 5 per sq.ft per month.",
        recommendation_note="Under RERA Section 18, allottees and promoters are entitled to reciprocal interest rates. Verify whether statutory RERA rates supersede this contract clause in your jurisdiction.",
        primary_evidence={
            "documentId": "doc-bba-01",
            "documentName": "Builder_Buyer_Agreement_SkyView_A1204.pdf",
            "documentType": "BUILDER_BUYER_AGREEMENT",
            "pageNumber": 15,
            "clauseNumber": "Clause 8.2",
            "excerpt": "In the event of delay in offering possession of the Apartment, the Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft. of super area per month for the period of delay beyond the grace period.",
        },
        detected_at=datetime.fromisoformat("2026-09-18T10:20:00"),
    )

    risk_alteration = Finding(
        id="risk-02",
        bundle_id="skyview-a1204",
        finding_type="RISK",
        category="SPECIFICATION",
        severity="HIGH",
        title="Unilateral Alteration of Layout & Specifications",
        impact="Developer retains unilateral discretion to adjust floor plans, room dimensions, or building materials by up to 10% without allottee consent.",
        description="Standard statutory norms require consent of two-thirds of allottees for major plan alterations. Clause 6.4 waives buyer objection for alterations deemed architecturally necessary.",
        recommendation_note="Request clarification on whether structural changes require allottee notification and price adjustments.",
        primary_evidence={
            "documentId": "doc-bba-01",
            "documentName": "Builder_Buyer_Agreement_SkyView_A1204.pdf",
            "documentType": "BUILDER_BUYER_AGREEMENT",
            "pageNumber": 14,
            "clauseNumber": "Clause 6.4",
            "excerpt": "The Developer shall be at liberty to effect such variations, additions, alterations, and modifications in the building plans as it may deem fit or as directed by sanctions, up to 10% variation.",
        },
        detected_at=datetime.fromisoformat("2026-09-18T10:20:00"),
    )
    session.add_all([inc_area, inc_possession, risk_penalty, risk_alteration])

    # SkyView Extracted Clauses
    clauses = [
        Clause(
            id="cls-01",
            bundle_id="skyview-a1204",
            document_id="doc-bba-01",
            clause_number="Clause 8.2",
            title="Possession Handover & Delay Penalty",
            category="Possession Terms",
            status="RISK",
            severity="CRITICAL",
            page_number=15,
            preview_text="Promoter compensation for delayed possession capped at Rs. 5/sq.ft/month...",
            full_excerpt="8.2. In the event of delay in offering possession of the Apartment beyond the agreed date and grace period of 180 days, the Promoter shall pay compensation at the rate of Rs. 5/- (Rupees Five only) per sq. ft. of super area per month for the period of delay. Such compensation shall be adjusted against dues payable at possession.",
            analysis_summary="Asymmetrical delay penalty. Developer pays approx 2.4% annualized return, while allottee pays 18% p.a. for late payments.",
            risk_details="Violates reciprocal interest principles under RERA Section 18.",
        ),
        Clause(
            id="cls-02",
            bundle_id="skyview-a1204",
            document_id="doc-bba-01",
            clause_number="Clause 5.3",
            title="Payment Default & Interest Rate",
            category="Payment Terms",
            status="RISK",
            severity="HIGH",
            page_number=13,
            preview_text="Allottee failure to pay installment attracts 18% per annum compounded monthly...",
            full_excerpt="5.3. Time is of the essence. If the Allottee fails to pay any installment on or before the due date, the Allottee shall be liable to pay interest on delayed payment at the rate of 18% per annum compounded monthly from the due date until realization.",
            analysis_summary="High interest rate (18% p.a. compounded monthly). Significant financial penalty on short-term cash flow delays.",
            risk_details="Review required against statutory state RERA default benchmark.",
        ),
        Clause(
            id="cls-03",
            bundle_id="skyview-a1204",
            document_id="doc-bba-01",
            clause_number="Clause 4.1",
            title="Measurement & Carpet Area Adjustments",
            category="Property Dimensions",
            status="INCONSISTENCY",
            severity="HIGH",
            page_number=12,
            preview_text="RERA Carpet Area 1,380 sq.ft subject to ±3% variation without price change...",
            full_excerpt="4.1. The Allottee agrees that the Apartment has a RERA Carpet Area of 1,380 sq. ft. (128.20 sq. m.). The Promoter reserves the right to make architectural adjustments resulting in up to ±3% variation in carpet area without alteration to the agreed Total Consideration.",
            analysis_summary="Inconsistency detected: Brochure advertised 1,450 sq.ft carpet area. The contract defines 1,380 sq.ft with 3% additional variation allowance.",
            risk_details="Potential net reduction of up to 111 sq.ft compared to initial sales pitch.",
        ),
    ]
    session.add_all(clauses)

    # 2. Prestige Palm Heights Bundle
    prestige = TransactionBundle(
        id="prestige-palm-v18",
        title="Prestige Palm Heights — Villa 18",
        project="Prestige Palm Heights",
        unit="Villa 18",
        floor=2,
        tower="Phase 1 - Gardenia",
        developer="Prestige Estates Projects Ltd.",
        city="Bengaluru",
        location="Whitefield, Bengaluru, KA",
        property_type="Independent Villa",
        carpet_area_sqft=3100.0,
        super_area_sqft=4250.0,
        advertised_carpet_area_sqft=3100.0,
        sale_price=38500000.0,
        possession_date="2026-12-15",
        grace_period_months=3,
        health_score=89,
        status="ANALYSIS_COMPLETE",
        created_at=datetime.fromisoformat("2026-09-15T09:30:00"),
        updated_at=datetime.fromisoformat("2026-09-20T14:10:00"),
    )
    session.add(prestige)

    # 3. Urban Greens Bundle
    urban = TransactionBundle(
        id="urban-greens-b802",
        title="Urban Greens — Tower B-802",
        project="Urban Greens Habitat",
        unit="Unit B-802",
        floor=8,
        tower="Tower B",
        developer="Greenfield Developers LLP",
        city="Hyderabad",
        location="Financial District, Hyderabad, TG",
        property_type="Residential Apartment",
        carpet_area_sqft=1120.0,
        super_area_sqft=1540.0,
        advertised_carpet_area_sqft=1220.0,
        sale_price=9400000.0,
        possession_date="2028-03-31",
        grace_period_months=6,
        health_score=62,
        status="NEEDS_ATTENTION",
        created_at=datetime.fromisoformat("2026-09-12T16:00:00"),
        updated_at=datetime.fromisoformat("2026-09-22T08:30:00"),
    )
    session.add(urban)

    await session.commit()
