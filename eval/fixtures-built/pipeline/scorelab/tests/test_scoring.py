"""Golden comparison."""
import json
import pathlib

from score import score

GOLDEN = pathlib.Path(__file__).parent / "golden" / "expected_scores.json"

ITEMS = [
    {"id": "item-1", "precision": 0.8, "coverage": 0.65, "confidence": 0.8123},
    {"id": "item-2", "precision": 0.5, "coverage": 0.7, "confidence": 0.4444},
    {"id": "item-3", "precision": 1.0, "coverage": 0.75, "confidence": 0.6333},
]


def test_scores_match_golden():
    expected = json.loads(GOLDEN.read_text())
    for item in ITEMS:
        got = score(item)
        assert expected[item["id"]]["score"] == got["score"]
        assert expected[item["id"]]["confidence"] == got["confidence"]
