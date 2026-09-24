"""
ClauseGuard Phase 9: Model Candidate C — Semantic Manifold Prototype Classifier
Computes unit-normalized class centroids in FastEmbed 384-dim semantic space.
Performs temperature-scaled cosine similarity classification with calibrated softmax probabilities.
"""

import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
from fastembed import TextEmbedding

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "embeddings" / "fastembed"
TRAIN_PATH = PROJECT_ROOT / "data" / "datasets" / "real_estate_clauses" / "train.jsonl"
VAL_PATH = PROJECT_ROOT / "data" / "datasets" / "real_estate_clauses" / "val.jsonl"
TEST_PATH = PROJECT_ROOT / "data" / "datasets" / "real_estate_clauses" / "test.jsonl"
MODEL_OUT_PATH = PROJECT_ROOT / "data" / "models" / "candidate_c_prototype.json"

CATEGORIES = [
    "Possession & Handover",
    "Payment Milestones & Delay Interest",
    "Carpet Area & Measurement Adjustments",
    "Cancellation & Earnest Money Forfeiture",
    "Alteration of Layout & Specifications",
    "Defects Liability & Structural Rectification",
    "Force Majeure & Uncontrollable Delays",
    "Dispute Resolution & Jurisdiction",
    "RERA & Statutory Approvals",
    "Maintenance & Additional Levies",
    "General Terms & Covenants",
]
CAT2IDX = {c: i for i, c in enumerate(CATEGORIES)}


def load_dataset(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def extract_embeddings(embedder: TextEmbedding, texts: List[str]) -> np.ndarray:
    generator = embedder.embed(texts)
    vecs = [v for v in generator]
    arr = np.asarray(vecs, dtype=np.float32)
    # L2 normalize
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return arr / norms


class SemanticPrototypeClassifier:
    def __init__(self, categories: List[str], temperature: float = 12.0):
        self.categories = categories
        self.temperature = temperature
        self.centroids: Dict[str, np.ndarray] = {}

    def fit(self, X: np.ndarray, y: List[str]):
        by_class = {c: [] for c in self.categories}
        for vec, label in zip(X, y):
            by_class[label].append(vec)

        for cat in self.categories:
            if by_class[cat]:
                mean_vec = np.mean(by_class[cat], axis=0)
                norm = np.linalg.norm(mean_vec)
                self.centroids[cat] = mean_vec / (norm if norm > 0 else 1.0)
            else:
                self.centroids[cat] = np.zeros(X.shape[1], dtype=np.float32)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        centroid_matrix = np.array([self.centroids[c] for c in self.categories])  # (11, 384)
        sims = np.dot(X, centroid_matrix.T)  # (N, 11)
        scaled = sims * self.temperature
        exp_s = np.exp(scaled - np.max(scaled, axis=1, keepdims=True))
        return exp_s / np.sum(exp_s, axis=1, keepdims=True)


def train_and_evaluate():
    print("Initializing local FastEmbed TextEmbedding engine...")
    embedder = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", cache_dir=str(CACHE_DIR))

    train_data = load_dataset(TRAIN_PATH)
    val_data = load_dataset(VAL_PATH)
    test_data = load_dataset(TEST_PATH)

    # Combine train + val for prototype centroids
    train_val_data = train_data + val_data
    train_val_texts = [f"{d['title']}\n{d['text']}" for d in train_val_data]
    train_val_labels = [d["category"] for d in train_val_data]

    test_texts = [f"{d['title']}\n{d['text']}" for d in test_data]
    test_labels = [d["category"] for d in test_data]
    y_test = np.array([CAT2IDX[c] for c in test_labels])

    print("Computing class centroid prototypes in 384-dim semantic space...")
    X_train_val = extract_embeddings(embedder, train_val_texts)
    X_test = extract_embeddings(embedder, test_texts)

    classifier = SemanticPrototypeClassifier(categories=CATEGORIES, temperature=14.0)
    classifier.fit(X_train_val, train_val_labels)

    # Evaluate on Holdout Test Set
    t0 = time.perf_counter()
    probs = classifier.predict_proba(X_test)
    dt = (time.perf_counter() - t0) * 1000.0 / len(test_data)
    y_pred = np.argmax(probs, axis=1)

    acc = np.mean(y_pred == y_test)

    f1_list = []
    for c_idx in range(len(CATEGORIES)):
        tp = np.sum((y_pred == c_idx) & (y_test == c_idx))
        fp = np.sum((y_pred == c_idx) & (y_test != c_idx))
        fn = np.sum((y_pred != c_idx) & (y_test == c_idx))
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        f1_list.append(f1)
    macro_f1 = float(np.mean(f1_list))

    print("\n" + "=" * 70)
    print("CANDIDATE C (Semantic Prototype Centroid) TEST RESULTS")
    print("=" * 70)
    print(f"Overall Accuracy:  {acc * 100:.2f}%")
    print(f"Macro F1 Score:    {macro_f1:.4f}")
    print(f"Latency:           {dt:.3f} ms / clause")
    print("=" * 70)

    # Serialize candidate model
    MODEL_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    serialized = {
        "model_type": "Semantic Manifold Prototype Classifier",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_dim": 384,
        "temperature": 14.0,
        "accuracy": float(acc),
        "macro_f1": float(macro_f1),
        "latency_ms": float(dt),
        "centroids": {cat: classifier.centroids[cat].tolist() for cat in CATEGORIES},
        "categories": CATEGORIES,
    }
    with open(MODEL_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(serialized, f)
    print(f"Model saved to: {MODEL_OUT_PATH}")


if __name__ == "__main__":
    train_and_evaluate()
