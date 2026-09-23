from typing import List, Optional, Tuple, Dict, Any
import re
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transaction import TransactionBundle
from app.models.document import Document, DocumentPage
from app.models.clause import Clause
from app.models.chunk import DocumentChunk
from app.schemas.rag import (
    RAGQueryRequestSchema,
    RAGQueryResponseSchema,
    EvidenceCitationSchema,
    DocumentIndexingStatusSchema,
    ChunkResponseSchema,
)
from app.rag.vector_engine import FastEmbedVectorEngine
from app.rag.chunker import ClauseCentricChunker, ProcessedChunk
from app.rag.retriever import HybridRetriever, RankedChunkResult


class TransactionRAGService:
    """
    Orchestrates local Grounded Transaction RAG:
    - Indexes document chunks with 384-d FastEmbed vectors into SQLite
    - Executes hybrid retrieval (dense 384-d cosine + BM25 lexical + RRF)
    - Anti-hallucination refusal when evidence is absent
    - Grounds answers strictly with clickable citation chips
    - 100% offline, local CPU execution with zero external API calls
    """

    CONFIDENCE_THRESHOLD = 0.28  # Minimum combined confidence required to answer

    def __init__(self):
        self.vector_engine = FastEmbedVectorEngine.get_instance()
        self.chunker = ClauseCentricChunker()
        self.retriever = HybridRetriever(self.vector_engine)

    async def index_document(
        self,
        db: AsyncSession,
        bundle_id: str,
        document_id: str,
    ) -> DocumentIndexingStatusSchema:
        """
        Extracts chunks for a document, generates 384-d embeddings, and saves to SQLite.
        """
        # Fetch document with clauses and pages
        stmt = (
            select(Document)
            .where(Document.id == document_id, Document.bundle_id == bundle_id)
            .options(selectinload(Document.clauses), selectinload(Document.pages))
        )
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document {document_id} not found in bundle {bundle_id}")

        # Remove existing chunks for this document to allow clean re-indexing
        del_stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        await db.execute(del_stmt)

        # Generate structured chunks
        raw_chunks: List[ProcessedChunk] = self.chunker.chunk_document(document)
        if not raw_chunks:
            await db.commit()
            return DocumentIndexingStatusSchema(
                bundleId=bundle_id,
                documentId=document_id,
                documentName=document.file_name,
                chunksIndexed=0,
                message="No extractable text or clauses found in document.",
            )

        # Batch embed chunk texts (384-d)
        texts_to_embed = [rc.chunk_text for rc in raw_chunks]
        embeddings = self.vector_engine.embed_batch(texts_to_embed)

        db_chunks = []
        for rc, emb in zip(raw_chunks, embeddings):
            chunk_rec = DocumentChunk(
                bundle_id=rc.bundle_id,
                document_id=rc.document_id,
                page_number=rc.page_number,
                clause_number=rc.clause_number,
                clause_title=rc.clause_title,
                chunk_type=rc.chunk_type,
                chunk_text=rc.chunk_text,
                embedding=emb,  # 384-d list of floats
            )
            db.add(chunk_rec)
            db_chunks.append(chunk_rec)

        await db.commit()

        return DocumentIndexingStatusSchema(
            bundleId=bundle_id,
            documentId=document_id,
            documentName=document.file_name,
            chunksIndexed=len(db_chunks),
            message=f"Successfully indexed {len(db_chunks)} chunks with 384-d FastEmbed vectors.",
        )

    async def index_all_bundle_documents(self, db: AsyncSession, bundle_id: str) -> int:
        """
        Indexes all documents within a transaction bundle.
        """
        stmt = select(Document).where(Document.bundle_id == bundle_id)
        result = await db.execute(stmt)
        documents = result.scalars().all()

        total_chunks = 0
        for doc in documents:
            status = await self.index_document(db, bundle_id, doc.id)
            total_chunks += status.chunksIndexed

        return total_chunks

    async def list_chunks(
        self,
        db: AsyncSession,
        bundle_id: str,
        document_id: Optional[str] = None,
    ) -> List[ChunkResponseSchema]:
        """
        List all indexed chunks for a bundle or document.
        """
        query = select(DocumentChunk).where(DocumentChunk.bundle_id == bundle_id)
        if document_id:
            query = query.where(DocumentChunk.document_id == document_id)
        query = query.order_by(DocumentChunk.page_number, DocumentChunk.clause_number)

        result = await db.execute(query)
        chunks = result.scalars().all()

        return [
            ChunkResponseSchema(
                id=c.id,
                bundleId=c.bundle_id,
                documentId=c.document_id,
                pageNumber=c.page_number,
                clauseNumber=c.clause_number,
                clauseTitle=c.clause_title,
                chunkType=c.chunk_type,
                chunkText=c.chunk_text,
                hasEmbedding=c.embedding is not None and len(c.embedding) == 384,
                createdAt=c.created_at.isoformat() if c.created_at else "",
            )
            for c in chunks
        ]

    async def query_transaction(
        self,
        db: AsyncSession,
        bundle_id: str,
        query_text: str,
        top_k: int = 5,
    ) -> RAGQueryResponseSchema:
        """
        Executes grounded transaction question answering.
        Combines 384-d FastEmbed semantic search, lexical matching, anti-hallucination refusal,
        and citation chip construction.
        """
        clean_query = query_text.strip()
        if len(clean_query) < 2:
            return RAGQueryResponseSchema(
                query=clean_query,
                answer="Please enter a more specific question regarding your transaction documents.",
                grounded=False,
                status="INSUFFICIENT_EVIDENCE",
                confidence=0.0,
                citations=[],
                bundleId=bundle_id,
            )

        # 1. Fetch chunks for bundle
        stmt = select(DocumentChunk).where(DocumentChunk.bundle_id == bundle_id)
        res = await db.execute(stmt)
        chunks = res.scalars().all()

        # If no chunks exist, auto-index the bundle documents
        if not chunks:
            await self.index_all_bundle_documents(db, bundle_id)
            res = await db.execute(stmt)
            chunks = res.scalars().all()

        if not chunks:
            return RAGQueryResponseSchema(
                query=clean_query,
                answer="No documents or clauses are available in this transaction bundle to answer your question.",
                grounded=False,
                status="INSUFFICIENT_EVIDENCE",
                confidence=0.0,
                citations=[],
                bundleId=bundle_id,
            )

        # 2. Hybrid Retrieval
        ranked_results: List[RankedChunkResult] = self.retriever.retrieve(
            query=clean_query,
            chunks=list(chunks),
            top_k=top_k,
        )

        if not ranked_results:
            return self._refusal_response(clean_query, bundle_id)

        top_match = ranked_results[0]

        # 3. Grounding & Anti-Hallucination Guardrail
        # Check if the query is relevant to any retrieved chunk
        is_grounded = self._verify_grounding(clean_query, ranked_results)
        if not is_grounded:
            return self._refusal_response(clean_query, bundle_id)

        # Fetch document metadata for citation assembly
        doc_ids = {r.chunk.document_id for r in ranked_results}
        docs_stmt = select(Document).where(Document.id.in_(doc_ids))
        docs_res = await db.execute(docs_stmt)
        docs_by_id = {d.id: d for d in docs_res.scalars().all()}

        # 4. Construct Citations
        citations: List[EvidenceCitationSchema] = []
        for r in ranked_results:
            doc = docs_by_id.get(r.chunk.document_id)
            doc_name = doc.file_name if doc else "Document"
            doc_type = doc.document_type if doc else "UNKNOWN"

            # Create concise excerpt from chunk text
            excerpt = self._extract_excerpt(r.chunk.chunk_text, clean_query)

            citations.append(
                EvidenceCitationSchema(
                    documentId=r.chunk.document_id,
                    documentName=doc_name,
                    documentType=doc_type,
                    pageNumber=r.chunk.page_number,
                    clauseNumber=r.chunk.clause_number,
                    clauseTitle=r.chunk.clause_title,
                    excerpt=excerpt,
                    relevanceScore=round(r.combined_confidence, 3),
                )
            )

        # 5. Synthesize Grounded Answer
        answer_text = self._synthesize_grounded_answer(clean_query, ranked_results, docs_by_id)

        return RAGQueryResponseSchema(
            query=clean_query,
            answer=answer_text,
            grounded=True,
            status="GROUNDED",
            confidence=round(top_match.combined_confidence, 2),
            citations=citations,
            bundleId=bundle_id,
        )

    def _verify_grounding(self, query: str, ranked: List[RankedChunkResult]) -> bool:
        """
        Anti-hallucination guardrail:
        Strictly verify whether the retrieved chunks actually ground the query topic.
        If top match has low cosine similarity and zero or negligible lexical overlap, reject.
        """
        top = ranked[0]

        # 1. Lexical keywords present + reasonable dense support
        if top.lexical_score > 0 and top.dense_score >= 0.25:
            return True

        # 2. Strong semantic similarity (paraphrased queries without exact keyword overlap)
        if top.dense_score >= 0.45:
            return True

        # 3. Direct legal identifier match (e.g. "Clause 8.2")
        if top.lexical_score >= 2.0:
            return True

        return False

    def _refusal_response(self, query: str, bundle_id: str) -> RAGQueryResponseSchema:
        """
        Returns a strict anti-hallucination refusal response.
        """
        # Extract subject from query
        subject = query.strip("?. ")
        refusal_msg = (
            f"Based on the uploaded documents in this transaction bundle, there is no verified mention "
            f"or specific provision regarding '{subject}'. Please verify directly with the developer "
            f"or request the relevant schedule/agreement."
        )
        return RAGQueryResponseSchema(
            query=query,
            answer=refusal_msg,
            grounded=False,
            status="INSUFFICIENT_EVIDENCE",
            confidence=0.0,
            citations=[],
            bundleId=bundle_id,
        )

    def _extract_excerpt(self, chunk_text: str, query: str, max_words: int = 50) -> str:
        """
        Extract the most query-relevant excerpt from chunk text.
        """
        lines = [line.strip() for line in chunk_text.split("\n") if line.strip()]
        if not lines:
            return ""

        query_terms = set(re.findall(r"\w+", query.lower()))
        best_line = lines[0]
        max_overlap = -1

        for line in lines:
            line_terms = set(re.findall(r"\w+", line.lower()))
            overlap = len(query_terms.intersection(line_terms))
            if overlap > max_overlap:
                max_overlap = overlap
                best_line = line

        words = best_line.split()
        if len(words) > max_words:
            return " ".join(words[:max_words]) + "..."
        return best_line

    def _synthesize_grounded_answer(
        self,
        query: str,
        ranked: List[RankedChunkResult],
        docs_by_id: Dict[str, Document],
    ) -> str:
        """
        Synthesizes a grounded, deterministic answer citing specific clauses, numbers,
        dates, percentages, and terms directly from retrieved context chunks.
        """
        top_match = ranked[0]
        top_chunk = top_match.chunk
        doc = docs_by_id.get(top_chunk.document_id)
        doc_label = doc.file_name if doc else "the transaction documents"

        clause_ref = f"{top_chunk.clause_number}: {top_chunk.clause_title}" if top_chunk.clause_number else f"Page {top_chunk.page_number}"

        # Clean chunk text lines
        lines = [l.strip() for l in top_chunk.chunk_text.split("\n") if l.strip()]
        relevant_body = " ".join(lines[1:]) if len(lines) > 1 else (lines[0] if lines else "")

        # Look for key figures (percentages, amounts, dates, durations)
        key_figures = re.findall(r"(\d+(?:\.\d+)?%|\b(?:rs\.?|inr)\s*[\d,]+|\b\d+\s*(?:days|months|years|sq\.?\s*ft|sqft)\b)", relevant_body, re.IGNORECASE)

        answer_parts = []
        answer_parts.append(f"According to **{clause_ref}** of **{doc_label}** (Page {top_chunk.page_number}):")

        # Include direct text summary
        # If relevant body is concise, present it directly; if long, present the leading sentences
        sentences = re.split(r"(?<=[.!?])\s+", relevant_body)
        summary_sentence = " ".join(sentences[:3]) if sentences else relevant_body
        answer_parts.append(f"> \"{summary_sentence}\"")

        if key_figures:
            unique_figures = list(dict.fromkeys([f.strip() for f in key_figures]))[:4]
            answer_parts.append(f"\n**Key Terms Stated:** {', '.join(unique_figures)}.")

        # If a secondary highly relevant chunk exists, mention it
        if len(ranked) > 1 and ranked[1].combined_confidence >= 0.35:
            second_chunk = ranked[1].chunk
            sec_doc = docs_by_id.get(second_chunk.document_id)
            sec_doc_label = sec_doc.file_name if sec_doc else "related document"
            sec_ref = f"{second_chunk.clause_number}" if second_chunk.clause_number else f"Page {second_chunk.page_number}"
            answer_parts.append(f"\nAdditionally, **{sec_ref}** in **{sec_doc_label}** specifies related provisions.")

        return "\n\n".join(answer_parts)
