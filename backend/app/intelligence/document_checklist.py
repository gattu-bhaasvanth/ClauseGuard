from typing import List, Dict, Any, Optional
from app.models.document import Document
from app.schemas.report import DocumentChecklistItemSchema


class DocumentChecklistAuditor:
    """
    Audits the bundle's document inventory against statutory real-estate transaction checklists.
    """

    STANDARD_CHECKLIST = [
        {
            "type": "BUILDER_BUYER_AGREEMENT",
            "displayName": "Builder-Buyer Agreement / Sale Agreement",
            "importance": "MANDATORY",
            "description": "Primary binding contract defining rights, specifications, delivery dates, and liabilities.",
            "impactOfMissing": "Critical legal risk: No binding contractual recourse or enforceable delivery timeline.",
        },
        {
            "type": "ALLOTMENT_LETTER",
            "displayName": "Allotment Letter",
            "importance": "REQUIRED",
            "description": "Formal confirmation of unit allotment, initial agreed price, and booking deposit receipt.",
            "impactOfMissing": "Lacks evidence of preliminary terms and advertised commitments made at booking.",
        },
        {
            "type": "PAYMENT_SCHEDULE",
            "displayName": "Payment Milestone Schedule",
            "importance": "REQUIRED",
            "description": "Construction-linked milestone installment schedule with percentages and trigger events.",
            "impactOfMissing": "Risk of premature payment demands without certified completion of construction stages.",
        },
        {
            "type": "SANCTIONED_BUILDING_PLAN",
            "displayName": "Sanctioned Building Plan & Layout",
            "importance": "RECOMMENDED",
            "description": "Statutory authority approved architectural layout and unit floor plans.",
            "impactOfMissing": "Inability to cross-check whether physical layout adheres to sanctioned approvals.",
        },
        {
            "type": "RERA_REGISTRATION_CERTIFICATE",
            "displayName": "RERA Registration Certificate",
            "importance": "RECOMMENDED",
            "description": "Official State Real Estate Regulatory Authority project registration certificate.",
            "impactOfMissing": "Requires manual verification of active registration and project end date on RERA portal.",
        },
        {
            "type": "MARKETING_BROCHURE",
            "displayName": "Sales Brochure & Marketing Collateral",
            "importance": "OPTIONAL",
            "description": "Promotional material advertising specifications, club amenities, and handover timeline.",
            "impactOfMissing": "Restricts multi-document discrepancy detection between marketing pitch and contract.",
        },
    ]

    def audit_documents(self, documents: List[Document]) -> List[DocumentChecklistItemSchema]:
        doc_type_map = {}
        for d in documents:
            d_type = (d.document_type or "OTHER").upper()
            doc_type_map[d_type] = d

        checklist_results: List[DocumentChecklistItemSchema] = []

        for item in self.STANDARD_CHECKLIST:
            target_type = item["type"]
            matched_doc = doc_type_map.get(target_type)

            # Check approximate matches (e.g. BBA matching AGREEMENT)
            if not matched_doc:
                for dtype, doc in doc_type_map.items():
                    if "AGREEMENT" in dtype and "AGREEMENT" in target_type:
                        matched_doc = doc
                        break
                    elif "ALLOTMENT" in dtype and "ALLOTMENT" in target_type:
                        matched_doc = doc
                        break
                    elif "PAYMENT" in dtype and "PAYMENT" in target_type:
                        matched_doc = doc
                        break
                    elif "BROCHURE" in dtype and "BROCHURE" in target_type:
                        matched_doc = doc
                        break

            if matched_doc:
                checklist_results.append(
                    DocumentChecklistItemSchema(
                        documentType=target_type,
                        displayName=item["displayName"],
                        status="PRESENT",
                        fileName=matched_doc.file_name,
                        pageCount=matched_doc.page_count,
                        description=item["description"],
                        importance=item["importance"],
                        impactOfMissing=None,
                    )
                )
            else:
                checklist_results.append(
                    DocumentChecklistItemSchema(
                        documentType=target_type,
                        displayName=item["displayName"],
                        status="MISSING" if item["importance"] in ("MANDATORY", "REQUIRED") else "RECOMMENDED",
                        fileName=None,
                        pageCount=None,
                        description=item["description"],
                        importance=item["importance"],
                        impactOfMissing=item["impactOfMissing"],
                    )
                )

        return checklist_results


document_checklist_auditor = DocumentChecklistAuditor()
