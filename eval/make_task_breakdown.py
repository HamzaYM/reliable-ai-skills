#!/usr/bin/env python3
"""Emit the per-task, per-run must-hit breakdown for the skills x effort lattice.

This is the finer-grained companion to eval/make_explorer.py. Where the
explorer draws the cell-level aggregates, this artifact holds every task's
must-hit hits broken out per run, for all 16 model x effort cells, so a UI
can show the run-to-run detail behind each cell.

It fixes an aggregation bug in the earlier hand-built task-breakdown.json:
that file declared 16 cells but only ever populated the 12 replicated
(3-run) cells, silently dropping the single-run cells (fable@medium,
fable@xhigh, haiku@none) and the invalid fable@max cell from every task.
Here every cell is emitted explicitly, with n_runs/shape making single-run,
triplicate, and no-data cells unambiguous.

Sources, all read at generation time (stdlib only, no network):
  - each cell's <run_dir>/scores.json, produced by the frozen scoring
    harness eval/harness/scoring.py. Replicated cells expose per-task,
    per-run hits at repeats_detail.per_repeat.rN.tasks[task]; single-run
    cells expose per-task hits at tasks[task].
  - results/matrix/matrix.json for the authoritative cell -> run_dir map
    and independent cross-check totals.
  - eval/tasks/golden-suite.jsonl for per-task metadata (skill, checklist).

Every emitted number is cross-checked against matrix.json and, when
present, the prior task-breakdown.json; a mismatch aborts the write.

Usage (from the repo root):
  python3 eval/make_task_breakdown.py \
      --matrix results/matrix/matrix.json \
      --golden eval/tasks/golden-suite.jsonl \
      --out results/matrix/task-breakdown-verified.json
"""

import argparse
import datetime
import json
import os
import sys

REGEN_COMMAND = (
    "python3 eval/make_task_breakdown.py --matrix results/matrix/matrix.json "
    "--golden eval/tasks/golden-suite.jsonl "
    "--out results/matrix/task-breakdown-verified.json"
)

# Presentation order (labels/ordering only, never numbers).
MODEL_SHORT = {
    "claude-fable-5": "fable",
    "claude-sonnet-5": "sonnet",
    "claude-opus-4-8": "opus",
    "claude-haiku-4-5-20251001": "haiku",
}
MODEL_ORDER = ["fable", "sonnet", "opus", "haiku"]
EFFORT_ORDER = ["low", "medium", "high", "xhigh", "max", "none"]

# The one attempted cell that produced no valid data, and is therefore
# absent from the published matrix. Included here as an explicit empty cell.
FABLE_MAX_DIR = "results/lattice-fable-max"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def short_cell(model, effort):
    return "%s@%s" % (MODEL_SHORT.get(model, model), effort)


def cell_sort_key(cell):
    model, effort = cell.split("@")
    mi = MODEL_ORDER.index(model) if model in MODEL_ORDER else len(MODEL_ORDER)
    ei = EFFORT_ORDER.index(effort) if effort in EFFORT_ORDER else len(EFFORT_ORDER)
    return (mi, ei)


def repo_root_of(path):
    """Best-effort repo root: matrix.json lives at results/matrix/matrix.json."""
    d = os.path.dirname(os.path.abspath(path))
    # .../results/matrix -> repo root two levels up
    return os.path.dirname(os.path.dirname(d))


# ---------------------------------------------------------------------------
# Per-cell extraction
# ---------------------------------------------------------------------------

def run_record(task_hits):
    """Normalize one run's per-task hit dict to the three fields we keep."""
    return {
        "cold_hits": task_hits["cold_hits"],
        "loaded_hits": task_hits["loaded_hits"],
        "n_must_hits": task_hits["n_must_hits"],
    }


