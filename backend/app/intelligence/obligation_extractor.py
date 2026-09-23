import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ObligationItem:
    party: str  # "BUYER", "DEVELOPER", "MUTUAL"
    action_type: str  # "PAYMENT", "DELIVERY", "MAINTENANCE", "COMPLIANCE", "RECTIFICATION"
    summary: str
    target_date_or_rate: Optional[str] = None


class ObligationExtractor:
    """
    Extracts and attributes contractual obligations from legal clause text,
    classifying duties between Buyer/Allottee and Developer/Promoter.
    """

    BUYER_TRIGGERS = [
        "allottee shall",
        "purchaser agrees to pay",
        "allottee agrees to pay",
        "liability of the allottee",
        "allottee fails to pay",
        "payable by the allottee",
        "allottee shall be liable",
        "shall bear all stamp duty",
        "time is of the essence",
    ]

    DEVELOPER_TRIGGERS = [
        "promoter shall",
        "developer shall",
        "developer agrees to",
        "promoter proposes to complete",
        "handover possession",
        "promoter shall pay compensation",
        "developer will rectify",
        "promoter agrees to obtain",
        "at its own cost",
    ]

    def extract_party(self, text: str) -> str:
        lower = text.lower()
        buyer_score = sum(1 for t in self.BUYER_TRIGGERS if t in lower)
        dev_score = sum(1 for t in self.DEVELOPER_TRIGGERS if t in lower)

        if buyer_score > dev_score:
            return "BUYER"
        elif dev_score > buyer_score:
            return "DEVELOPER"
        return "MUTUAL"

    def extract_obligation_details(self, title: str, text: str) -> ObligationItem:
        party = self.extract_party(text)
        lower = text.lower()

        # Determine action type and key metric
        if "interest on delayed" in lower or "compounded monthly" in lower or "18%" in lower:
            action_type = "PAYMENT"
            summary = "Pay delay interest on overdue installments"
            target = "18% p.a." if "18%" in lower else None
        elif "delay in offering possession" in lower or "rs. 5" in lower or "grace period" in lower:
            action_type = "DELIVERY"
            summary = "Hand over possession with compensation for delays"
            target = "Rs. 5/sq.ft/month" if "rs. 5" in lower else None
        elif "carpet area" in lower:
            action_type = "SPECIFICATION"
            summary = "Accept specified carpet area with agreed variation limits"
            target = "±3% variation" if "3%" in lower else None
        elif "defect liability" in lower or "structural defect" in lower:
            action_type = "RECTIFICATION"
            summary = "Rectify structural and workmanship defects"
            target = "5 Years" if "5 year" in lower or "five year" in lower else None
        elif "forfeit" in lower or "cancellation" in lower:
            action_type = "CANCELLATION"
            summary = "Forfeit earnest money upon buyer cancellation"
            target = "20%" if "20%" in lower else "10%"
        else:
            action_type = "COMPLIANCE"
            summary = f"Abide by terms of {title}"
            target = None

        return ObligationItem(
            party=party,
            action_type=action_type,
            summary=summary,
            target_date_or_rate=target,
        )
