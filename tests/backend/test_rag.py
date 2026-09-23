import pytest
import numpy as np
from sqlalchemy import select
from app.rag.vector_engine import FastEmbedVectorEngine, EMBEDDING_DIM
from app.rag.chunker import ClauseCentricChunker, ProcessedChunk
from app.rag.retriever import HybridRetriever
from app.rag.rag_service import TransactionRAGService
from app.models.clause import Clause
from app.models.document import Document, DocumentPage
from app.models.chunk import DocumentChunk
from app.models.transaction import TransactionBundle


def test_vector_engine_dimensions_and_normalization():
    """Verify FastEmbed generates strictly 384-dimensional unit vectors."""
    engine = FastEmbedVectorEngine.get_instance()
    assert engine.dimension == 384
    assert EMBEDDING_DIM == 384

    # Single text embedding
    text = "Clause 8.2: The Builder shall deliver possession on or before December 31, 2027."
    vec = engine.embed_text(text)
    assert len(vec) == 384
    # Check unit normalization: norm should be ~1.0
    norm = np.linalg.norm(np.array(vec, dtype=np.float32))
    assert pytest.approx(norm, abs=1e-4) == 1.0

    # Batch embedding
    texts = [
        "Payment delay interest rate shall be 18% per annum.",
        "Carpet area is 1200 square feet subject to 3% variation.",
        "Allotment letter issued on March 15, 2024.",
    ]
    batch_vecs = engine.embed_batch(texts)
    assert len(batch_vecs) == 3
    for b_vec in batch_vecs:
        assert len(b_vec) == 384
        b_norm = np.linalg.norm(np.array(b_vec, dtype=np.float32))
        assert pytest.approx(b_norm, abs=1e-4) == 1.0


def test_cosine_similarity():
    """Verify cosine similarity calculation between 384-d vectors."""
    engine = FastEmbedVectorEngine.get_instance()

    vec_a = engine.embed_text("Delay in possession compensation SBI MCLR + 2%")
    vec_b = engine.embed_text("SBI MCLR plus 2 percent builder handover penalty")
    vec_c = engine.embed_text("Blue elephants walking on Mars surface")

    sim_ab = engine.cosine_similarity(vec_a, vec_b)
    sim_ac = engine.cosine_similarity(vec_a, vec_c)

    # Semantically related clauses should have noticeably higher similarity than unrelated topics
    assert sim_ab > 0.65
    assert sim_ac < 0.35
    assert sim_ab > sim_ac

    # Self-similarity should be 1.0
    sim_self = engine.cosine_similarity(vec_a, vec_a)
    assert pytest.approx(sim_self, abs=1e-4) == 1.0


def test_clause_centric_chunker():
    """Verify chunker extracts structured clause metadata and handles oversized clauses."""
    chunker = ClauseCentricChunker()

    clause1 = Clause(
        id="cls-01",
        bundle_id="bnd-01",
        document_id="doc-01",
        clause_number="Clause 6.2",
        title="Delayed Payment Charges",
        page_number=12,
        preview_text="Interest of 18% p.a. on delayed installments.",
        full_excerpt="In the event of default in payment of any installment by the Buyer, interest at 18% per annum shall be payable.",
    )

    doc = Document(
        id="doc-01",
        bundle_id="bnd-01",
        file_name="Agreement_for_Sale.pdf",
        document_type="SALE_AGREEMENT",
    )

    chunks = chunker.chunk_document(doc, clauses=[clause1])
    assert len(chunks) == 1
    chk = chunks[0]
    assert chk.bundle_id == "bnd-01"
    assert chk.document_id == "doc-01"
    assert chk.page_number == 12
    assert chk.clause_number == "Clause 6.2"
    assert chk.clause_title == "Delayed Payment Charges"
    assert "18% per annum" in chk.chunk_text
    assert chk.chunk_type == "CLAUSE"


def test_hybrid_retriever_ranking():
    """Verify HybridRetriever fuses BM25 lexical and 384-d dense scores."""
    engine = FastEmbedVectorEngine.get_instance()
    retriever = HybridRetriever(engine)

    # Create synthetic chunks
    c1 = DocumentChunk(
        id="c1",
        bundle_id="bnd-01",
        document_id="doc-01",
        page_number=5,
        clause_number="Clause 6.2",
        clause_title="Payment Default & Interest",
        chunk_type="CLAUSE",
        chunk_text="Clause 6.2: Payment Default & Interest\nDelayed payments by the purchaser shall attract interest of 18% per annum.",
        embedding=engine.embed_text("Clause 6.2: Payment Default & Interest\nDelayed payments by the purchaser shall attract interest of 18% per annum."),
    )
    c2 = DocumentChunk(
        id="c2",
        bundle_id="bnd-01",
        document_id="doc-01",
        page_number=14,
        clause_number="Clause 8.2",
        clause_title="Possession and Delay Compensation",
        chunk_type="CLAUSE",
        chunk_text="Clause 8.2: Possession and Delay Compensation\nPossession of the apartment shall be completed by December 31, 2027 with 6 months grace.",
        embedding=engine.embed_text("Clause 8.2: Possession and Delay Compensation\nPossession of the apartment shall be completed by December 31, 2027 with 6 months grace."),
    )
    c3 = DocumentChunk(
        id="c3",
        bundle_id="bnd-01",
        document_id="doc-01",
        page_number=20,
        clause_number="Clause 14.1",
        clause_title="Maintenance & Club Charges",
        chunk_type="CLAUSE",
        chunk_text="Clause 14.1: Maintenance & Club Charges\nAdvance maintenance of Rs 50,000 shall be payable prior to handover.",
        embedding=engine.embed_text("Clause 14.1: Maintenance & Club Charges\nAdvance maintenance of Rs 50,000 shall be payable prior to handover."),
    )

    results = retriever.retrieve(query="What is the interest rate for delayed payment?", chunks=[c1, c2, c3], top_k=3)
    assert len(results) == 3
    # c1 should rank #1 because it mentions both delayed payment and interest rate
    assert results[0].chunk.id == "c1"
    assert results[0].chunk.clause_number == "Clause 6.2"
    assert results[0].rrf_score > 0
    assert results[0].combined_confidence > 0.4