def extract_cell(scores, tasks, repeats):
    """Return {task_id: {n_runs, shape, runs:{rN:{...}}}} for one cell.

    Replicated (repeats>1) cells read per-run hits from
    repeats_detail.per_repeat.rN.tasks; single-run cells read tasks[task].
    """
    out = {}
    if repeats and repeats > 1:
        per_repeat = scores["repeats_detail"]["per_repeat"]
        run_ids = sorted(per_repeat.keys())  # r1, r2, r3
        for tid in tasks:
            runs = {}
            for rid in run_ids:
                th = per_repeat[rid].get("tasks", {}).get(tid)
                if th is not None:
                    runs[rid] = run_record(th)
            out[tid] = {"n_runs": len(runs), "shape": "triplicate", "runs": runs}
    else:
        cell_tasks = scores.get("tasks", {})
        for tid in tasks:
            th = cell_tasks.get(tid)
            runs = {"r1": run_record(th)} if th is not None else {}
            out[tid] = {"n_runs": len(runs), "shape": "single", "runs": runs}
    return out


def empty_cell(tasks):
    """A cell that was attempted but produced no valid scored data."""
    return {tid: {"n_runs": 0, "shape": "no_valid_data", "runs": {}}
            for tid in tasks}


# ---------------------------------------------------------------------------
# Cross-checks (fail loud; evidence integrity over convenience)
# ---------------------------------------------------------------------------

def check_replicated_against_matrix(cell, per_task, matrix_cell, problems):
    """Sum of per-run per-task hits must equal matrix per-repeat totals."""
    mr = matrix_cell["aggregate_complete_case"]["mean_over_repeats"]["per_repeat"]
    for rid, mrec in mr.items():
        cold = sum(pt["runs"][rid]["cold_hits"]
                   for pt in per_task.values() if rid in pt["runs"])
        loaded = sum(pt["runs"][rid]["loaded_hits"]
                     for pt in per_task.values() if rid in pt["runs"])
        n = sum(pt["runs"][rid]["n_must_hits"]
                for pt in per_task.values() if rid in pt["runs"])
        if cold != mrec["cold_hits"] or loaded != mrec["loaded_hits"] \
                or n != mrec["n_expectations"]:
            problems.append(
                "%s %s: rebuilt (cold=%d loaded=%d n=%d) != matrix "
                "(cold=%d loaded=%d n=%d)"
                % (cell, rid, cold, loaded, n, mrec["cold_hits"],
                   mrec["loaded_hits"], mrec["n_expectations"]))


def check_single_against_matrix(cell, per_task, matrix_cell, problems):
    """Sum of single-run per-task hits must equal matrix cell aggregate."""
    agg = matrix_cell["aggregate_complete_case"]
    cold = sum(pt["runs"]["r1"]["cold_hits"]
               for pt in per_task.values() if "r1" in pt["runs"])
    loaded = sum(pt["runs"]["r1"]["loaded_hits"]
                 for pt in per_task.values() if "r1" in pt["runs"])
    n = sum(pt["runs"]["r1"]["n_must_hits"]
            for pt in per_task.values() if "r1" in pt["runs"])
    if cold != agg["cold_hits"] or loaded != agg["loaded_hits"] \
            or n != agg["n_expectations"]:
        problems.append(
            "%s: rebuilt (cold=%d loaded=%d n=%d) != matrix aggregate "
            "(cold=%d loaded=%d n=%d)"
            % (cell, cold, loaded, n, agg["cold_hits"], agg["loaded_hits"],
               agg["n_expectations"]))


