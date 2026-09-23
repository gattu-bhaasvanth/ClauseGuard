import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.document import Document, DocumentPage
from app.models.clause import Clause
from app.models.attribute import ExtractedAttribute
from app.models.transaction import TransactionBundle
from app.intelligence.segmenter import ClauseBoundaryDetector, RawClauseChunk
from app.intelligence.entity_extractor import (
    TransactionEntityExtractor,
    transaction_entity_extractor,
    ExtractedEntity,
)
from app.schemas.attribute import (
    UnifiedTransactionMetadataSchema,
    PaymentMilestoneItemSchema,
)


class TransactionMetadataEngine:
    """
    Coordinates entity extraction, normalization, deduplication, and persistence
    across document pages, and synthesizes the Unified Transaction Model.
    """

    def __init__(self, extractor: Optional[TransactionEntityExtractor] = None):
        self.extractor = extractor or transaction_entity_extractor
        self.segmenter = ClauseBoundaryDetector()

    async def process_document_metadata(
        self, session: AsyncSession, bundle_id: str, document_id: str
    ) -> List[ExtractedAttribute]:
        """
        Extracts structured entities from document pages and clauses,
        persisting them to the database.
        """
        # 1. Fetch document pages
        res_pages = await session.execute(
            select(DocumentPage)
            .filter_by(document_id=document_id)
            .order_by(DocumentPage.page_number.asc())
        )
        pages = res_pages.scalars().all()
        if not pages:
            return []

        page_tuples = [(p.page_number, p.raw_text) for p in pages]

        # 2. Fetch existing clauses or segment dynamically
        res_clauses = await session.execute(
            select(Clause)
            .filter_by(document_id=document_id)
            .order_by(Clause.page_number.asc())
        )
        db_clauses = res_clauses.scalars().all()

        clause_chunks = []
        if db_clauses:
            for c in db_clauses:
                clause_chunks.append(
                    RawClauseChunk(
                        clause_number=c.clause_number,
                        title=c.title,
                        full_excerpt=c.full_excerpt or c.preview_text,
                        preview_text=c.preview_text,
                        page_number=c.page_number,
                    )
                )
        else:
            clause_chunks = self.segmenter.segment_pages(page_tuples)

        # 3. Extract entities
        entities: List[ExtractedEntity] = self.extractor.extract_from_clauses_and_pages(
            pages=page_tuples, clauses=clause_chunks
        )

        # 4. Clean previous extracted attributes for this document
        await session.execute(
            delete(ExtractedAttribute).filter_by(document_id=document_id)
        )

        # 5. Persist extracted attributes
        persisted: List[ExtractedAttribute] = []
        for ent in entities:
            attr = ExtractedAttribute(
                id=f"attr-{uuid.uuid4().hex[:8]}",
                bundle_id=bundle_id,
                document_id=document_id,
                attribute_key=ent.attribute_key,
                attribute_value=ent.attribute_value,
                normalized_value=ent.normalized_value,
                unit=ent.unit,
                source_page=ent.source_page,
                source_clause=ent.source_clause,
                raw_excerpt=ent.raw_excerpt,
                confidence=ent.confidence,
            )
            session.add(attr)
            persisted.append(attr)

        await session.commit()
        return persisted

    async def get_unified_transaction_metadata(
        self, session: AsyncSession, bundle_id: str
    ) -> UnifiedTransactionMetadataSchema:
        """
        Synthesizes the bundle-level Unified Transaction Model across all extracted attributes.
        """
        # Fetch bundle record
        res_bundle = await session.execute(
            select(TransactionBundle).filter_by(id=bundle_id)
        )
        bundle = res_bundle.scalar_one_or_none()

        # Fetch all extracted attributes for this bundle
        res_attrs = await session.execute(
            select(ExtractedAttribute).filter_by(bundle_id=bundle_id)
        )
        attrs = res_attrs.scalars().all()

        # Initialize schema with bundle defaults
        schema = UnifiedTransactionMetadataSchema(
            bundleId=bundle_id,
            carpetAreaSqft=bundle.carpet_area_sqft if bundle else None,
            superAreaSqft=bundle.super_area_sqft if bundle else None,
            advertisedCarpetAreaSqft=bundle.advertised_carpet_area_sqft if bundle else None,
            salePrice=bundle.sale_price if bundle else None,
            possessionDate=bundle.possession_date if bundle else None,
            gracePeriodMonths=bundle.grace_period_months if bundle else None,
            unitNumber=bundle.unit if bundle else None,
            floor=bundle.floor if bundle else None,
            tower=bundle.tower if bundle else None,
            developer=bundle.developer if bundle else None,
            totalAttributesExtracted=len(attrs),
        )

        # Overlay extracted attributes from documents
        for a in attrs:
            key = a.attribute_key
            norm_val = a.normalized_value

            if key == "carpet_area" and norm_val:
                try:
                    schema.carpetAreaSqft = float(norm_val)
                except ValueError:
                    pass
            elif key == "super_area" and norm_val:
                try:
                    schema.superAreaSqft = float(norm_val)
                except ValueError:
                    pass
            elif key == "total_price" and norm_val:
                try:
                    schema.salePrice = float(norm_val)
                except ValueError:
                    pass
            elif key == "possession_date" and norm_val:
                schema.possessionDate = norm_val
            elif key == "grace_period_months" and norm_val:
                try:
                    schema.gracePeriodMonths = int(norm_val)
                except ValueError:
                    pass
            elif key == "unit_number" and norm_val:
                schema.unitNumber = norm_val
            elif key == "tower" and norm_val:
                schema.tower = norm_val
            elif key == "developer_name" and norm_val:
                schema.developer = norm_val
            elif key == "rera_registration_number" and norm_val:
                schema.reraNumber = norm_val
            elif key == "delayed_payment_interest_rate" and norm_val:
                try:
                    schema.delayedPaymentRate = float(norm_val)
                except ValueError:
                    pass

        return schema


metadata_engine = TransactionMetadataEngine()
