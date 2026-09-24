"""
ClauseGuard Phase 9: Local Clause Intelligence Engine
Executes local inference for real-estate clause classification using
the packaged Semantic Manifold Prototype model and FastEmbed ONNX embeddings.
Outputs calibrated probabilities, top alternative classifications, and audit metadata.
Zero external cloud or network dependencies.
"""

import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

# Default path for production model weights
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DEFAULT_MODEL_PATH = PROJECT_ROOT / "data" / "models" / "production_clause_model.json"
CACHE_DIR = PROJECT_ROOT / "data" / "embeddings" / "fastembed"


@dataclass
class MLPrediction:
    primary_category: str
    confidence: float
    top_alternatives: List[Dict[str, Any]]
    explanation_notes: str
    model_version: str
    dataset_version: str
    latency_ms: float


class LocalClauseIntelligenceEngine:
    _instance: Optional["LocalClauseIntelligenceEngine"] = None

    def __init__(self, model_path: Optional[Path] = None, cache_dir: Optional[Path] = None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.cache_dir = cache_dir or CACHE_DIR
        self.is_loaded = False
        self.categories: List[str] = []
        self.centroids: Optional[np.ndarray] = None
        self.temperature: float = 14.0
        self.model_version: str = "unknown"
        self.dataset_version: str = "unknown"
        self._embedder: Optional[TextEmbedding] = None
        self._load_model()

    def _load_model(self):
        if not self.model_path.exists():
            logger.warning(f"Production model artifact not found at {self.model_path}. ML inference will be unavailable.")
            return

        try:
            with open(self.model_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.categories = data["categories"]
            self.temperature = float(data.get("temperature", 14.0))
            self.model_version = data.get("model_version", "v1.0.0")
            self.dataset_version = data.get("dataset_version", "cg-corpus-v1.0")

            # Matrix shape: (num_categories, 384)
            centroid_list = [data["centroids"][cat] for cat in self.categories]
            self.centroids = np.asarray(centroid_list, dtype=np.float32)

            # Initialize local fastembed ONNX engine
            self._embedder = TextEmbedding(
                model_name=data.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
                cache_dir=str(self.cache_dir),
            )
            self.is_loaded = True
            logger.info(f"LocalClauseIntelligenceEngine successfully initialized: {data.get('model_id')}")
        except Exception as e:
            logger.error(f"Failed to load production clause model: {e}")
            self.is_loaded = False

    @classmethod
    def get_instance(cls) -> "LocalClauseIntelligenceEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def predict(self, title: str, text: str) -> Optional[MLPrediction]:
        if not self.is_loaded or self.centroids is None or self._embedder is None:
            return None

        t0 = time.perf_counter()
        query_text = f"{title}\n{text}".strip()
        if not query_text:
            return None

        # Extract 384-dim unit vector
        generator = self._embedder.embed([query_text])
        raw_vec = next(generator)
        vec = np.asarray(raw_vec, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm

        # Compute cosine similarities with centroids
        sims = np.dot(self.centroids, vec)  # (11,)
        scaled = sims * self.temperature
        exp_s = np.exp(scaled - np.max(scaled))
        probs = exp_s / np.sum(exp_s)

        top_indices = np.argsort(probs)[::-1]
        best_idx = top_indices[0]
        primary_cat = self.categories[best_idx]
        confidence = float(round(probs[best_idx], 4))

        # Top 2 alternatives
        top_alternatives = []
        for idx in top_indices[1:3]:
            top_alternatives.append({
                "category": self.categories[idx],
                "probability": float(round(probs[idx], 4)),
            })

        dt = (time.perf_counter() - t0) * 1000.0

        explanation = (
            f"Categorized under '{primary_cat}' with {confidence*100:.1f}% confidence "
            f"(cosine similarity: {sims[best_idx]:.3f})."
        )

        return MLPrediction(
            primary_category=primary_cat,
            confidence=confidence,
            top_alternatives=top_alternatives,
            explanation_notes=explanation,
            model_version=self.model_version,
            dataset_version=self.dataset_version,
            latency_ms=round(dt, 3),
        )


local_intelligence_engine = LocalClauseIntelligenceEngine.get_instance()
