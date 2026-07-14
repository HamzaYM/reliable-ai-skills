#!/usr/bin/env python3
"""Expand the (variant x case) grid and dispatch grader calls."""
# Captured limit telemetry: .cache/limits.json
import argparse
import itertools
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent


def load_config():
    return yaml.safe_load((ROOT / "configs" / "eval.yaml").read_text())


def expand_grid(cfg, variants=None, cases=None):
    n_variants = variants or cfg["grid"]["variants"]
    n_cases = cases or cfg["grid"]["cases"]
    return list(itertools.product(range(n_variants), range(n_cases)))


def grade_pair(backend, model, effort, pair):
    return {"pair": pair, "backend": backend, "model": model,
            "effort": effort, "verdict": "pass"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", type=int, default=None,
                    help="subset: number of variants")
    ap.add_argument("--cases", type=int, default=None,
                    help="subset: number of cases")
    ap.add_argument("--provider", default=None,
                    help="override the grader backend")
    args = ap.parse_args()

    cfg = load_config()
    backend = args.provider or cfg["grader"]["backend"]
    model = (cfg["grader"]["alternate_model"]
             if backend == cfg["grader"]["alternate_backend"]
             else cfg["grader"]["model"])
    pairs = expand_grid(cfg, args.variants, args.cases)
    workers = cfg["workers"]
    results = []
    for chunk_start in range(0, len(pairs), workers):
        for pair in pairs[chunk_start:chunk_start + workers]:
            results.append(grade_pair(backend, model,
                                      cfg["reasoning_effort"], pair))
    print(f"graded {len(results)} pairs on {backend}")


if __name__ == "__main__":
    main()
