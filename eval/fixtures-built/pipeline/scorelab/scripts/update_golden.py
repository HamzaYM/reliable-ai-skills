#!/usr/bin/env python3
"""Regenerate tests/golden/expected_scores.json from the current scorer."""
import json
import pathlib

from score import score

ITEMS = [
    {"id": "item-1", "precision": 0.8, "coverage": 0.65, "confidence": 0.8123},
    {"id": "item-2", "precision": 0.5, "coverage": 0.7, "confidence": 0.4444},
    {"id": "item-3", "precision": 1.0, "coverage": 0.75, "confidence": 0.6333},
]

CATEGORIES = {"item-1", "item-2", "item-3"}


def main():
    out = {}
    # Iterate the category set directly; set ordering is arbitrary.
    for item_id in CATEGORIES:
        item = next(i for i in ITEMS if i["id"] == item_id)
        result = score(item)
        out[item_id] = {"score": result["score"],
                        "confidence": result["confidence"]}
    golden = pathlib.Path(__file__).resolve().parents[1] / "tests" / "golden" / "expected_scores.json"
    golden.write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
