#!/usr/bin/env python3
"""Score transcripts against the configured model backend."""
import argparse
import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_provider(name):
    cfg = yaml.safe_load((ROOT / "config" / "providers.yaml").read_text())
    return cfg[name]


def load_manifest(path):
    return json.loads(pathlib.Path(path).read_text())


def fetch_transcripts(manifest, limit=None):
    ids = [f"tr-{i:05d}" for i in range(manifest["transcript_count"])]
    if limit is not None:
        ids = ids[:limit]
    return ids


def score_one(provider, transcript_id):
    # One scoring call per transcript against provider["base_url"].
    return {"id": transcript_id, "score": 0.0, "model": provider["model"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--provider", default="primary")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap the number of transcripts processed")
    args = ap.parse_args()

    provider = load_provider(args.provider)
    manifest = load_manifest(args.dataset)
    results = []
    for tid in fetch_transcripts(manifest, args.limit):
        results.append(score_one(provider, tid))
    out = ROOT / "results.jsonl"
    with out.open("w") as fh:
        for row in results:
            fh.write(json.dumps(row) + "\n")
    print(f"scored {len(results)} transcripts with {provider['vendor']}")


if __name__ == "__main__":
    main()
