"""
ClauseGuard Phase 9: Formal Baseline Evaluation of Existing Phase 4 Classifier
Evaluates the deterministic keyword/regex ClauseClassifier against the holdout test set.
Computes authoritative baseline metrics:
- Accuracy
- Macro & Weighted Precision, Recall, F1-scores
- Per-category confusion matrix and breakdown
- Inference latency profiling (mean, p95)
Outputs data/models/baseline_report.json.
"""

import json
import os
import sys
import time
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# Ensure project root and backend are on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.intelligence.classifier import ClauseClassifier
from app.intelligence.taxonomy import ClauseCategory

TEST_DATA_PATH = PROJECT_ROOT / "data" / "datasets" / "real_estate_clauses" / "test.jsonl"
REPORT_OUTPUT_PATH = PROJECT_ROOT / "data" / "models" / "baseline_report.json"

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


def evaluate_baseline() -> Dict[str, Any]:
    if not TEST_DATA_PATH.exists():
        raise FileNotFoundError(f"Holdout test data not found at {TEST_DATA_PATH}")

    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        test_samples = [json.loads(line) for line in f if line.strip()]

    print(f"Evaluating Phase 4 Baseline Classifier on {len(test_samples)} holdout test samples...")

    classifier = ClauseClassifier()

    y_true = []
    y_pred = []
    latencies = []
    misclassifications = []

    for sample in test_samples:
        t0 = time.perf_counter()
        result = classifier.classify_clause(title=sample["title"], text=sample["text"])
        dt = (time.perf_counter() - t0) * 1000.0  # ms
        latencies.append(dt)

        actual = sample["category"]
        pred = result.category.value if hasattr(result.category, "value") else str(result.category)

        y_true.append(actual)
        y_pred.append(pred)

        if actual != pred:
            misclassifications.append({
                "clause_id": sample["clause_id"],
                "title": sample["title"],
                "actual": actual,
                "predicted": pred,
                "confidence": result.confidence,
                "text_snippet": sample["text"][:120] + "...",
            })

    total = len(y_true)
    correct = sum(1 for a, p in zip(y_true, y_pred) if a == p)
    accuracy = correct / total if total > 0 else 0.0

    # Compute per-category precision, recall, f1
    cat_metrics = {}
    macro_p = 0.0
    macro_r = 0.0
    macro_f1 = 0.0
    weighted_f1 = 0.0

    # Build confusion matrix
    cm = {c: {c2: 0 for c2 in CATEGORIES} for c in CATEGORIES}
    for a, p in zip(y_true, y_pred):
        if a in cm and p in cm[a]:
            cm[a][p] += 1

    for cat in CATEGORIES:
        tp = sum(1 for a, p in zip(y_true, y_pred) if a == cat and p == cat)
        fp = sum(1 for a, p in zip(y_true, y_pred) if a != cat and p == cat)
        fn = sum(1 for a, p in zip(y_true, y_pred) if a == cat and p != cat)
        support = sum(1 for a in y_true if a == cat)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        cat_metrics[cat] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "support": support,
        }

        macro_p += prec
        macro_r += rec
        macro_f1 += f1
        weighted_f1 += f1 * support

    num_cats = len(CATEGORIES)
    macro_p = round(macro_p / num_cats, 4)
    macro_r = round(macro_r / num_cats, 4)
    macro_f1 = round(macro_f1 / num_cats, 4)
    weighted_f1 = round(weighted_f1 / total, 4) if total > 0 else 0.0

    avg_latency = round(sum(latencies) / len(latencies), 3)
    p95_latency = round(sorted(latencies)[int(0.95 * len(latencies))], 3)

    report = {
        "engine": "Phase 4 Deterministic ClauseClassifier (Keyword/Heuristic Baseline)",
        "evaluation_dataset": "ClauseGuard Real-Estate Holdout Test Split (test.jsonl)",
        "sample_count": total,
        "overall_accuracy": round(accuracy, 4),
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "average_latency_ms": avg_latency,
        "p95_latency_ms": p95_latency,
        "per_category_metrics": cat_metrics,
        "confusion_matrix": cm,
        "misclassifications_count": len(misclassifications),
        "sample_misclassifications": misclassifications[:10],
    }

    REPORT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 70)
    print("PHASE 4 BASELINE EVALUATION REPORT SUMMARY")
    print("=" * 70)
    print(f"Total Test Samples:    {total}")
    print(f"Overall Accuracy:      {accuracy * 100:.2f}%")
    print(f"Macro F1 Score:        {macro_f1:.4f}")
    print(f"Weighted F1 Score:     {weighted_f1:.4f}")
    print(f"Average Latency:       {avg_latency:.3f} ms / clause")
    print(f"P95 Latency:           {p95_latency:.3f} ms / clause")
    print(f"Misclassified Clauses: {len(misclassifications)} / {total}")
    print("=" * 70)
    print(f"Full baseline report saved to: {REPORT_OUTPUT_PATH}")

    return report


if __name__ == "__main__":
    evaluate_baseline()
