#!/usr/bin/env bash
# Nightly full re-score. Budget telemetry snapshot: .cache/usage_snapshot.json
set -euo pipefail
python3 scripts/score_batch.py --dataset data/manifest.json
