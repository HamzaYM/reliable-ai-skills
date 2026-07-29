#!/usr/bin/env python3
"""Recompute the per-cell cost-per-run dataset the lattice page publishes.

Emits the JSON body of lab/lattice/cost-per-run-dataset.json (and the copy
embedded in lab/lattice/index.html) to stdout, so the published averages can
be reproduced from the raw record instead of being hand-carried.

Method, one entry per lattice cell:

  - read every results/lattice-*/consumer/*.json artifact and take its
    `total_cost_usd`, `task`, `repeat` and `arm` fields;
  - PAIR on (task, repeat): a run enters the average only if BOTH its cold and
    its loaded twin exist. A one-sided arm is dropped from both sides, never
    from one, so a missing loaded run can never make a cell look cheaper with
    skills than without;
  - n_cold and n_loaded are the paired count and are equal by construction;
  - avg_cold_usd / avg_loaded_usd are the paired means, skill_marginal_usd is
    avg_loaded_usd - avg_cold_usd, each rounded once to 4 decimals.

Cell sources: every cell reads from this repo's results/. The Fable max-effort
cell is the exception -- it is the pre-registered OPEN cell whose artifacts
were never published here (results/lattice-fable-max/consumer holds 2 of 96
runs), so its artifacts are read from FABLE_MAX_SRC below. Point that at a
checkout that carries the full cell, or pass --fable-max-dir. Fable-max stays
exploratory-only and is not part of the confirmatory 15-cell matrix.

Additive and stdlib-only. Touches no existing harness file, writes no file.
"""

import argparse
import glob
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(REPO, "results")

# The exploratory Fable-max cell lives outside this repo (see docstring).
FABLE_MAX_SRC = os.path.expanduser("~/repos/hamza-skills-oss/results/lattice-fable-max")

# Publication order of the dataset file: the 15 confirmatory cells, then the
# added-later Fable-max addendum last.
CELL_ORDER = [
    "lattice-fable-high",
    "lattice-fable-low",
    "lattice-fable-medium",
    "lattice-fable-xhigh",
    "lattice-haiku",
    "lattice-opus-high",
    "lattice-opus-low",
    "lattice-opus-max",
    "lattice-opus-medium",
    "lattice-opus-xhigh",
    "lattice-sonnet-high",
    "lattice-sonnet-low",
    "lattice-sonnet-max",
    "lattice-sonnet-medium",
    "lattice-sonnet-xhigh",
    "lattice-fable-max",
]


def cell_costs(cell_dir):
    """Return {(task, repeat, arm): cost_usd} for one cell directory."""
    runs = {}
    for path in sorted(glob.glob(os.path.join(cell_dir, "consumer", "*.json"))):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        key = (d["task"], int(d["repeat"]), d["arm"])
        if key in runs:
            raise SystemExit("duplicate artifact for %s in %s" % (key, cell_dir))
        runs[key] = float(d["total_cost_usd"])
    return runs


def cell_entry(cell_dir):
    """Paired per-run cost summary for one cell, or None if nothing pairs."""
    runs = cell_costs(cell_dir)
    paired = sorted(
        (task, repeat)
        for (task, repeat, arm) in runs
        if arm == "cold" and (task, repeat, "loaded") in runs
    )
    if not paired:
        return None, []
    dropped = sorted(
        (task, repeat, arm)
        for (task, repeat, arm) in runs
        if (task, repeat) not in set(paired)
    )
    n = len(paired)
    cold = sum(runs[(t, r, "cold")] for t, r in paired) / n
    loaded = sum(runs[(t, r, "loaded")] for t, r in paired) / n
    return (
        {
            "n_cold": n,
            "avg_cold_usd": round(cold, 4),
            "n_loaded": n,
            "avg_loaded_usd": round(loaded, 4),
            "skill_marginal_usd": round(loaded - cold, 4),
        },
        dropped,
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--fable-max-dir",
        default=FABLE_MAX_SRC,
        help="cell directory holding the full exploratory Fable-max run",
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="report unpaired artifacts on stderr",
    )
    args = ap.parse_args()

    out = {}
    for cell in CELL_ORDER:
        cell_dir = os.path.join(RESULTS, cell)
        if cell == "lattice-fable-max":
            cell_dir = args.fable_max_dir
        entry, dropped = cell_entry(cell_dir)
        if entry is None:
            raise SystemExit("no paired runs found in %s" % cell_dir)
        if dropped and args.verbose:
            import sys

            print("%s: dropped unpaired %s" % (cell, dropped), file=sys.stderr)
        out[cell] = entry

    print(json.dumps(out, indent=1), end="")


if __name__ == "__main__":
    main()
