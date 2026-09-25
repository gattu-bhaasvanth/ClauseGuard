from typing import List, Dict, Any, Optional
from collections import defaultdict

from app.models.document import Document
from app.models.attribute import ExtractedAttribute
from app.schemas.matrix import (
    DocumentAttributeValueSchema,
    ComparisonMatrixItemSchema,
    ComparisonMatrixResponseSchema,
)


ATTRIBUTE_LABELS: Dict[str, str] = {
    "carpet_area": "Carpet Area",
    "built_up_area": "Built-Up Area",
    "super_area": "Super Built-Up Area",
    "total_price": "Total Consideration / Price",
    "possession_date": "Promised Possession Date",
    "grace_period_months": "Grace Period",
    "delayed_payment_interest_rate": "Delayed Payment Interest Penalty",
    "rera_registration_number": "RERA Registration Number",
    "developer_name": "Developer Legal Entity",
    "unit_number": "Unit / Apartment Number",
    "tower": "Tower / Block",
    "defect_liability_years": "Defect Liability Period",
}


class DocumentAlignmentMatrix:
    """
    Aligns and collates extracted attributes across all documents in a bundle,
    providing side-by-side comparative views and variance flags.
    """

    def build_matrix(
        self,
        bundle_id: str,
        documents: List[Document],
        attributes: List[ExtractedAttribute],
    ) -> ComparisonMatrixResponseSchema:
        doc_map = {d.id: d for d in documents}

        # Group attributes by attribute_key
        grouped: Dict[str, List[ExtractedAttribute]] = defaultdict(list)
        for attr in attributes:
            grouped[attr.attribute_key].append(attr)

        matrix_items: List[ComparisonMatrixItemSchema] = []
        inconsistent_count = 0

        for key, attrs in grouped.items():
            label = ATTRIBUTE_LABELS.get(key, key.replace("_", " ").title())
            doc_values: List[DocumentAttributeValueSchema] = []

            seen_doc_keys = set()
            normalized_values = set()

            for a in attrs:
                doc = doc_map.get(a.document_id)
                doc_name = doc.file_name if doc else a.document_id
                doc_type = doc.document_type if doc else "OTHER"

                doc_values.append(
                    DocumentAttributeValueSchema(
                        documentId=a.document_id,
                        documentName=doc_name,
                        documentType=doc_type,
                        rawValue=a.attribute_value,
                        normalizedValue=a.normalized_value or a.attribute_value,
                        unit=a.unit or "",
                        sourcePage=a.source_page or 1,
                        sourceClause=a.source_clause,
                        rawExcerpt=a.raw_excerpt,
                    )
                )

                if a.normalized_value:
                    normalized_values.add(a.normalized_value.strip().lower())

            # A field is considered inconsistent if multiple documents provide conflicting normalized values
            is_consistent = len(normalized_values) <= 1
            variance_desc = None
            if not is_consistent:
                inconsistent_count += 1
                distinct_vals = list(normalized_values)
                variance_desc = f"Mismatched values detected: {', '.join(distinct_vals)}"

            matrix_items.append(
                ComparisonMatrixItemSchema(
                    attributeKey=key,
                    label=label,
                    isConsistent=is_consistent,
                    varianceDescription=variance_desc,
                    valuesByDocument=doc_values,
                )
            )

        # Sort matrix items so inconsistent ones appear first
        matrix_items.sort(key=lambda item: item.isConsistent)

        return ComparisonMatrixResponseSchema(
            bundleId=bundle_id,
            totalAttributesCompared=len(matrix_items),
            inconsistentAttributesCount=inconsistent_count,
            matrix=matrix_items,
        )


alignment_matrix_builder = DocumentAlignmentMatrix()
