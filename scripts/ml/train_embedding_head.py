"""
ClauseGuard Phase 9: Model Candidate B — Dense FastEmbed + Classification Head
Uses local FastEmbed (all-MiniLM-L6-v2 ONNX) to extract 384-dim semantic embeddings.
Trains a Softmax Classification Head on embeddings with L2 regularization.
"""

import json
import os
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
MODEL_OUT_PATH = PROJECT_ROOT / "data" / "models" / "candidate_b_embedding_head.json"

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
    return np.asarray(vecs, dtype=np.float32)


class DenseSoftmaxHead:
    def __init__(self, dim: int = 384, num_classes: int = 11, lr: float = 0.05, l2: float = 0.001):
        self.W = np.random.randn(dim, num_classes).astype(np.float32) * 0.01
        self.b = np.zeros(num_classes, dtype=np.float32)
        self.lr = lr
        self.l2 = l2

    def softmax(self, z: np.ndarray) -> np.ndarray:
        exp_z = np.exp(z - np.max(z, axis=-1, keepdims=True))
        return exp_z / np.sum(exp_z, axis=-1, keepdims=True)

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray, epochs: int = 300):
        n_samples, n_classes = X_train.shape[0], self.W.shape[1]
        Y = np.zeros((n_samples, n_classes), dtype=np.float32)
        Y[np.arange(n_samples), y_train] = 1.0

        best_val_acc = 0.0
        best_W = self.W.copy()
        best_b = self.b.copy()

        for epoch in range(epochs):
            logits = np.dot(X_train, self.W) + self.b
            probs = self.softmax(logits)

            grad_W = np.dot(X_train.T, (probs - Y)) / n_samples + self.l2 * self.W
            grad_b = np.mean(probs - Y, axis=0)

            self.W -= self.lr * grad_W
            self.b -= self.lr * grad_b

            if (epoch + 1) % 20 == 0:
                val_probs = self.predict_proba(X_val)
                val_pred = np.argmax(val_probs, axis=1)
                val_acc = np.mean(val_pred == y_val)
                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    best_W = self.W.copy()
                    best_b = self.b.copy()

        self.W = best_W
        self.b = best_b

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        logits = np.dot(X, self.W) + self.b
        return self.softmax(logits)


def train_and_evaluate():
    print("Initializing local FastEmbed TextEmbedding engine...")
    embedder = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", cache_dir=str(CACHE_DIR))

    train_data = load_dataset(TRAIN_PATH)
    val_data = load_dataset(VAL_PATH)
    test_data = load_dataset(TEST_PATH)

    print("Extracting dense 384-dimensional embeddings...")
    train_texts = [f"{d['title']}\n{d['text']}" for d in train_data]
    val_texts = [f"{d['title']}\n{d['text']}" for d in val_data]
    test_texts = [f"{d['title']}\n{d['text']}" for d in test_data]

    X_train = extract_embeddings(embedder, train_texts)
    y_train = np.array([CAT2IDX[d["category"]] for d in train_data])

    X_val = extract_embeddings(embedder, val_texts)
    y_val = np.array([CAT2IDX[d["category"]] for d in val_data])

    X_test = extract_embeddings(embedder, test_texts)
    y_test = np.array([CAT2IDX[d["category"]] for d in test_data])

    print("Training Dense Softmax Classification Head...")
    head = DenseSoftmaxHead(dim=384, num_classes=len(CATEGORIES), lr=0.1, l2=0.0001)
    head.fit(X_train, y_train, X_val, y_val, epochs=500)

    # Evaluate on Holdout Test Set
    t0 = time.perf_counter()
    probs = head.predict_proba(X_test)
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
    print("CANDIDATE B (FastEmbed + Dense Head) TEST RESULTS")
    print("=" * 70)
    print(f"Overall Accuracy:  {acc * 100:.2f}%")
    print(f"Macro F1 Score:    {macro_f1:.4f}")
    print(f"Latency:           {dt:.3f} ms / clause")
    print("=" * 70)

    # Serialize candidate model
    MODEL_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    serialized = {
        "model_type": "FastEmbed + Dense Softmax Head",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_dim": 384,
        "accuracy": float(acc),
        "macro_f1": float(macro_f1),
        "latency_ms": float(dt),
        "W": head.W.tolist(),
        "b": head.b.tolist(),
        "categories": CATEGORIES,
    }
    with open(MODEL_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(serialized, f)
    print(f"Model saved to: {MODEL_OUT_PATH}")


if __name__ == "__main__":
    train_and_evaluate()
