#!/usr/bin/env python3
"""Tune v2's decision thresholds.

Reads training/threshold_tuning_set.jsonl and sweeps candidate thresholds
per slice, keeping the setting with the best F1.
"""
import json
import pathlib

TUNING_SET = pathlib.Path(__file__).resolve().parents[1] / "training" / "threshold_tuning_set.jsonl"


def main():
    rows = [json.loads(l) for l in TUNING_SET.read_text().splitlines()]
    print(f"tuning on {len(rows)} rows")


if __name__ == "__main__":
    main()
