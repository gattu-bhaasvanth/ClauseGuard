"""
ClauseGuard Phase 9: Model Candidate A — TF-IDF + Softmax Classifier
Implemented in pure Python & NumPy with zero extra dependencies.
Trains a multinomial logistic regression classifier on n-gram TF-IDF representations.
"""

import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TRAIN_PATH = PROJECT_ROOT / "data" / "datasets" / "real_estate_clauses" / "train.jsonl"
VAL_PATH = PROJECT_ROOT / "data" / "datasets" / "real_estate_clauses" / "val.jsonl"
TEST_PATH = PROJECT_ROOT / "data" / "datasets" / "real_estate_clauses" / "test.jsonl"
MODEL_OUT_PATH = PROJECT_ROOT / "data" / "models" / "candidate_a_linear.json"

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


class NumpyTfidfVectorizer:
    def __init__(self, max_features: int = 500, min_df: int = 2, ngram_range=(1, 2)):
        self.max_features = max_features
        self.min_df = min_df
        self.ngram_range = ngram_range
        self.vocab = {}
        self.idf = {}

    def _tokenize(self, text: str) -> List[str]:
        words = [w.strip(".,;:()[]\"'-").lower() for w in text.split()]
        words = [w for w in words if len(w) > 1]
        tokens = []
        if 1 in self.ngram_range:
            tokens.extend(words)
        if 2 in self.ngram_range:
            tokens.extend([f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)])
        return tokens

    def fit(self, texts: List[str]):
        doc_counts = Counter()
        n_docs = len(texts)
        for t in texts:
            unique_tokens = set(self._tokenize(t))
            for tok in unique_tokens:
                doc_counts[tok] += 1

        filtered = [tok for tok, cnt in doc_counts.items() if cnt >= self.min_df]
        filtered.sort(key=lambda tok: doc_counts[tok], reverse=True)
        top_tokens = filtered[:self.max_features]

        self.vocab = {tok: idx for idx, tok in enumerate(top_tokens)}
        self.idf = {
            tok: math.log((1 + n_docs) / (1 + doc_counts[tok])) + 1.0
            for tok in self.vocab
        }

    def transform(self, texts: List[str]) -> np.ndarray:
        X = np.zeros((len(texts), len(self.vocab)), dtype=np.float32)
        for i, t in enumerate(texts):
            tokens = self._tokenize(t)
            counts = Counter(tokens)
            for tok, cnt in counts.items():
                if tok in self.vocab:
                    col = self.vocab[tok]
                    tf = cnt / len(tokens) if len(tokens) > 0 else 0
                    X[i, col] = tf * self.idf[tok]
            # L2 normalize
            norm = np.linalg.norm(X[i])
            if norm > 0:
                X[i] /= norm
        return X


class SoftmaxClassifier:
    def __init__(self, num_features: int, num_classes: int, lr: float = 0.1, l2: float = 0.001):
        self.W = np.zeros((num_features, num_classes), dtype=np.float32)
        self.b = np.zeros(num_classes, dtype=np.float32)
        self.lr = lr
        self.l2 = l2

    def softmax(self, z: np.ndarray) -> np.ndarray:
        exp_z = np.exp(z - np.max(z, axis=-1, keepdims=True))
        return exp_z / np.sum(exp_z, axis=-1, keepdims=True)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 150):
        n_samples, n_classes = X.shape[0], self.W.shape[1]
        Y = np.zeros((n_samples, n_classes), dtype=np.float32)
        Y[np.arange(n_samples), y] = 1.0

        for epoch in range(epochs):
            logits = np.dot(X, self.W) + self.b
            probs = self.softmax(logits)

            grad_W = np.dot(X.T, (probs - Y)) / n_samples + self.l2 * self.W
            grad_b = np.mean(probs - Y, axis=0)

            self.W -= self.lr * grad_W
            self.b -= self.lr * grad_b

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        logits = np.dot(X, self.W) + self.b
        return self.softmax(logits)


def train_and_evaluate():
    print("Training Candidate A: TF-IDF + Multinomial Logistic Classifier...")

    with open(TRAIN_PATH, "r", encoding="utf-8") as f:
        train_data = [json.loads(line) for line in f if line.strip()]
    with open(VAL_PATH, "r", encoding="utf-8") as f:
        val_data = [json.loads(line) for line in f if line.strip()]
    with open(TEST_PATH, "r", encoding="utf-8") as f:
        test_data = [json.loads(line) for line in f if line.strip()]

    vectorizer = NumpyTfidfVectorizer(max_features=400, min_df=2)
    train_texts = [f"{d['title']} {d['text']}" for d in train_data]
    vectorizer.fit(train_texts)

    X_train = vectorizer.transform(train_texts)
    y_train = np.array([CAT2IDX[d["category"]] for d in train_data])

    val_texts = [f"{d['title']} {d['text']}" for d in val_data]
    X_val = vectorizer.transform(val_texts)
    y_val = np.array([CAT2IDX[d["category"]] for d in val_data])

    test_texts = [f"{d['title']} {d['text']}" for d in test_data]
    X_test = vectorizer.transform(test_texts)
    y_test = np.array([CAT2IDX[d["category"]] for d in test_data])

    model = SoftmaxClassifier(num_features=X_train.shape[1], num_classes=len(CATEGORIES), lr=0.5, l2=0.0005)
    model.fit(X_train, y_train, epochs=250)

    # Evaluate on Test
    t0 = time.perf_counter()
    probs = model.predict_proba(X_test)
    dt = (time.perf_counter() - t0) * 1000.0 / len(test_data)
    y_pred = np.argmax(probs, axis=1)

    acc = np.mean(y_pred == y_test)

    # Calculate Macro F1
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

    print(f"Candidate A (TF-IDF + Linear): Accuracy = {acc*100:.2f}%, Macro F1 = {macro_f1:.4f}, Latency = {dt:.3f} ms/clause")

    # Serialize candidate model
    MODEL_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    serialized = {
        "model_type": "TF-IDF + Softmax Classifier",
        "accuracy": float(acc),
        "macro_f1": float(macro_f1),
        "latency_ms": float(dt),
        "vocab": vectorizer.vocab,
        "idf": vectorizer.idf,
        "W": model.W.tolist(),
        "b": model.b.tolist(),
        "categories": CATEGORIES,
    }
    with open(MODEL_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(serialized, f)


if __name__ == "__main__":
    train_and_evaluate()
