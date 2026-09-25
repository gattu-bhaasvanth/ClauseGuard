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

    def _identify_target_documents(self, query: str, documents: List[Document]) -> List[Document]:
        """
        Detects if user query explicitly mentions one or more specific documents.
        Supports filenames, document types, and common legal aliases.
        """
        q = query.lower()
        matched: List[Document] = []
        for doc in documents:
            fname = (doc.file_name or "").lower()
            dtype = (doc.document_type or "").lower()
            stem = fname.rsplit(".", 1)[0]

            is_match = False
            # Check exact stem / filename mention
            if stem and stem in q:
                is_match = True
            elif "allotment" in q and ("allotment" in fname or "allotment" in dtype):
                is_match = True
            elif ("bba" in q or "builder buyer" in q or "builder-buyer" in q) and ("bba" in fname or "builder" in fname or "buyer" in fname or "bba" in dtype):
                is_match = True
            elif ("sale agreement" in q or "agreement for sale" in q) and ("sale_agreement" in fname or "sale agreement" in fname or "sale" in dtype):
                is_match = True
            elif ("brochure" in q or "marketing" in q) and ("brochure" in fname or "marketing" in fname or "brochure" in dtype or "marketing" in dtype):
                is_match = True
            elif ("payment schedule" in q or "payment plan" in q) and ("payment" in fname or "payment" in dtype):
                is_match = True

            if is_match and doc not in matched:
                matched.append(doc)

        return matched

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
        document-scoped query routing, and citation chip construction.
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

        # 1. Fetch all documents for this bundle to enable scoped routing and citations
        docs_stmt = select(Document).where(Document.bundle_id == bundle_id)
        docs_res = await db.execute(docs_stmt)
        all_docs = docs_res.scalars().all()
        docs_by_id = {d.id: d for d in all_docs}

        # 2. Fetch chunks for bundle
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

        # 3. Detect Document Scope from Query
        target_docs = self._identify_target_documents(clean_query, all_docs)

        if len(target_docs) == 1:
            # Single document scope specified (e.g. "What is the possession date in the Allotment Letter?")
            target_doc_id = target_docs[0].id
            scoped_chunks = [c for c in chunks if c.document_id == target_doc_id]
            if scoped_chunks:
                ranked_results = self.retriever.retrieve(
                    query=clean_query,
                    chunks=scoped_chunks,
                    top_k=top_k,
                )
            else:
                ranked_results = self.retriever.retrieve(
                    query=clean_query,
                    chunks=list(chunks),
                    top_k=top_k,
                )
        elif len(target_docs) > 1:
            # Multi-document scope specified (e.g. "What are the possession dates in the BBA and Allotment Letter?")
            ranked_results = []
            for t_doc in target_docs:
                doc_chunks = [c for c in chunks if c.document_id == t_doc.id]
                if doc_chunks:
                    doc_ranked = self.retriever.retrieve(
                        query=clean_query,
                        chunks=doc_chunks,
                        top_k=max(2, top_k // len(target_docs)),
                    )
                    ranked_results.extend(doc_ranked)
        else:
            # General query across entire bundle
            # If asking about possession across the transaction, prioritize chunks mentioning handover/possession
            is_possession_query = any(k in clean_query.lower() for k in ["possession", "handover", "completion date"])
            if is_possession_query:
                possession_chunks = [c for c in chunks if any(k in c.chunk_text.lower() for k in ["possession", "handover", "completion"])]
                if len(possession_chunks) > 0:
                    ranked_results = self.retriever.retrieve(
                        query=clean_query,
                        chunks=possession_chunks,
                        top_k=top_k,
                    )
                else:
                    ranked_results = self.retriever.retrieve(
                        query=clean_query,
                        chunks=list(chunks),
                        top_k=top_k,
                    )
            else:
                ranked_results = self.retriever.retrieve(
                    query=clean_query,
                    chunks=list(chunks),
                    top_k=top_k,
                )

        if not ranked_results:
            return self._refusal_response(clean_query, bundle_id)

        top_match = ranked_results[0]

        # 4. Grounding & Anti-Hallucination Guardrail
        is_grounded = self._verify_grounding(clean_query, ranked_results)
        if not is_grounded:
            return self._refusal_response(clean_query, bundle_id)

        # 5. Construct Citations
        citations: List[EvidenceCitationSchema] = []
        for r in ranked_results:
            doc = docs_by_id.get(r.chunk.document_id)
            doc_name = doc.file_name if doc else "Document"
            doc_type = doc.document_type if doc else "UNKNOWN"

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

        # 6. Synthesize Grounded Answer
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
        Preserves date precision honestly (never invents missing day/month precision).
        """
        from app.intelligence.entity_normalizer import DateNormalizer

        doc_ids_represented = list(dict.fromkeys([r.chunk.document_id for r in ranked]))
        is_multi_doc = len(doc_ids_represented) > 1

        q_lower = query.lower()
        is_possession = any(k in q_lower for k in ["possession", "handover", "delivery", "completion"])
        is_area = any(k in q_lower for k in ["carpet area", "super area", "area of the apartment", "unit area", "sq.ft", "sqft"])

        # Handle multi-document comparative questions
        if is_multi_doc and (is_possession or is_area or len(doc_ids_represented) >= 2):
            answer_parts = ["### Cross-Document Verification\n"]
            doc_summaries = []
            extracted_facts = {}

            for doc_id in doc_ids_represented[:3]:
                doc = docs_by_id.get(doc_id)
                doc_name = doc.file_name if doc else "Document"
                doc_chunk = next(r.chunk for r in ranked if r.chunk.document_id == doc_id)
                clause_ref = f"{doc_chunk.clause_number}: {doc_chunk.clause_title}" if doc_chunk.clause_number else f"Page {doc_chunk.page_number}"
                excerpt = self._extract_excerpt(doc_chunk.chunk_text, query)

                fact_note = ""
                if is_possession:
                    norm_res = DateNormalizer.normalize_with_precision(doc_chunk.chunk_text)
                    if norm_res:
                        norm_val, prec = norm_res
                        if prec == "YEAR":
                            fact_note = f" (Target Year: **{norm_val}**; exact date not specified)"
                        elif prec == "MONTH":
                            fact_note = f" (Projected: **{norm_val}**)"
                        else:
                            fact_note = f" (Committed Date: **{norm_val}**)"
                        extracted_facts[doc_name] = (norm_val, prec)

                doc_summaries.append(
                    f"• **{doc_name}** ({clause_ref}){fact_note}:\n  > \"{excerpt}\""
                )

            answer_parts.extend(doc_summaries)

            if is_possession and len(extracted_facts) >= 2:
                values = list(extracted_facts.values())
                if any(v[0] != values[0][0] for v in values):
                    answer_parts.append(
                        "\n⚠️ **Discrepancy Note**: The formal agreement handover date shifts from the preliminary allotment/brochure timeline."
                    )

            return "\n\n".join(answer_parts)

        # Single document grounded synthesis
        top_match = ranked[0]
        top_chunk = top_match.chunk
        doc = docs_by_id.get(top_chunk.document_id)
        doc_label = doc.file_name if doc else "the transaction documents"

        clause_ref = f"{top_chunk.clause_number}: {top_chunk.clause_title}" if top_chunk.clause_number else f"Page {top_chunk.page_number}"

        lines = [l.strip() for l in top_chunk.chunk_text.split("\n") if l.strip()]
        relevant_body = " ".join(lines[1:]) if len(lines) > 1 else (lines[0] if lines else "")

        key_figures = re.findall(
            r"(\d+(?:\.\d+)?%|\b(?:rs\.?|inr|₹)\s*[\d,]+|\b\d+\s*(?:days|months|years|sq\.?\s*ft|sqft)\b)",
            relevant_body,
            re.IGNORECASE,
        )

        answer_parts = []
        answer_parts.append(f"According to **{clause_ref}** of **{doc_label}** (Page {top_chunk.page_number}):")

        sentences = re.split(r"(?<=[.!?])\s+", relevant_body)
        summary_sentence = " ".join(sentences[:3]) if sentences else relevant_body
        answer_parts.append(f"> \"{summary_sentence}\"")

        if is_possession:
            norm_res = DateNormalizer.normalize_with_precision(top_chunk.chunk_text)
            if norm_res:
                norm_val, prec = norm_res
                if prec == "YEAR":
                    answer_parts.append(f"\n**Target Handover Stated**: {norm_val} (Year precision; exact date is not specified in this document).")
                elif prec == "MONTH":
                    answer_parts.append(f"\n**Target Handover Stated**: {norm_val} (Month precision).")
                else:
                    answer_parts.append(f"\n**Contractual Handover Date**: {norm_val}.")
        elif key_figures:
            unique_figures = list(dict.fromkeys([f.strip() for f in key_figures]))[:4]
            answer_parts.append(f"\n**Key Terms Stated:** {', '.join(unique_figures)}.")

        if len(ranked) > 1 and ranked[1].combined_confidence >= 0.35 and ranked[1].chunk.document_id != top_chunk.document_id:
            second_chunk = ranked[1].chunk
            sec_doc = docs_by_id.get(second_chunk.document_id)
            sec_doc_label = sec_doc.file_name if sec_doc else "related document"
            sec_ref = f"{second_chunk.clause_number}" if second_chunk.clause_number else f"Page {second_chunk.page_number}"
            answer_parts.append(f"\nAdditionally, **{sec_ref}** in **{sec_doc_label}** specifies related provisions.")

        return "\n\n".join(answer_parts)

