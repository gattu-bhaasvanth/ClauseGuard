"""
Unit tests for ClauseGuard Phase 9: Dataset Integrity, Provenance & Anti-Contamination.
Verifies:
1. Split existence and valid JSONL formatting.
2. Full provenance metadata presence on all records.
3. Zero train/val/test exact hash collisions.
4. 8-gram Jaccard overlap < 0.40 (no blueprint template leakage).
5. Entity span offset alignment with raw clause text.
6. Representation of all 11 canonical categories.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set
import pytest

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "datasets" / "real_estate_clauses"
SPLIT_FILES = {
    "train": DATA_DIR / "train.jsonl",
    "val": DATA_DIR / "val.jsonl",
    "test": DATA_DIR / "test.jsonl",
}

MANDATORY_PROVENANCE_FIELDS = [
    "clause_id",
    "title",
    "text",
    "category",
    "source_document",
    "source_url",
    "jurisdiction",
    "source_type",
    "license",
    "date",
    "annotation_version",
    "annotator_id",
    "entities",
]

EXPECTED_CATEGORIES = {
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
}


def compute_hash(text: str) -> str:
    norm = " ".join(text.lower().split())
    return hashlib.md5(norm.encode("utf-8")).hexdigest()


def extract_ngrams(text: str, n: int = 8) -> Set[str]:
    tokens = text.lower().split()
    if len(tokens) < n:
        return set([" ".join(tokens)])
    return set(" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1))


def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    if not set_a or not set_b:
        return 0.0
    union_len = len(set_a.union(set_b))
    if union_len == 0:
        return 0.0
    return len(set_a.intersection(set_b)) / union_len


@pytest.fixture(scope="module")
def dataset_records() -> Dict[str, List[dict]]:
    records_by_split = {}
    for split_name, path in SPLIT_FILES.items():
        assert path.exists(), f"Split file not found: {path}"
        recs = []
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                recs.append(data)
        records_by_split[split_name] = recs
    return records_by_split


def test_split_files_exist_and_not_empty(dataset_records):
    assert len(dataset_records["train"]) > 0, "Train split is empty"
    assert len(dataset_records["val"]) > 0, "Val split is empty"
    assert len(dataset_records["test"]) > 0, "Test split is empty"


def test_mandatory_provenance_fields(dataset_records):
    for split_name, recs in dataset_records.items():
        for rec in recs:
            for field in MANDATORY_PROVENANCE_FIELDS:
                assert field in rec, f"Missing {field} in {split_name} record {rec.get('clause_id')}"
                assert rec[field] is not None, f"Field {field} is None in {rec.get('clause_id')}"
            assert rec["category"] in EXPECTED_CATEGORIES, f"Invalid category {rec['category']}"
            assert rec["license"] in [
                "Government Open Data / Public Domain",
                "Public Domain",
                "Crown Copyright",
                "Open Government Data",
            ], f"Invalid or unverified license: {rec.get('license')}"


def test_all_11_categories_represented(dataset_records):
    train_cats = {r["category"] for r in dataset_records["train"]}
    test_cats = {r["category"] for r in dataset_records["test"]}
    assert train_cats == EXPECTED_CATEGORIES, f"Missing categories in train: {EXPECTED_CATEGORIES - train_cats}"
    assert test_cats == EXPECTED_CATEGORIES, f"Missing categories in test: {EXPECTED_CATEGORIES - test_cats}"


def test_zero_exact_hash_collisions(dataset_records):
    hashes = {}
    for split_name, recs in dataset_records.items():
        hashes[split_name] = {compute_hash(r["text"]) for r in recs}

    train_val_overlap = hashes["train"].intersection(hashes["val"])
    train_test_overlap = hashes["train"].intersection(hashes["test"])
    val_test_overlap = hashes["val"].intersection(hashes["test"])

    assert len(train_val_overlap) == 0, f"Found train-val hash collisions: {len(train_val_overlap)}"
    assert len(train_test_overlap) == 0, f"Found train-test hash collisions: {len(train_test_overlap)}"
    assert len(val_test_overlap) == 0, f"Found val-test hash collisions: {len(val_test_overlap)}"


def test_strict_8gram_jaccard_similarity(dataset_records):
    """
    Asserts max 8-gram Jaccard similarity across train and test splits is < 0.40,
    proving blueprint-level separation and zero template leakage.
    """
    train_grams = [extract_ngrams(r["text"], n=8) for r in dataset_records["train"]]
    test_grams = [extract_ngrams(r["text"], n=8) for r in dataset_records["test"]]

    max_jaccard = 0.0
    for t_idx, t_g in enumerate(test_grams):
        for tr_idx, tr_g in enumerate(train_grams):
            sim = jaccard_similarity(t_g, tr_g)
            if sim > max_jaccard:
                max_jaccard = sim

    assert max_jaccard < 0.40, f"8-gram Jaccard similarity exceeds threshold: {max_jaccard:.4f} >= 0.40"


def test_entity_span_alignment(dataset_records):
    for split_name, recs in dataset_records.items():
        for rec in recs:
            text = rec["text"]
            for ent in rec.get("entities", []):
                start = ent.get("start_char")
                end = ent.get("end_char")
                val = ent.get("text")
                assert start is not None and end is not None and val is not None
                extracted = text[start:end]
                assert extracted == val, (
                    f"Entity misalignment in {rec['clause_id']}: expected '{val}', got '{extracted}'"
                )


def test_corpus_manifest():
    manifest_path = DATA_DIR / "corpus_manifest.json"
    assert manifest_path.exists(), "Corpus manifest file not found"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert "provenance_sources" in manifest
    assert len(manifest["provenance_sources"]) >= 6
    for src in manifest["provenance_sources"]:
        assert "source_id" in src
        assert "jurisdiction" in src
        assert "title" in src
        assert "license" in src
