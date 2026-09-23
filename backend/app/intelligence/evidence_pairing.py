from typing import Optional, Dict, Any
from app.models.document import Document
from app.models.attribute import ExtractedAttribute


class EvidencePairingService:
    """
    Constructs dual evidence payloads matching Guiding Principle 3:
    Document -> Page -> Clause -> Source Excerpt.
    """

    @staticmethod
    def create_citation(
        document: Optional[Document],
        attribute: Optional[ExtractedAttribute] = None,
        page_number: int = 1,
        clause_number: Optional[str] = None,
        excerpt: str = "",
        bounding_box: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        doc_id = document.id if document else (attribute.document_id if attribute else "")
        doc_name = document.file_name if document else "Document"
        doc_type = document.document_type if document else "OTHER"

        pg = page_number
        cls_num = clause_number
        quote = excerpt

        if attribute:
            pg = attribute.source_page or pg
            cls_num = attribute.source_clause or cls_num
            quote = attribute.raw_excerpt or quote or attribute.attribute_value

        return {
            "documentId": doc_id,
            "documentName": doc_name,
            "documentType": doc_type,
            "pageNumber": pg,
            "clauseNumber": cls_num,
            "excerpt": quote,
            "boundingBox": bounding_box,
        }

    @classmethod
    def pair_discrepancy_evidence(
        cls,
        doc_a: Optional[Document],
        attr_a: Optional[ExtractedAttribute],
        doc_b: Optional[Document],
        attr_b: Optional[ExtractedAttribute],
        fallback_excerpt_a: str = "",
        fallback_excerpt_b: str = "",
    ) -> Dict[str, Dict[str, Any]]:
        citation_a = cls.create_citation(
            document=doc_a,
            attribute=attr_a,
            excerpt=fallback_excerpt_a,
        )
        citation_b = cls.create_citation(
            document=doc_b,
            attribute=attr_b,
            excerpt=fallback_excerpt_b,
        )
        return {
            "primary_evidence": citation_a,
            "secondary_evidence": citation_b,
        }


evidence_pairing_service = EvidencePairingService()
