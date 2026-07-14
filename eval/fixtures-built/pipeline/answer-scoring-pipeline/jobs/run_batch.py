"""Batch runner."""
import json
import pathlib

from scoring.scorer import score

EVAL_SET = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "eval_set.jsonl"


def run():
    rows = [json.loads(l) for l in EVAL_SET.read_text().splitlines()]
    return [score(r["answer"], r["reference"]) for r in rows]