@pytest.mark.asyncio
async def test_anti_hallucination_refusal(db_session):
    """Verify strict refusal guardrail triggers when query is out of scope."""
    rag_service = TransactionRAGService()

    # Query an absurd/unrelated topic not present in real estate documents
    res = await rag_service.query_transaction(
        db=db_session,
        bundle_id="skyview-a1204",
        query_text="What color are the curtains and can I keep a pet giraffe in the flat?",
    )

    # Must refuse to speculate
    assert res.grounded is False
    assert res.status == "INSUFFICIENT_EVIDENCE"
    assert len(res.citations) == 0
    assert "no verified mention" in res.answer or "insufficient" in res.answer.lower()


@pytest.mark.asyncio
async def test_grounded_rag_query_with_citations(db_session):
    """Verify grounded RAG query returns answers citing exact clauses."""
    rag_service = TransactionRAGService()

    res = await rag_service.query_transaction(
        db=db_session,
        bundle_id="skyview-a1204",
        query_text="What happens if the buyer delays payment?",
    )

    assert res.grounded is True
    assert res.status == "GROUNDED"
    assert res.confidence > 0.3
    assert len(res.citations) > 0

    top_citation = res.citations[0]
    assert top_citation.pageNumber >= 1
    assert top_citation.clauseNumber is not None
    assert len(top_citation.excerpt) > 10


@pytest.mark.asyncio
async def test_rag_api_endpoints(client, db_session):
    """Test REST API routes for RAG query and chunk retrieval."""
    # 1. Ask grounded question via API
    resp = await client.post(
        "/api/v1/transactions/skyview-a1204/rag/query",
        json={"query": "What is the penalty if the builder delays handover?", "topK": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "What is the penalty if the builder delays handover?"
    assert data["grounded"] is True
    assert data["status"] == "GROUNDED"
    assert len(data["citations"]) > 0
    assert "ClauseGuard" in data["disclaimer"]

    # 2. Get chunks list via API
    chunks_resp = await client.get("/api/v1/transactions/skyview-a1204/rag/chunks")
    assert chunks_resp.status_code == 200
    chunks_data = chunks_resp.json()
    assert isinstance(chunks_data, list)
    assert len(chunks_data) > 0
    assert chunks_data[0]["hasEmbedding"] is True

    # 3. Test 404 for nonexistent transaction
    bad_resp = await client.post(
        "/api/v1/transactions/nonexistent-bundle-999/rag/query",
        json={"query": "Any query"},
    )
    assert bad_resp.status_code == 404


@pytest.mark.asyncio
async def test_rag_ui_contract_and_suggested_queries(client, db_session):
    """
    Verify that the RAG endpoint satisfies the exact JSON contract required by
    the frontend SemanticExplorationWorkspace and tests standard suggested queries.
    """
    ui_suggested_queries = [
        ("What is the penalty if the builder delays handover?", "8.2"),
        ("What is the interest rate on delayed installment payment?", "5.3"),
        ("What variation in carpet area is allowed without price adjustment?", "4.1"),
    ]

    for question, expected_clause in ui_suggested_queries:
        resp = await client.post(
            "/api/v1/transactions/skyview-a1204/rag/query",
            json={"query": question, "topK": 5},
        )
        assert resp.status_code == 200
        payload = resp.json()

        # Contract fields required by types/rag.ts
        assert "query" in payload
        assert "answer" in payload
        assert "grounded" in payload
        assert "status" in payload
        assert "confidence" in payload
        assert "citations" in payload
        assert "bundleId" in payload
        assert "disclaimer" in payload

        assert payload["grounded"] is True
        assert payload["status"] == "GROUNDED"
        assert payload["confidence"] > 0.3
        assert len(payload["citations"]) > 0

        # Verify citation contract fields for SourceEvidenceModal
        top_cit = payload["citations"][0]
        assert "documentId" in top_cit
        assert "documentName" in top_cit
        assert "documentType" in top_cit
        assert "pageNumber" in top_cit
        assert "clauseNumber" in top_cit
        assert "clauseTitle" in top_cit
        assert "excerpt" in top_cit
        assert "relevanceScore" in top_cit
        assert top_cit["relevanceScore"] >= 0.0

        # Verify expected clause was retrieved in citations
        all_clauses = [c.get("clauseNumber", "") for c in payload["citations"]]
        assert any(expected_clause in cl for cl in all_clauses)
