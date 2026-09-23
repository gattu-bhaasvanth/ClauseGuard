from enum import Enum
from typing import Dict, List, Any


class ClauseCategory(str, Enum):
    POSSESSION_TERMS = "Possession & Handover"
    PAYMENT_TERMS = "Payment Milestones & Delay Interest"
    AREA_SPECIFICATIONS = "Carpet Area & Measurement Adjustments"
    CANCELLATION_FORFEITURE = "Cancellation & Earnest Money Forfeiture"
    ALTERATION_VARIATION = "Alteration of Layout & Specifications"
    DEFECTS_LIABILITY = "Defects Liability & Structural Rectification"
    FORCE_MAJEURE = "Force Majeure & Uncontrollable Delays"
    DISPUTE_JURISDICTION = "Dispute Resolution & Jurisdiction"
    STATUTORY_COMPLIANCE = "RERA & Statutory Approvals"
    MAINTENANCE_CHARGES = "Maintenance & Additional Levies"
    GENERAL_TERMS = "General Terms & Covenants"


# Domain-specific terminology and keyword weights for classification
TAXONOMY_KEYWORDS: Dict[ClauseCategory, List[str]] = {
    ClauseCategory.POSSESSION_TERMS: [
        "possession",
        "handover",
        "conveyance",
        "offer of possession",
        "scheduled completion",
        "grace period",
        "delayed possession",
        "occupancy certificate",
        "completion certificate",
        "hand over",
        "fit-out",
        "deemed possession",
    ],
    ClauseCategory.PAYMENT_TERMS: [
        "installment",
        "payment plan",
        "payment terms",
        "payment",
        "delay payment",
        "delayed payment",
        "interest on delayed",
        "compounded monthly",
        "time is of the essence",
        "due date",
        "total consideration",
        "booking amount",
        "mclr",
        "default in payment",
        "default",
    ],
    ClauseCategory.AREA_SPECIFICATIONS: [
        "carpet area",
        "rera carpet",
        "super area",
        "super built-up",
        "built-up area",
        "measurement",
        "undivided share",
        "uds",
        "variation in area",
        "percentage variation",
        "sq.ft",
        "sq. ft",
        "sq.m",
    ],
    ClauseCategory.CANCELLATION_FORFEITURE: [
        "cancellation",
        "forfeiture",
        "earnest money",
        "terminate",
        "termination",
        "liquidated damages",
        "refund",
        "rescind",
        "forfeit",
        "default by allottee",
    ],
    ClauseCategory.ALTERATION_VARIATION: [
        "alteration",
        "modification of plans",
        "sanction plan revision",
        "variation in layout",
        "architectural necessity",
        "change in specifications",
        "liberty to effect",
        "consent of allottees",
    ],
    ClauseCategory.DEFECTS_LIABILITY: [
        "defect liability",
        "defects liability",
        "structural defect",
        "workmanship",
        "rectify",
        "warranty",
        "five years",
        "5 years",
        "maintenance period",
    ],
    ClauseCategory.FORCE_MAJEURE: [
        "force majeure",
        "act of god",
        "war",
        "strike",
        "epidemic",
        "pandemic",
        "lockdown",
        "unforeseen circumstances",
        "beyond control",
        "court injunction",
    ],
    ClauseCategory.DISPUTE_JURISDICTION: [
        "dispute resolution",
        "arbitration",
        "arbitrator",
        "exclusive jurisdiction",
        "courts at",
        "conciliation",
        "appellate tribunal",
        "governing law",
    ],
    ClauseCategory.STATUTORY_COMPLIANCE: [
        "rera",
        "real estate regulatory",
        "registration number",
        "sanction",
        "statutory approval",
        "environment clearance",
        "fire noc",
        "building bye-laws",
    ],
    ClauseCategory.MAINTENANCE_CHARGES: [
        "maintenance",
        "common areas",
        "club charges",
        "electrification",
        "substation",
        "sinking fund",
        "ifms",
        "external development charges",
        "edc",
        "idc",
        "property tax",
    ],
}
