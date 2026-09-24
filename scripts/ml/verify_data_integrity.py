"""
ClauseGuard Phase 9: Dataset Integrity and Anti-Contamination Verification
Verifies:
1. Complete provenance metadata on every record (source_document, source_url, jurisdiction, license, date).
2. Zero exact-text or MD5 hash collisions across train, val, and test splits.
3. Strict 8-gram Jaccard overlap threshold (< 0.40) between train and test splits.
4. Entity span index alignment with raw text.
5. All 11 categories represented in all partitions.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

DATA_DIR = Path("data/datasets/real_estate_clauses")
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


def verify_splits() -> bool:
    print("=" * 70)
    print("CLAUSEGUARD PHASE 9: DATASET INTEGRITY & CONTAMINATION VERIFICATION")
    print("=" * 70)

    records_by_split: Dict[str, List[dict]] = {}
    hashes_by_split: Dict[str, Set[str]] = {}
    errors = []

    for split_name, path in SPLIT_FILES.items():
        if not path.exists():
            errors.append(f"Missing split file: {path}")
            continue

        records = []
        hashes = set()
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"JSON decode error in {split_name} line {line_no}: {e}")
                    continue

                # 1. Check mandatory provenance fields
                for field in MANDATORY_PROVENANCE_FIELDS:
                    if field not in rec or rec[field] is None:
                        errors.append(f"Record {rec.get('clause_id', line_no)} in {split_name} missing mandatory field: {field}")

                # 2. Check valid category
                cat = rec.get("category")
                if cat not in EXPECTED_CATEGORIES:
                    errors.append(f"Unknown category '{cat}' in record {rec.get('clause_id')} ({split_name})")

                # 3. Check entity offset validity
                text = rec.get("text", "")
                for ent in rec.get("entities", []):
                    s, e, expected_txt = ent.get("start_char"), ent.get("end_char"), ent.get("text")
                    if s is not None and e is not None and expected_txt is not None:
                        actual_slice = text[s:e]
                        if actual_slice != expected_txt:
                            errors.append(
                                f"Entity offset mismatch in {rec.get('clause_id')}: "
                                f"expected '{expected_txt}', slice was '{actual_slice}'"
                            )

                h = compute_hash(text)
                hashes.add(h)
                records.append(rec)

        records_by_split[split_name] = records
        hashes_by_split[split_name] = hashes
        print(f"[{split_name.upper()}] Loaded {len(records)} records. Unique hashes: {len(hashes)}")

    if errors:
        print("\n❌ INTEGRITY ERRORS FOUND:")
        for err in errors[:10]:
            print(f"  • {err}")
        return False

    # 4. Check for cross-split exact collisions
    splits = ["train", "val", "test"]
    for i in range(len(splits)):
        for j in range(i + 1, len(splits)):
            s1, s2 = splits[i], splits[j]
            overlap = hashes_by_split[s1].intersection(hashes_by_split[s2])
            if overlap:
                errors.append(f"Data leakage detected! {len(overlap)} exact hash collisions between '{s1}' and '{s2}'")

    # 5. Check 8-gram Jaccard contamination between train and test
    train_texts = [r["text"] for r in records_by_split["train"]]
    test_texts = [r["text"] for r in records_by_split["test"]]

    max_jaccard = 0.0
    high_overlap_pairs = 0
    for t_text in test_texts:
        test_ngrams = extract_ngrams(t_text, n=8)
        for tr_text in train_texts:
            tr_ngrams = extract_ngrams(tr_text, n=8)
            sim = jaccard_similarity(test_ngrams, tr_ngrams)
            if sim > max_jaccard:
                max_jaccard = sim
            if sim >= 0.40:
                high_overlap_pairs += 1

    print(f"\n[LEAKAGE CHECK] Max 8-gram Jaccard similarity between Train and Test: {max_jaccard:.4f}")
    if max_jaccard >= 0.40:
        errors.append(
            f"Contamination threshold exceeded! Max 8-gram Jaccard is {max_jaccard:.4f} (limit: < 0.40). "
            f"{high_overlap_pairs} pairs exceeded threshold."
        )

    # 6. Verify all 11 categories in all splits
    for s_name in splits:
        found_cats = set(r["category"] for r in records_by_split[s_name])
        missing = EXPECTED_CATEGORIES - found_cats
        if missing:
            errors.append(f"Split '{s_name}' is missing {len(missing)} categories: {missing}")

    if errors:
        print("\n❌ VERIFICATION FAILED:")
        for err in errors:
            print(f"  • {err}")
        return False

    print("\n✅ ZERO DATA LEAKAGE: Exact collisions = 0")
    print(f"✅ N-GRAM OVERLAP GATE PASSED: Max Jaccard = {max_jaccard:.4f} < 0.40")
    print(f"✅ CATEGORY COVERAGE COMPLETE: All 11 categories verified across train, val, and test")
    print("✅ PROVENANCE AUDIT PASSED: Mandatory statutory metadata verified for 100% of samples")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = verify_splits()
    sys.exit(0 if success else 1)
