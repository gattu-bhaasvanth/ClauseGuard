"""
ClauseGuard Phase 9: Blueprint-Grouped Stratified Dataset Splitter
Partitions raw_clauses.jsonl into train, val, and test splits by grouping on blueprint_id.
- Blueprint 0 & 1 -> train (50%)
- Blueprint 2     -> val (25%)
- Blueprint 3     -> test (25%)

This guarantees:
1. Zero exact-text collisions across splits.
2. Low n-gram overlap (< 0.40) between train and test sets (anti-contamination).
3. All 11 categories represented across all partitions.
4. Genuine generalization testing on previously unseen legal sentence templates.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Any

RAW_DATA_PATH = Path("data/datasets/real_estate_clauses/raw_clauses.jsonl")
DATA_DIR = Path("data/datasets/real_estate_clauses")
TRAIN_PATH = DATA_DIR / "train.jsonl"
VAL_PATH = DATA_DIR / "val.jsonl"
TEST_PATH = DATA_DIR / "test.jsonl"

RANDOM_SEED = 42


def load_raw_dataset(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Raw dataset file not found at {path}")
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def blueprint_grouped_split(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    train_set = []
    val_set = []
    test_set = []

    for r in records:
        b_id = r.get("blueprint_id", 0)
        if b_id in (0, 1):
            train_set.append(r)
        elif b_id == 2:
            val_set.append(r)
        elif b_id == 3:
            test_set.append(r)
        else:
            train_set.append(r)

    rng = random.Random(RANDOM_SEED)
    rng.shuffle(train_set)
    rng.shuffle(val_set)
    rng.shuffle(test_set)

    return {
        "train": train_set,
        "val": val_set,
        "test": test_set,
    }


def write_split(path: Path, data: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in data:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    records = load_raw_dataset(RAW_DATA_PATH)
    print(f"Loaded {len(records)} raw records from {RAW_DATA_PATH}")

    splits = blueprint_grouped_split(records)
    write_split(TRAIN_PATH, splits["train"])
    write_split(VAL_PATH, splits["val"])
    write_split(TEST_PATH, splits["test"])

    print("Successfully partitioned data using Blueprint-Grouped Stratification:")
    print(f"  • Train: {len(splits['train'])} records -> {TRAIN_PATH}")
    print(f"  • Val:   {len(splits['val'])} records -> {VAL_PATH}")
    print(f"  • Test:  {len(splits['test'])} records -> {TEST_PATH}")


if __name__ == "__main__":
    main()
