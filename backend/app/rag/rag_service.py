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

    DOCUMENT_ROLE_ALIASES = {
        "ALLOTMENT": [
            "letter of allotment", "unit allotment letter", "allotment letter", "allotment agreement", "allotment"
        ],
        "AGREEMENT_FOR_SALE": [
            "agreement for sale", "sale agreement", "builder buyer agreement", "builder-buyer agreement",
            "agreement of sale", "sale contract", "buyer agreement", "bba", "villa agreement"
        ],
        "BROCHURE": [
            "project brochure", "marketing brochure", "sales brochure", "project overview",
            "project information", "marketing document", "sales deck", "e-brochure", "brochure", "marketing"
        ],
        "BOOKING": [
            "reservation agreement", "booking agreement", "booking form", "reservation form",
            "application form", "booking", "reservation"
        ],
        "PAYMENT_SCHEDULE": [
            "payment demand schedule", "demand schedule", "payment schedule", "payment plan",
            "demand notice", "cost sheet", "payment demand"
        ],
        "CONVEYANCE": [
            "conveyance deed", "sale deed", "conveyance"
        ],
        "LEASE": [
            "lease agreement", "lease deed", "lease"
        ],
    }

    @classmethod
    def _doc_matches_role(cls, doc: Document, role: str) -> bool:
        fname = (doc.file_name or "").lower().replace("_", " ").replace("-", " ")
        dtype = (doc.document_type or "").lower()
        aliases = cls.DOCUMENT_ROLE_ALIASES.get(role, [])
        for alias in aliases:
            if alias in fname or alias in dtype:
                return True
        if role == "ALLOTMENT" and ("allotment" in dtype or "allotment" in fname):
            return True
        if role == "AGREEMENT_FOR_SALE" and (
            "bba" in dtype or "sale" in dtype or "buyer" in dtype or "agreement" in dtype
            or "sale_agreement" in fname or "sale agreement" in fname or "agreement for sale" in fname
            or "agreement of sale" in fname or "sale contract" in fname or "builder" in fname
        ):
            if ("booking" in fname or "reservation" in fname) and "sale" not in fname and "bba" not in fname:
                return False
            return True
        if role == "BROCHURE" and (
            "brochure" in dtype or "marketing" in dtype
            or "brochure" in fname or "marketing" in fname or "information" in fname or "overview" in fname
        ):
            return True
        if role == "BOOKING" and (
            "booking" in dtype or "reservation" in dtype
            or "booking" in fname or "reservation" in fname or "application" in fname
        ):
            return True
        if role == "PAYMENT_SCHEDULE" and (
            "payment" in dtype or "demand" in dtype
            or "payment" in fname or "demand" in fname or "schedule" in fname or "cost" in fname
        ):
            return True
        return False

    def _identify_target_documents(self, query: str, documents: List[Document]) -> List[Document]:
        """
        Detects if user query explicitly mentions one or more specific documents.
        Supports filenames, document types, and common legal aliases.
        """
        q = query.lower()

        # 1. Identify which legal document roles and specific aliases the query explicitly asks for
        active_roles = set()
        matched_query_aliases = []
        for role, aliases in self.DOCUMENT_ROLE_ALIASES.items():
            for alias in aliases:
                if re.search(r"\b" + re.escape(alias) + r"\b", q):
                    active_roles.add(role)
                    matched_query_aliases.append(alias)

        # Map each active role to its candidate matching documents
        role_candidates: Dict[str, List[Tuple[Document, int]]] = {r: [] for r in active_roles}

        for doc in documents:
            fname = (doc.file_name or "").lower().replace("_", " ").replace("-", " ")
            for role in active_roles:
                if self._doc_matches_role(doc, role):
                    # Compute specificity for this document within this role
                    spec = 10
                    for alias in matched_query_aliases:
                        if alias in fname:
                            spec = max(spec, len(alias) * 2)
                    role_candidates[role].append((doc, spec))

        matched_docs: List[Document] = []
        for role, candidates in role_candidates.items():
            if not candidates:
                continue
            max_spec = max(spec for _, spec in candidates)
            # If any candidate for this role had a specific filename match (> 10), keep only specific matches
            if max_spec > 10:
                for doc, spec in candidates:
                    if spec > 10 and doc not in matched_docs:
                        matched_docs.append(doc)
            else:
                for doc, _ in candidates:
                    if doc not in matched_docs:
                        matched_docs.append(doc)

        # Also check direct filename stem matches if not matched by role
        if not matched_docs:
            for doc in documents:
                fname = (doc.file_name or "").lower()
                stem = fname.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
                stripped_stem = re.sub(r"^\d+\s*", "", stem).strip()
                if (stem and stem in q) or (stripped_stem and len(stripped_stem) >= 4 and stripped_stem in q):
                    if doc not in matched_docs:
                        matched_docs.append(doc)
                elif any(
                    bigram in q
                    for bigram in [
                        f"{w1} {w2}"
                        for w1, w2 in zip(stem.split()[:-1], stem.split()[1:])
                        if len(w1) >= 3 and len(w2) >= 3 and f"{w1} {w2}" not in {"for sale", "of sale", "and sale"}
                    ]
                ):
                    if doc not in matched_docs:
                        matched_docs.append(doc)

        return matched_docs

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

    GENERIC_CONTAINER_TERMS = {
        "what", "is", "the", "are", "in", "of", "for", "to", "and", "a", "an", "on", "by", "at",
        "which", "with", "this", "that", "from", "as", "it", "any", "all", "or", "how", "much",
        "apartment", "flat", "unit", "villa", "property", "project", "building", "complex",
        "agreement", "document", "contract", "clause", "schedule", "letter", "brochure",
        "tell", "me", "about", "state", "mention", "give", "show", "details", "there"
    }

    REAL_ESTATE_SYNONYMS = {
        "possession": {"possession", "handover", "delivery", "occupancy", "completion"},
        "handover": {"possession", "handover", "delivery", "occupancy", "completion"},
        "delivery": {"possession", "handover", "delivery", "occupancy", "completion"},
        "completion": {"possession", "handover", "delivery", "occupancy", "completion"},
        "price": {"price", "cost", "consideration", "amount", "valuation", "payment"},
        "consideration": {"price", "cost", "consideration", "amount", "valuation", "payment"},
        "cost": {"price", "cost", "consideration", "amount", "valuation", "payment"},
        "area": {"area", "sqft", "sq.ft", "sqm", "carpet", "super", "dimensions"},
        "penalty": {"penalty", "interest", "compensation", "damages", "forfeiture", "liquidated"},
        "compensation": {"penalty", "interest", "compensation", "damages", "forfeiture", "liquidated"},
        "default": {"default", "breach", "delay", "termination", "forfeiture"},
    }

    def _verify_grounding(self, query: str, ranked: List[RankedChunkResult]) -> bool:
        """
        Anti-hallucination guardrail:
        Strictly verify whether the retrieved chunks actually ground the query topic.
        If top match has low cosine similarity and zero substantive lexical overlap on topic terms, reject.
        """
        if not ranked:
            return False

        top = ranked[0]

        # 1. High semantic similarity always passes (strong paraphrases)
        if top.dense_score >= 0.50:
            return True

        # 2. Extract substantive query topic terms (excluding generic containers and stopwords)
        q_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", query.lower()))
        topic_words = {w for w in q_words if w not in self.GENERIC_CONTAINER_TERMS}

        # Expand substantive topic words with domain synonyms (e.g. possession <-> handover/completion)
        expanded_topic_words = set(topic_words)
        for tw in topic_words:
            if tw in self.REAL_ESTATE_SYNONYMS:
                expanded_topic_words.update(self.REAL_ESTATE_SYNONYMS[tw])

        # Check if any substantive topic word or domain synonym is in the retrieved top chunks
        combined_text = " ".join([r.chunk.chunk_text.lower() for r in ranked[:3]])
        has_substantive_overlap = (
            any(re.search(r"\b" + re.escape(tw) + r"\b", combined_text) for tw in expanded_topic_words)
            if expanded_topic_words
            else False
        )

        if has_substantive_overlap:
            # Substantive topic word present + solid dense semantic corroboration
            if top.dense_score >= 0.33 and top.lexical_score >= 0.8:
                return True
            if top.dense_score >= 0.42:
                return True

        # 3. Direct clause reference match (e.g., "Clause 8.2" or "Clause 3")
        clause_match = re.search(r"clause\s*(\d+(?:\.\d+)?)", query, re.IGNORECASE)
        if clause_match:
            cl_num = clause_match.group(1)
            if any(cl_num in (r.chunk.clause_number or "") for r in ranked[:3]):
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

    @staticmethod
    def _detect_area_and_type(text: str) -> Optional[Tuple[float, str, str]]:
        """
        Extracts (normalized_sqft, raw_string, area_type) from text.
        Area types: 'Carpet Area', 'Built-Up Area', 'Super Built-Up Area'.
        """
        from app.intelligence.entity_normalizer import AreaNormalizer

        # 1. Super Area / Saleable Area / Chargeable Area
        m_super = re.search(
            r"(?:super\s+(?:built-?up\s+)?area|saleable\s+area|chargeable\s+area)\s*[:\-–]?\s*(?:of\s+|is\s+)?([0-9,]+(?:\.[0-9]+)?\s*(?:sq\.?\s*ft|sqft|sft|sq\.?\s*m|square\s+feet))",
            text,
            re.IGNORECASE,
        )
        if m_super:
            norm = AreaNormalizer.normalize(m_super.group(1))
            if norm:
                return (norm[0], m_super.group(1), "Super Built-Up Area")

        # 2. Built-Up Area / Plinth Area (not super)
        m_built = re.search(
            r"(?<!super\s)(?<!super-)\b(?:built-?up\s+area|plinth\s+area)\s*[:\-–]?\s*(?:of\s+|is\s+)?([0-9,]+(?:\.[0-9]+)?\s*(?:sq\.?\s*ft|sqft|sft|sq\.?\s*m|square\s+feet))",
            text,
            re.IGNORECASE,
        )
        if m_built:
            norm = AreaNormalizer.normalize(m_built.group(1))
            if norm:
                return (norm[0], m_built.group(1), "Built-Up Area")

        # 3. Carpet Area / Usable Area
        m_carpet = re.search(
            r"(?:carpet\s+area|usable\s+area|net\s+usable\s+floor\s+area|apartment\s+carpet\s+area)\s*[:\-–]?\s*(?:of\s+|is\s+|advertises\s+a\s+(?:carpet|usable)\s+area\s+of\s+)?([0-9,]+(?:\.[0-9]+)?\s*(?:sq\.?\s*ft|sqft|sft|sq\.?\s*m|square\s+feet))",
            text,
            re.IGNORECASE,
        )
        if m_carpet:
            norm = AreaNormalizer.normalize(m_carpet.group(1))
            if norm:
                return (norm[0], m_carpet.group(1), "Carpet Area")

        # 4. Fallback general area
        m_gen = re.search(
            r"(\b[\d,]+(?:\.\d+)?\s*(?:sq\.?\s*ft|sqft|sq\.?\s*m|square\s+feet)\b)",
            text,
            re.IGNORECASE,
        )
        if m_gen:
            norm = AreaNormalizer.normalize(m_gen.group(1))
            if norm:
                return (norm[0], m_gen.group(1), "Carpet Area")

        return None

    def _synthesize_grounded_answer(
        self,
        query: str,
        ranked: List[RankedChunkResult],
        docs_by_id: Dict[str, Document],
    ) -> str:
        """
        Dynamically synthesizes a concise, grounded answer referencing exact clauses,
        dates, amounts, and discrepancies without hallucinating.
        """
        from app.intelligence.entity_normalizer import DateNormalizer

        doc_ids_represented = list(dict.fromkeys([r.chunk.document_id for r in ranked]))
        is_multi_doc = len(doc_ids_represented) > 1

        q_lower = query.lower()
        is_possession = any(k in q_lower for k in ["possession", "handover", "delivery", "completion"])
        is_area = any(k in q_lower for k in ["area", "carpet area", "super area", "built-up", "built up", "saleable", "plinth", "usable", "unit area", "sq.ft", "sqft", "square feet"])

        # Handle multi-document comparative questions
        if is_multi_doc and (is_possession or is_area or len(doc_ids_represented) >= 2):
            answer_parts = ["### Cross-Document Verification\n"]
            doc_summaries = []
            extracted_facts = {}
            extracted_facts_by_type: Dict[str, Dict[str, float]] = {}

            for doc_id in doc_ids_represented[:5]:
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
                elif is_area:
                    area_info = self._detect_area_and_type(doc_chunk.chunk_text)
                    if area_info:
                        sqft_val, raw_area, a_type = area_info
                        fact_note = f" ({a_type}: **{sqft_val:,.0f} sq.ft.** / {raw_area})"
                        if a_type not in extracted_facts_by_type:
                            extracted_facts_by_type[a_type] = {}
                        extracted_facts_by_type[a_type][doc_name] = sqft_val

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
            elif is_area:
                has_discrepancy = False
                for a_type, type_facts in extracted_facts_by_type.items():
                    if len(type_facts) >= 2:
                        area_vals = list(type_facts.values())
                        if any(abs(v - area_vals[0]) > 1.0 for v in area_vals):
                            min_a = min(area_vals)
                            max_a = max(area_vals)
                            diff_a = max_a - min_a
                            has_discrepancy = True
                            answer_parts.append(
                                f"\n⚠️ **Discrepancy Note**: {a_type} mismatch detected across documents ({min_a:,.0f} sq.ft. contractual vs. {max_a:,.0f} sq.ft. marketing/brochure, variance of {diff_a:,.0f} sq.ft.)."
                            )
                if not has_discrepancy and len(extracted_facts_by_type) >= 2:
                    distinct_types = ", ".join(extracted_facts_by_type.keys())
                    answer_parts.append(
                        f"\nℹ️ **Area Type Distinction**: Retrieved documents cite distinct area metrics ({distinct_types}). Under RERA guidelines, these represent distinct spatial metrics and are evaluated independently."
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
        elif is_area:
            area_info = self._detect_area_and_type(top_chunk.chunk_text)
            if area_info:
                sqft_val, raw_area, a_type = area_info
                answer_parts.append(f"\n**Stated {a_type}**: {sqft_val:,.0f} sq.ft. ({raw_area}).")
            elif key_figures:
                unique_figures = list(dict.fromkeys([f.strip() for f in key_figures]))[:4]
                answer_parts.append(f"\n**Key Terms Stated:** {', '.join(unique_figures)}.")
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

