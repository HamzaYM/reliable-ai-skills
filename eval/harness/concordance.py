"""Deterministic Codex concordance sample over committed judge inputs.

Pre-registered exploratory robustness check: 50 comparisons are selected
deterministically by hash-parity over the committed judge-input files and
emitted as a manifest for manual re-scoring on Codex (a second vendor).
The resulting concordance rate is exploratory only and never touches any
verdict. There is no Codex API integration by design; the committed judge
inputs are public precisely so third parties can extend the cross-vendor
audit.
"""
import hashlib
import json
from pathlib import Path

from . import REPO_ROOT

SAMPLE_SIZE = 50

SELECTION_RULE = (
    "compute SHA-256 over the committed judge-input file bytes of every "
    "comparison in the given runs; keep the comparisons whose digest is "
    "even (digest as an integer, mod 2 == 0); sort the kept comparisons "
    "by digest ascending; take the first {size}"
)


class ConcordanceError(Exception):
    pass


def _rel(path):
    path = Path(path).resolve()
    return (
        str(path.relative_to(REPO_ROOT))
        if path.is_relative_to(REPO_ROOT) else str(path)
    )


def build_manifest(run_dirs, sample_size=SAMPLE_SIZE):
    """Select the concordance sample from one or more completed runs.

    Deterministic given the committed judge-input bytes: re-running over
    the same run directories always yields the same manifest, so the
    selection cannot be steered after seeing any scores.
    """
    items = []
    seen_runs = set()
    for run_dir in run_dirs:
        run_dir = Path(run_dir)
        meta_path = run_dir / "run-meta.json"
        if not meta_path.is_file():
            raise ConcordanceError(
                f"{run_dir}: not a run directory (no run-meta.json)"
            )
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        run_id = meta.get("run_id", run_dir.name)
        if run_id in seen_runs:
            raise ConcordanceError(
                f"run {run_id} passed more than once; pass each run once"
            )
        seen_runs.add(run_id)
        input_files = sorted((run_dir / "judge-inputs").glob("*.json"))
        if not input_files:
            raise ConcordanceError(
                f"{run_dir}: no committed judge inputs under judge-inputs/"
            )
        for p in input_files:
            raw = p.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            data = json.loads(raw.decode("utf-8"))
            items.append({
                "run_id": run_id,
                "pair": data.get("pair", p.stem),
                "task": data.get("task"),
                "judge_input": _rel(p),
                "judge_input_sha256": digest,
            })
    kept = sorted(
        (i for i in items if int(i["judge_input_sha256"], 16) % 2 == 0),
        key=lambda i: i["judge_input_sha256"],
    )
    selected = kept[:sample_size]
    return {
        "purpose": (
            "exploratory cross-vendor concordance sample for manual Codex "
            "re-scoring; the result is reported as a concordance rate only "
            "and never touches any verdict"
        ),
        "selection_rule": SELECTION_RULE.format(size=sample_size),
        "sample_size_target": sample_size,
        "pool_comparisons": len(items),
        "parity_kept": len(kept),
        "selected_n": len(selected),
        "shortfall_note": (
            None if len(selected) >= sample_size else
            "the even-parity pool is smaller than the target; every kept "
            "comparison is selected and the shortfall stands (no backfill "
            "from the odd-parity pool, which would change the "
            "pre-registered rule)"
        ),
        "judge_schema": "eval/schemas/judge.schema.json",
        "instructions": (
            "for each selected comparison, submit the committed "
            "judge-input prompt to Codex, collect one judgment conforming "
            "to the judge schema, and compare its per must-hit marks "
            "against the committed Claude panel marks for the same "
            "comparison"
        ),
        "selected": selected,
    }
