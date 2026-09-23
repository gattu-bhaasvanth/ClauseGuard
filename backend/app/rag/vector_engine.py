import os
from pathlib import Path
from typing import List, Optional
import numpy as np
from fastembed import TextEmbedding
from app.config import settings

EMBEDDING_DIM = 384


class FastEmbedVectorEngine:
    """
    FastEmbed vector engine utilizing sentence-transformers/all-MiniLM-L6-v2 via ONNX runtime.
    Produces strictly 384-dimensional unit-normalized embeddings locally with zero external API calls.
    Uses local cache directory to prevent redundant downloads.
    """

    _instance: Optional["FastEmbedVectorEngine"] = None
    _embedder: Optional[TextEmbedding] = None

    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            # Resolve to project root data/embeddings/fastembed
            root_dir = Path(__file__).resolve().parent.parent.parent.parent
            resolved_cache = root_dir / "data" / "embeddings" / "fastembed"
            resolved_cache.mkdir(parents=True, exist_ok=True)
            self.cache_dir = str(resolved_cache)
        else:
            self.cache_dir = os.path.abspath(cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)

        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.dimension = EMBEDDING_DIM
        self._init_model()

    def _init_model(self) -> None:
        if FastEmbedVectorEngine._embedder is None:
            FastEmbedVectorEngine._embedder = TextEmbedding(
                model_name=self.model_name,
                cache_dir=self.cache_dir,
            )
        self.model = FastEmbedVectorEngine._embedder

    @classmethod
    def get_instance(cls, cache_dir: Optional[str] = None) -> "FastEmbedVectorEngine":
        if cls._instance is None:
            cls._instance = cls(cache_dir=cache_dir)
        return cls._instance

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string into a 384-dimensional normalized float list.
        """
        clean_text = text.strip() if text else ""
        if not clean_text:
            return [0.0] * self.dimension

        generator = self.model.embed([clean_text])
        raw_vec = next(generator)
        vec = np.asarray(raw_vec, dtype=np.float32)

        # Strictly enforce 384 dimensions
        if len(vec) != self.dimension:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {len(vec)}")

        # Ensure unit normalization for cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm

        return vec.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of text strings in batch.
        """
        if not texts:
            return []

        clean_texts = [t.strip() if t and t.strip() else "empty" for t in texts]
        generator = self.model.embed(clean_texts)

        results: List[List[float]] = []
        for raw_vec in generator:
            vec = np.asarray(raw_vec, dtype=np.float32)
            if len(vec) != self.dimension:
                raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {len(vec)}")
            norm = np.linalg.norm(vec)
            if norm > 1e-9:
                vec = vec / norm
            results.append(vec.tolist())

        return results

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """
        Compute cosine similarity between two 384-dimensional vectors.
        Returns a float in range [-1.0, 1.0], typically [0.0, 1.0] for sentence embeddings.
        """
        if not vec_a or not vec_b:
            return 0.0

        a = np.asarray(vec_a, dtype=np.float32)
        b = np.asarray(vec_b, dtype=np.float32)

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a < 1e-9 or norm_b < 1e-9:
            return 0.0

        dot = np.dot(a, b)
        similarity = float(dot / (norm_a * norm_b))
        return max(-1.0, min(1.0, similarity))

    @staticmethod
    def batch_cosine_similarity(query_vec: List[float], candidate_vecs: List[List[float]]) -> List[float]:
        """
        Compute cosine similarity between a single 384-d query vector and multiple candidate vectors.
        """
        if not candidate_vecs or not query_vec:
            return []

        q = np.asarray(query_vec, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm < 1e-9:
            return [0.0] * len(candidate_vecs)
        q_unit = q / q_norm

        candidates = np.asarray(candidate_vecs, dtype=np.float32)
        norms = np.linalg.norm(candidates, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms < 1e-9, 1.0, norms)
        cand_unit = candidates / norms

        sims = np.dot(cand_unit, q_unit)
        return [float(max(-1.0, min(1.0, s))) for s in sims]
