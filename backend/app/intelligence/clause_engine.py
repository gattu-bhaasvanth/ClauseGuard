import uuid
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.document import Document, DocumentPage
from app.models.clause import Clause
from app.intelligence.segmenter import ClauseBoundaryDetector, RawClauseChunk
from app.intelligence.classifier import ClauseClassifier, ClassificationResult
from app.intelligence.ml.hybrid_classifier import hybrid_clause_classifier
from app.intelligence.obligation_extractor import ObligationExtractor


class ClauseIntelligenceEngine:
    """
    Orchestrates clause segmentation, legal taxonomy classification,
    risk evaluation, obligation attribution, and database persistence.
    """

    def __init__(
        self,
        segmenter: Optional[ClauseBoundaryDetector] = None,
        classifier: Optional[Any] = None,
        obligation_extractor: Optional[ObligationExtractor] = None,
    ):
        self.segmenter = segmenter or ClauseBoundaryDetector()
        self.classifier = classifier or hybrid_clause_classifier
        self.obligation_extractor = obligation_extractor or ObligationExtractor()

    async def process_document_clauses(
        self, session: AsyncSession, bundle_id: str, document_id: str
    ) -> List[Clause]:
        # 1. Fetch document pages
        result = await session.execute(
            select(DocumentPage)
            .filter_by(document_id=document_id)
            .order_by(DocumentPage.page_number.asc())
        )
        pages = result.scalars().all()
        if not pages:
            return []

        # Prepare (page_num, text) tuples
        page_tuples = [(p.page_number, p.raw_text) for p in pages]

        # 2. Segment clauses
        raw_chunks = self.segmenter.segment_pages(page_tuples)

        # 3. Clean existing clauses for this document to avoid duplicates
        await session.execute(delete(Clause).filter_by(document_id=document_id))

        # 4. Classify and create Clause entities
        persisted_clauses: List[Clause] = []
        issues_count = 0

        for chunk in raw_chunks:
            cls_res: ClassificationResult = self.classifier.classify_clause(
                chunk.title, chunk.full_excerpt
            )
            ob_item = self.obligation_extractor.extract_obligation_details(
                chunk.title, chunk.full_excerpt
            )

            if cls_res.status in ("RISK", "INCONSISTENCY"):
                issues_count += 1

            clause_entity = Clause(
                id=f"cls-{uuid.uuid4().hex[:8]}",
                bundle_id=bundle_id,
                document_id=document_id,
                clause_number=chunk.clause_number,
                title=chunk.title,
                category=cls_res.category.value,
                status=cls_res.status,
                severity=cls_res.severity,
                obligation_type=ob_item.party,
                page_number=chunk.page_number,
                preview_text=chunk.preview_text,
                full_excerpt=chunk.full_excerpt,
                analysis_summary=cls_res.analysis_summary,
                risk_details=cls_res.risk_details,
                confidence=cls_res.confidence,
                classification_source=cls_res.classification_source,
                model_version=cls_res.model_version,
                dataset_version=cls_res.dataset_version,
                top_alternatives=cls_res.top_alternatives,
                explanation_notes=cls_res.explanation_notes,
            )
            session.add(clause_entity)
            persisted_clauses.append(clause_entity)

        # 5. Update document clause and issue counts
        doc_res = await session.execute(select(Document).filter_by(id=document_id))
        doc = doc_res.scalar_one_or_none()
        if doc:
            doc.clause_count = len(persisted_clauses)
            doc.issue_count = issues_count

        await session.commit()
        return persisted_clauses


clause_intelligence_engine = ClauseIntelligenceEngine()
