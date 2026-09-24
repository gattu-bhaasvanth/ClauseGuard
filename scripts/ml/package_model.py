"""
ClauseGuard Phase 9: Model Packaging & Optimization Service
Packages the selected Candidate C (Semantic Manifold Prototype Classifier)
into a production artifact with complete metadata, provenance, and calibration parameters.
Outputs: data/models/production_clause_model.json
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CANDIDATE_C_PATH = PROJECT_ROOT / "data" / "models" / "candidate_c_prototype.json"
BAKEOFF_PATH = PROJECT_ROOT / "data" / "models" / "bakeoff_comparison.json"
PRODUCTION_MODEL_PATH = PROJECT_ROOT / "data" / "models" / "production_clause_model.json"


def package_production_model():
    print("Packaging selected ML model into production artifact...")

    if not CANDIDATE_C_PATH.exists():
        raise FileNotFoundError(f"Selected candidate model not found at {CANDIDATE_C_PATH}")
    if not BAKEOFF_PATH.exists():
        raise FileNotFoundError(f"Bakeoff report not found at {BAKEOFF_PATH}")

    with open(CANDIDATE_C_PATH, "r", encoding="utf-8") as f:
        cand_data = json.load(f)
    with open(BAKEOFF_PATH, "r", encoding="utf-8") as f:
        bakeoff_data = json.load(f)

    production_payload = {
        "model_id": "cg-intel-semantic-prototype-v1.0",
        "model_name": "ClauseGuard Semantic Manifold Prototype Classifier",
        "architecture": "FastEmbed all-MiniLM-L6-v2 ONNX + Temperature-Scaled Centroid Manifold",
        "model_version": "v1.0.0",
        "dataset_version": "cg-statutory-corpus-v1.0",
        "packaged_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "embedding_model": cand_data["embedding_model"],
        "embedding_dim": cand_data["embedding_dim"],
        "temperature": cand_data["temperature"],
        "categories": cand_data["categories"],
        "centroids": cand_data["centroids"],
        "performance_metrics": {
            "test_accuracy": cand_data["accuracy"],
            "test_macro_f1": cand_data["macro_f1"],
            "baseline_macro_f1": bakeoff_data["baseline_macro_f1"],
            "improvement_delta_f1": bakeoff_data["improvement_delta_f1"],
            "latency_ms": cand_data["latency_ms"],
        },
        "provenance": {
            "sources": [
                "Central RERA General Rules 2016 (Form 'A')",
                "MahaRERA Model Form of Agreement for Sale",
                "Karnataka Real Estate Rules 2017 (Form 'N')",
                "Haryana RERA Standard Builder-Buyer Agreement",
                "Tamil Nadu Real Estate Rules 2017 (Form 'G')",
                "Delhi RERA Model Conveyance Regulations",
            ],
            "license": "Government Open Data / Public Domain",
            "pii_redacted": True,
        },
        "runtime_engine": "fastembed-onnx-cpu",
    }

    PRODUCTION_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PRODUCTION_MODEL_PATH, "w", encoding="utf-8") as f:
        json.dump(production_payload, f, indent=2)

    print(f"✅ Production model successfully packaged to: {PRODUCTION_MODEL_PATH}")
    print(f"   Model ID: {production_payload['model_id']}")
    print(f"   Accuracy: {production_payload['performance_metrics']['test_accuracy']*100:.2f}%")
    print(f"   Macro F1: {production_payload['performance_metrics']['test_macro_f1']:.4f}")
    print(f"   Delta F1: +{production_payload['performance_metrics']['improvement_delta_f1']:.4f}")


if __name__ == "__main__":
    package_production_model()
