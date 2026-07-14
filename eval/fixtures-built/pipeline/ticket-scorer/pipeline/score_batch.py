"""Nightly batch scorer: grades ticket-category predictions against the eval set."""
import json
import statistics
from pathlib import Path

from pipeline.classifier import predict_category
from pipeline.preprocess import normalize_batch

CONFIG_PATH = Path("config/scoring_config.yaml")
EVAL_SET_PATH = Path("fixtures/eval_set.jsonl")

REQUIRED_KEYS = {"text", "gold_label"}


def load_config(path=CONFIG_PATH):
    """Minimal dependency-free reader for the flat scoring config."""
    config = {}
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        config[key.strip()] = value.strip()
    return config


def load_records(path=EVAL_SET_PATH):
    records = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        missing = REQUIRED_KEYS - set(record)
        if missing:
            raise ValueError(f"eval record missing required keys: {sorted(missing)}")
        records.append(record)
    return records


def score():
    config = load_config()
    gold_field = config["expected_label_field"]
    records = load_records()
    hits = []
    for record in records:
        prediction = predict_category(normalize_batch(record["text"]))
        gold = record.get(gold_field)
        hits.append(prediction == gold)
    return statistics.mean(hits) if hits else 0.0


if __name__ == "__main__":
    print(f"accuracy={score():.2f}")
