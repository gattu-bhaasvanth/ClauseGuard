import math
import re
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from app.models.chunk import DocumentChunk
from app.rag.vector_engine import FastEmbedVectorEngine


@dataclass
class RankedChunkResult:
    chunk: DocumentChunk
    rrf_score: float
    dense_score: float
    lexical_score: float
    combined_confidence: float


class HybridRetriever:
    """
    Hybrid retriever combining 384-dimensional dense cosine semantic similarity
    with lexical keyword / BM25-style scoring, fused using Reciprocal Rank Fusion (RRF).
    """

    RRF_K = 60  # Standard RRF constant

    def __init__(self, vector_engine: Optional[FastEmbedVectorEngine] = None):
        self.vector_engine = vector_engine or FastEmbedVectorEngine.get_instance()

    def retrieve(
        self,
        query: str,
        chunks: List[DocumentChunk],
        top_k: int = 5,
    ) -> List[RankedChunkResult]:
        """
        Executes hybrid retrieval over a collection of DocumentChunk objects.
        """
        if not chunks or not query.strip():
            return []

        # 1. Lexical retrieval pass
        lexical_scores = self._score_lexical(query, chunks)
        # Sort indices by descending lexical score
        lexical_ranked_indices = sorted(
            range(len(chunks)),
            key=lambda idx: lexical_scores[idx],
            reverse=True,
        )

        # 2. Dense semantic retrieval pass (384-d cosine similarity)
        query_vec = self.vector_engine.embed_text(query)
        dense_scores = self._score_dense(query_vec, chunks)
        # Sort indices by descending dense score
        dense_ranked_indices = sorted(
            range(len(chunks)),
            key=lambda idx: dense_scores[idx],
            reverse=True,
        )

        # 3. Reciprocal Rank Fusion (RRF)
        # Rank is 1-based index in the sorted list
        lexical_rank_map: Dict[int, int] = {idx: rank + 1 for rank, idx in enumerate(lexical_ranked_indices)}
        dense_rank_map: Dict[int, int] = {idx: rank + 1 for rank, idx in enumerate(dense_ranked_indices)}

        rrf_scores: Dict[int, float] = {}
        for idx in range(len(chunks)):
            r_dense = dense_rank_map[idx]
            r_lex = lexical_rank_map[idx]
            rrf = (1.0 / (self.RRF_K + r_dense)) + (1.0 / (self.RRF_K + r_lex))
            rrf_scores[idx] = rrf

        # Sort all chunks by RRF score descending
        fused_sorted_indices = sorted(
            range(len(chunks)),
            key=lambda idx: rrf_scores[idx],
            reverse=True,
        )

        # Build results for top_k
        max_possible_rrf = (1.0 / (self.RRF_K + 1)) + (1.0 / (self.RRF_K + 1))  # ~0.03278
        results: List[RankedChunkResult] = []

        for idx in fused_sorted_indices[:top_k]:
            chunk = chunks[idx]
            rrf = rrf_scores[idx]
            dense_s = dense_scores[idx]
            lex_s = lexical_scores[idx]

            # Normalized combined confidence (0.0 to 1.0)
            norm_rrf = min(1.0, rrf / max_possible_rrf)
            if lex_s > 0:
                combined_conf = float(max(dense_s, 0.4 * max(0.0, dense_s) + 0.3 * norm_rrf + 0.3 * min(1.0, lex_s / 5.0)))
            else:
                # No lexical match: confidence is strictly dictated by dense cosine similarity
                combined_conf = float(max(0.0, dense_s))

            results.append(
                RankedChunkResult(
                    chunk=chunk,
                    rrf_score=rrf,
                    dense_score=dense_s,
                    lexical_score=lex_s,
                    combined_confidence=combined_conf,
                )
            )

        return results

    def _score_dense(self, query_vec: List[float], chunks: List[DocumentChunk]) -> List[float]:
        """
        Compute cosine similarities between query vector and all chunk embeddings.
        Falls back to 0.0 if embedding is missing.
        """
        scores: List[float] = []
        for chunk in chunks:
            if chunk.embedding and len(chunk.embedding) == 384:
                sim = self.vector_engine.cosine_similarity(query_vec, chunk.embedding)
                scores.append(max(0.0, sim))
            else:
                # If chunk embedding not computed yet, compute on the fly
                vec = self.vector_engine.embed_text(chunk.chunk_text)
                sim = self.vector_engine.cosine_similarity(query_vec, vec)
                scores.append(max(0.0, sim))
        return scores

    def _score_lexical(self, query: str, chunks: List[DocumentChunk]) -> List[float]:
        """
        Lexical scoring using BM25-style term frequency with real-estate keyword boosting.
        """
        query_terms = self._tokenize(query)
        if not query_terms:
            return [0.0] * len(chunks)

        chunk_token_lists = [self._tokenize(c.chunk_text) for c in chunks]
        doc_count = len(chunks)

        # Calculate document frequencies
        df: Dict[str, int] = {}
        for terms in chunk_token_lists:
            unique_terms = set(terms)
            for t in unique_terms:
                df[t] = df.get(t, 0) + 1

        scores: List[float] = []
        for i, chunk in enumerate(chunks):
            terms = chunk_token_lists[i]
            if not terms:
                scores.append(0.0)
                continue

            term_freqs: Dict[str, int] = {}
            for t in terms:
                term_freqs[t] = term_freqs.get(t, 0) + 1

            chunk_len = len(terms)
            score = 0.0

            # Boost if query matches clause number or clause title directly
            clause_num = (chunk.clause_number or "").lower().strip()
            query_lower = query.lower()
            query_terms_set = set(query_terms)

            if clause_num and (clause_num in query_lower):
                score += 5.0
            title_terms = set(self._tokenize(chunk.clause_title or ""))
            if title_terms.intersection(query_terms_set):
                score += 2.0

            for q_term in query_terms:
                tf = term_freqs.get(q_term, 0)
                if tf > 0:
                    doc_freq = df.get(q_term, 1)
                    # Standard BM25 IDF
                    idf = math.log((doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
                    tf_norm = (tf * 2.2) / (tf + 1.2 * (1.0 - 0.75 + 0.75 * (chunk_len / 100.0)))
                    score += idf * tf_norm

            scores.append(float(score))

        return scores

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        Tokenize text preserving legal identifiers like '8.2', '18%', 'rera', etc.
        """
        clean = text.lower()
        # Find alphanumeric words, including decimals like 8.2 and percentages like 18%
        tokens = re.findall(r"\b\w+(?:\.\w+)*%?\b", clean)
        # Remove trivial single-character and conversational stopwords
        stopwords = {
            "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or",
            "is", "are", "be", "was", "were", "been", "what", "which", "where",
            "when", "how", "why", "can", "could", "would", "should", "i", "you",
            "your", "my", "we", "our", "it", "its", "do", "does", "did", "have",
            "has", "had", "this", "that", "these", "those"
        }
        return [t for t in tokens if t not in stopwords and len(t) > 1]
