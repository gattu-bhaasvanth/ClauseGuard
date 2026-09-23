from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.transaction import TransactionBundle
from app.models.document import Document
from app.schemas.rag import (
    RAGQueryRequestSchema,
    RAGQueryResponseSchema,
    DocumentIndexingStatusSchema,
    ChunkResponseSchema,
)
from app.rag.rag_service import TransactionRAGService

router = APIRouter(prefix="/transactions", tags=["RAG & Semantic Exploration"])
rag_service = TransactionRAGService()


@router.post(
    "/{transaction_id}/rag/query",
    response_model=RAGQueryResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def query_transaction_rag(
    transaction_id: str,
    payload: RAGQueryRequestSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    Ask a natural-language question about the transaction bundle.
    Returns a grounded answer supported by exact citation chips (Document -> Page -> Clause -> Excerpt).
    Executes 100% locally using 384-dimensional FastEmbed embeddings and hybrid retrieval.
    Strictly refuses to speculate if evidence is absent.
    """
    # Verify transaction bundle exists
    bundle_res = await db.execute(select(TransactionBundle).where(TransactionBundle.id == transaction_id))
    bundle = bundle_res.scalar_one_or_none()
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )

    return await rag_service.query_transaction(
        db=db,
        bundle_id=transaction_id,
        query_text=payload.query,
        top_k=payload.topK or 5,
    )


@router.post(
    "/{transaction_id}/documents/{document_id}/rag/index",
    response_model=DocumentIndexingStatusSchema,
    status_code=status.HTTP_200_OK,
)
async def index_document_for_rag(
    transaction_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Index a single document into 384-dimensional vector chunks in SQLite.
    Preserves clause boundaries, page numbers, and provenance metadata.
    """
    doc_res = await db.execute(
        select(Document).where(Document.id == document_id, Document.bundle_id == transaction_id)
    )
    doc = doc_res.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found in transaction '{transaction_id}'.",
        )

    return await rag_service.index_document(db, transaction_id, document_id)


@router.post(
    "/{transaction_id}/rag/index-all",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def index_all_documents_for_rag(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Index all documents in the transaction bundle for RAG retrieval.
    """
    bundle_res = await db.execute(select(TransactionBundle).where(TransactionBundle.id == transaction_id))
    bundle = bundle_res.scalar_one_or_none()
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )

    total_chunks = await rag_service.index_all_bundle_documents(db, transaction_id)
    return {
        "bundleId": transaction_id,
        "totalChunksIndexed": total_chunks,
        "message": f"Successfully indexed {total_chunks} chunks across all bundle documents.",
    }


@router.get(
    "/{transaction_id}/rag/chunks",
    response_model=List[ChunkResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_transaction_chunks(
    transaction_id: str,
    document_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all indexed chunks and provenance for a transaction bundle.
    """
    bundle_res = await db.execute(select(TransactionBundle).where(TransactionBundle.id == transaction_id))
    bundle = bundle_res.scalar_one_or_none()
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )

    return await rag_service.list_chunks(db, transaction_id, document_id)