def check_against_prior(prior, tasks_out, problems):
    """Every populated cell in the prior file must match, value for value."""
    prior_tasks = prior.get("tasks", {})
    for tid, cells in prior_tasks.items():
        for cell, runs in cells.items():
            if not runs:
                continue
            new = tasks_out.get(tid, {}).get(cell, {}).get("runs", {})
            for rid, rec in runs.items():
                nrec = new.get(rid)
                if nrec is None or any(nrec.get(k) != rec.get(k)
                                       for k in ("cold_hits", "loaded_hits",
                                                 "n_must_hits")):
                    problems.append(
                        "prior mismatch %s/%s/%s: prior=%s new=%s"
                        % (tid, cell, rid, rec, nrec))


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def build(matrix_path, golden_path, prior_path):
    matrix = load_json(matrix_path)
    root = repo_root_of(matrix_path)
    tasks = list(matrix["complete_case_tasks"])  # the 17 shared tasks

    # Per-task metadata from the frozen golden suite.
    golden = {}
    for line in open(golden_path, "r", encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        golden[r["id"]] = r
    tasks_meta = {}
    for tid in tasks:
        g = golden.get(tid, {})
        mh = g.get("must_hits", [])
        tasks_meta[tid] = {
            "skill": g.get("skill"),
            "fixture": g.get("fixture"),
            "n_must_hits": len(mh),
            "must_hit_ids": [m["id"] for m in mh],
        }

    # Cell -> (short id, run_dir, repeats) from the authoritative matrix,
    # plus the invalid fable@max cell that the matrix omits.
    cells = {}
    for c in matrix["cells"].values():
        sid = short_cell(c["model"], c["effort"])
        cells[sid] = {
            "run_dir": os.path.join(root, c["run_dir"]),
            "repeats": c.get("repeats", 1),
            "matrix_cell": c,
        }
    cells["fable@max"] = {
        "run_dir": os.path.join(root, FABLE_MAX_DIR),
        "repeats": None,
        "matrix_cell": None,
    }

    problems = []
    counts = {"triplicate": 0, "single": 0, "no_valid_data": 0}
    # tasks_out[task_id][cell] = {n_runs, shape, runs}
    tasks_out = {tid: {} for tid in tasks}

    for sid in sorted(cells, key=cell_sort_key):
        info = cells[sid]
        scores = load_json(os.path.join(info["run_dir"], "scores.json"))
        agg = scores.get("aggregate", {})
        if not agg.get("n_expectations"):
            # Attempted but no valid scored data (every task excluded).
            per_task = empty_cell(tasks)
            counts["no_valid_data"] += 1
        elif info["repeats"] and info["repeats"] > 1:
            per_task = extract_cell(scores, tasks, info["repeats"])
            check_replicated_against_matrix(sid, per_task, info["matrix_cell"],
                                            problems)
            counts["triplicate"] += 1
        else:
            per_task = extract_cell(scores, tasks, 1)
            check_single_against_matrix(sid, per_task, info["matrix_cell"],
                                        problems)
            counts["single"] += 1
        for tid in tasks:
            tasks_out[tid][sid] = per_task[tid]

    # Cross-check against the prior hand-built file, if present.
    if prior_path and os.path.isfile(prior_path):
        check_against_prior(load_json(prior_path), tasks_out, problems)

    if problems:
        raise SystemExit("cross-check failed, refusing to write:\n  "
                         + "\n  ".join(problems))

    ordered_cells = sorted(cells, key=cell_sort_key)
    meta = build_meta(ordered_cells, tasks, counts)
    return {"_meta": meta, "tasks_meta": tasks_meta, "tasks": tasks_out}


def build_meta(ordered_cells, tasks, counts):
    return {
        "purpose": (
            "Per-task, per-run must-hit breakdown for all 16 model x effort "
            "cells of the skills x effort lattice study, across the 17 shared "
            "tasks. Companion to results/matrix/explorer.html. Fixes the "
            "aggregation bug that silently dropped the single-run cells "
            "(fable@medium, fable@xhigh, haiku@none) and the invalid "
            "fable@max cell from the per-task view."),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
            .strftime("%Y-%m-%d %H:%M:%S UTC"),
        "generator": "eval/make_task_breakdown.py",
        "rebuild_command": REGEN_COMMAND,
        "source_of_truth": (
            "each cell's <run_dir>/scores.json from the frozen scoring "
            "harness eval/harness/scoring.py; replicated cells read "
            "repeats_detail.per_repeat.rN.tasks, single-run cells read "
            "tasks. Every value cross-checked against results/matrix/"
            "matrix.json (and the prior task-breakdown.json) before writing."),
        "metric": {
            "unit": (
                "must-hit checklist items: each task ships a short checklist "
                "an answer must satisfy; a two-judge panel with a pinned "
                "adjudicator decides HIT or MISS per item, per arm."),
            "cold_hits": (
                "checklist items satisfied WITHOUT the skill installed, out "
                "of n_must_hits (this run's denominator N)."),
            "loaded_hits": (
                "checklist items satisfied WITH the skill installed, out of "
                "n_must_hits."),
            "n_must_hits": (
                "denominator N for this run: the task's checklist length "
                "(4 for most tasks; 3 for env-hazards-t1 and mmar-t1; 5 for "
                "mt-auth-t1 and tcr-t1). Smaller only if a judge-failure "
                "exclusion dropped an item in that particular run."),
        },
        "how_cells_are_represented": {
            "triplicate": (
                "12 cells, run 3 times (repeats=3). n_runs=3, "
                "shape='triplicate', runs has r1/r2/r3, each an object "
                "{cold_hits, loaded_hits, n_must_hits}. Read across r1..r3 "
                "for the run-to-run spread; min and max across the three are "
                "the range the effort-curve side-ticks show."),
            "single": (
                "3 cells (fable@medium, fable@xhigh, haiku@none), run once "
                "(repeats=1). n_runs=1, shape='single', runs has ONLY r1, a "
                "single {cold_hits, loaded_hits, n_must_hits}. Same 'runs' "
                "container as triplicate cells so a UI can render every cell "
                "the same way; n_runs and shape are what tell single from "
                "triplicate. There is no r2/r3 because the condition was "
                "executed exactly once."),
            "no_valid_data": (
                "1 cell (fable@max). n_runs=0, shape='no_valid_data', "
                "runs={}. The run was attempted at repeats=3 but every task "
                "in every repeat errored at execution (claude exited 1; a "
                "mktemp temp-file collision in the runner), so all 17 tasks "
                "were excluded and no score exists. Absent from the published "
                "matrix; kept here as an explicit empty cell so a UI can "
                "label it 'run failed, no data' rather than omit it "
                "silently."),
        },
        "four_runs_question": (
            "No published cell has 4 repeat runs; the maximum is 3 (the 12 "
            "triplicate endpoints). Single-run cells are 1; fable@max "
            "attempted 3 but all failed. History: six conditions (opus and "
            "sonnet at medium/high/xhigh) were each run once early, archived "
            "under results/_superseded/*-1x, then re-run three times for the "
            "final data, so 4 total executions exist in the study history for "
            "each of those six; opus@medium additionally has partial re-run "
            "batches under results/_audit/. The published data pools only the "
            "final 3-run replication for every cell; the early 4th run was "
            "superseded, never mixed in."),
        "cells": ordered_cells,
        "n_cells": len(ordered_cells),
        "cell_counts": counts,
        "models": MODEL_SHORT,
        "effort_order": EFFORT_ORDER,
        "shared_tasks": tasks,
        "n_shared_tasks": len(tasks),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--golden", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prior", default="results/matrix/task-breakdown.json",
                    help="prior task-breakdown.json to cross-check against")
    args = ap.parse_args(argv)

    data = build(args.matrix, args.golden, args.prior)

    text = json.dumps(data, ensure_ascii=False, indent=2)
    if "—" in text:
        sys.exit("refusing to write: an em-dash reached the output")
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text + "\n")

    m = data["_meta"]
    print("wrote %s" % args.out)
    print("  %d cells: %s" % (m["n_cells"], m["cell_counts"]))
    print("  %d shared tasks" % m["n_shared_tasks"])


if __name__ == "__main__":
    main()
