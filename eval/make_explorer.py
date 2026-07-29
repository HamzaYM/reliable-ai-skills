#!/usr/bin/env python3
"""Emit the merged lattice results explorer as one self-contained HTML file.

Reads the final matrix artifact (results/matrix/matrix.json), the per-cell
scores.json files under the run directories, the second-vendor concordance
spot-check, the verified per-task/per-run breakdown
(results/matrix/task-breakdown-verified.json), and the frozen golden suite
(eval/tasks/golden-suite.jsonl). It cross-checks the matrix numbers against
the per-cell artifacts and writes a single HTML page with the data embedded as
JSON. Stdlib only. No network, no external assets. Every number on the page
comes from the JSON read at generation time; the template contributes labels
only.

This one generator now emits BOTH the per-cell summary AND the per-task
drill-down (the old separate task explorer), so the two views share one build
stamp, one suite hash, and one source of truth.

Usage (from the repo root):
  python3 eval/make_explorer.py --matrix results/matrix/matrix.json \
      --cells 'results/lattice-*' \
      --breakdown results/matrix/task-breakdown-verified.json \
      --golden eval/tasks/golden-suite.jsonl \
      --out results/matrix/explorer.html
"""

import argparse
import datetime
import glob
import hashlib
import html
import json
import os
import sys

REGEN_COMMAND = (
    "python3 eval/make_explorer.py --matrix results/matrix/matrix.json "
    "--cells 'results/lattice-*' "
    "--breakdown results/matrix/task-breakdown-verified.json "
    "--golden eval/tasks/golden-suite.jsonl "
    "--out results/matrix/explorer.html")
DEFAULT_CONCORDANCE = "results/concordance/codex-concordance.json"
DEFAULT_BREAKDOWN = "results/matrix/task-breakdown-verified.json"
DEFAULT_GOLDEN = "eval/tasks/golden-suite.jsonl"
DEFAULT_LINKS = "results/matrix/task-github-links.json"
REPO_LABEL = "HamzaYM/reliable-ai-skills"
SCRIPT_BLOB = ("https://github.com/HamzaYM/reliable-ai-skills/blob/main/"
               "eval/make_explorer.py")

_HERE = os.path.dirname(os.path.abspath(__file__))
FAVICON_FILE = os.path.join(_HERE, "explorer-favicon.txt")
TASK_LABELS_FILE = os.path.join(_HERE, "explorer-task-labels.json")

# Presentation-only configuration (labels and ordering, never numbers).
EFFORT_ORDER = ["low", "medium", "high", "xhigh", "max"]
MODEL_ORDER = ["claude-fable-5", "claude-sonnet-5", "claude-opus-4-8"]
BASELINE_LABEL = "no effort setting, shown for reference"
OPEN_CELL_LABEL = "max run not finished"

# Locked, owner-approved copy for the Fable-at-max addendum badge. Reused
# verbatim (badge text and its hover tooltip); never paraphrased. The cost
# figure here is the centrally recomputed total published in
# results/matrix/NUMBERS.md; it is not recomputed by this generator (see the
# note in build_extra_display about which artifacts that total counts).
LOCKED_COPY = {
    "badge": "added later",
    "hoverFull": (
        "Fable at max was run separately after publication and added "
        "2026-07-12. It completed 16 of 17 tasks: mmar-t1 timed out on a "
        "second machine and was excluded, not a quality issue. Cold 97.4% "
        "· loaded 100.0% · change +2.6 pp. Cost $219.62. It does not "
        "join the confirmatory matrix: Fable's pre-registered pair stays low "
        "vs high."),
}

# Short breakdown keys (fable@low) map to matrix model ids (claude-fable-5).
SHORT2FULL = {
    "fable": "claude-fable-5",
    "sonnet": "claude-sonnet-5",
    "opus": "claude-opus-4-8",
    "haiku": "claude-haiku-4-5-20251001",
}
TASK_MODEL_ORDER = ["fable", "sonnet", "opus", "haiku"]

# Effort-curves panel order, laid out as a 2x2 grid (top row, then bottom row):
#   Haiku   Sonnet
#   Opus    Fable
CURVES_ORDER = ["haiku", "sonnet", "opus", "fable"]

# Series colours (warm Fable, green-teal Opus, blue-violet Sonnet, gray Haiku).
SERIES_COLORS = {
    "fable": "#E8734A",
    "opus": "#27A37A",
    "sonnet": "#6C5CE0",
    "haiku": "#8A94A0",
}


def model_color(model):
    for key, col in SERIES_COLORS.items():
        if key in model:
            return col
    return SERIES_COLORS["haiku"]


def short_of(model):
    for key in SERIES_COLORS:
        if key in model:
            return key
    return "haiku"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_text_asset(path):
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def esc(s):
    return html.escape(str(s), quote=True)


def esc_task(s):
    """Escape frozen task prose. Any em/en dash in the source text becomes an
    HTML entity so the literal character never reaches the output (the em-dash
    guard protects the template copy, not the verbatim task artifacts, which
    still display faithfully)."""
    return (html.escape(str(s), quote=True)
            .replace("—", "&mdash;")
            .replace("–", "&ndash;"))


def fmt_pct(v):
    return "{:.1f}%".format(v)


def fmt_round_pct(v):
    return "{:.0f}%".format(v)


def fmt_delta(v):
    return "{:+.1f}".format(v)


def fmt_signed_int(v):
    return "{:+d}".format(int(round(v)))


def fmt_mean(v):
    s = "{:.1f}".format(v)
    return s[:-2] if s.endswith(".0") else s


def fmt_thousands(n):
    return "{:,}".format(int(n))


# ---------------------------------------------------------------------------
# Data assembly: matrix cells, concordance, judging (unchanged core)
# ---------------------------------------------------------------------------

def scan_cell_dirs(pattern):
    scanned, skipped = {}, []
    for d in sorted(glob.glob(pattern)):
        if not os.path.isdir(d):
            continue
        scores_path = os.path.join(d, "scores.json")
        meta_path = os.path.join(d, "run-meta.json")
        if not os.path.isfile(scores_path):
            skipped.append((d, "no scores.json"))
            continue
        meta = load_json(meta_path) if os.path.isfile(meta_path) else {}
        scanned[os.path.basename(d)] = {
            "dir": d,
            "scores": load_json(scores_path),
            "meta": meta,
        }
    return scanned, skipped


def cross_check(matrix, scanned):
    warnings, used = [], set()
    for key, cell in matrix["cells"].items():
        base = os.path.basename(cell.get("run_dir") or cell.get("run_id") or "")
        rec = scanned.get(base)
        if rec is None:
            warnings.append(
                "%s: run dir %s not found under --cells; matrix values "
                "shown without per-cell cross-check" % (key, base))
            continue
        used.add(base)
        sa = rec["scores"].get("aggregate", {})
        ma = cell.get("aggregate", {})
        for field in ("n_expectations", "cold_hits", "loaded_hits"):
            if sa.get(field) != ma.get(field):
                warnings.append(
                    "%s: %s mismatch (matrix %s vs scores.json %s)"
                    % (key, field, ma.get(field), sa.get(field)))
    return warnings, used


def find_open_and_extra(scanned, used):
    open_cells, extras = [], []
    for base, rec in sorted(scanned.items()):
        if base in used:
            continue
        agg = rec["scores"].get("aggregate", {})
        meta = rec["meta"]
        if not agg.get("n_expectations"):
            open_cells.append({
                "run_id": base,
                "model": meta.get("model", "unknown"),
                "effort": meta.get("effort", "unknown"),
                "preregistered": bool(meta.get("preregistered")),
            })
        else:
            extras.append(build_extra_display(base, rec))
    return open_cells, extras


def build_cell_display(key, cell):
    cc = cell["aggregate_complete_case"]
    replicated = bool(cell.get("replicated"))
    rec = {
        "key": key,
        "model": cell["model"],
        "effort": cell["effort"],
        "run_id": cell.get("run_id"),
        "replicated": replicated,
        "repeats": cell.get("repeats", 1),
        "n_tasks": cc["n_tasks"],
        "n_expectations": cc["n_expectations"],
        "label": cc["label"],
        "excluded_tasks": cell.get("excluded_tasks", []),
    }
    if replicated:
        m = cc["mean_over_repeats"]
        rec.update(cold=m["cold_rate_pct"], loaded=m["loaded_rate_pct"],
                   delta=m["delta_pp"],
                   per_repeat=[
                       {"cold": r["cold_rate_pct"],
                        "loaded": r["loaded_rate_pct"],
                        "delta": r["delta_pp"]}
                       for _, r in sorted(m["per_repeat"].items())])
    else:
        rec.update(cold=cc["cold_rate_pct"], loaded=cc["loaded_rate_pct"],
                   delta=cc["delta_pp"],
                   cold_hits=cc["cold_hits"], loaded_hits=cc["loaded_hits"])
    return rec


def build_extra_display(base, rec):
    """Display record for a scored run directory that is not one of the
    confirmatory matrix cells (e.g. the Fable-at-max addendum). Mirrors
    build_cell_display()'s replicated/single shape, but reads the run-dir
    scores.json, whose shape differs from a matrix cell: the aggregate lives
    under `aggregate`, and for a replicated cell the repeat-mean endpoint is
    `repeats_detail.mean_over_repeats` with a sibling `repeats_detail.per_repeat`
    (the matrix cell nests per_repeat inside mean_over_repeats instead).

    Cost is intentionally omitted. This generator does not compute cost; the
    per-artifact total_cost_usd summation lives in eval/make_numbers.py, which
    counts, for every cell, only the artifacts for tasks that entered that
    cell's scores. The excluded mmar-t1 task's partial consumer runs ship in
    the addendum directory as evidence of what ran and carry no cost against
    the cell, the same way they carry no score, so the published addendum cost
    ($219.62) is the sum over the 16 scored tasks. That figure is carried
    verbatim in the locked badge copy, not derived here."""
    scores = rec["scores"]
    meta = rec["meta"]
    agg = scores.get("aggregate", {})
    rd = scores.get("repeats_detail") or {}
    mor = rd.get("mean_over_repeats")
    replicated = bool(mor)
    disp = {
        "run_id": base,
        "model": meta.get("model", "unknown"),
        "effort": meta.get("effort", "unknown"),
        "replicated": replicated,
        "repeats": scores.get("repeats", meta.get("repeats", 1)),
        "n_tasks": len(scores.get("tasks", {})),
        "n_expectations": agg.get("n_expectations"),
        "excluded_tasks": scores.get("excluded_tasks", []),
        "cold_hits": agg.get("cold_hits"),
        "loaded_hits": agg.get("loaded_hits"),
    }
    if replicated:
        disp.update(
            cold=mor["cold_rate_pct"], loaded=mor["loaded_rate_pct"],
            delta=mor["delta_pp"],
            per_repeat=[
                {"cold": r["cold_rate_pct"], "loaded": r["loaded_rate_pct"],
                 "delta": r["delta_pp"]}
                for _, r in sorted(rd.get("per_repeat", {}).items())])
    else:
        cold, loaded = agg.get("cold_pct"), agg.get("loaded_pct")
        delta = (loaded - cold) if None not in (cold, loaded) else None
        disp.update(cold=cold, loaded=loaded, delta=delta)
    return disp


def build_concordance(concordance, cells):
    def _base_run_id(run_id):
        # matrix.json labels some replicated cells with a "-v2" suffix
        # (e.g. lattice-opus-high-v2) reflecting a later consolidation pass;
        # the concordance file's "cell" values are the plain run-directory
        # basename Codex actually sampled from (e.g. lattice-opus-high), so
        # strip the label to match.
        return run_id[:-3] if run_id and run_id.endswith("-v2") else run_id

    run_to_key = {
        _base_run_id(c["run_id"]): c["key"] for c in cells.values() if c.get("run_id")
    }
    per_cell = {}
    for comp in concordance.get("per_comparison", []):
        key = run_to_key.get(comp.get("cell"))
        if key is None:
            continue
        agg = per_cell.setdefault(
            key, {"n_comparisons": 0, "n_marks": 0, "n_agree": 0})
        agg["n_comparisons"] += 1
        agg["n_marks"] += comp.get("n_marks", 0)
        agg["n_agree"] += comp.get("n_agree", 0)
    for agg in per_cell.values():
        agg["n_disagree"] = agg["n_marks"] - agg["n_agree"]
    ov = concordance.get("overall", {})
    return {
        "overall_pct": ov.get("concordance_pct"),
        "n_marks": ov.get("n_marks"),
        "n_agree": ov.get("n_agree"),
        "sample_size": concordance.get("sample_size"),
        "n_comparisons": concordance.get("n_comparisons"),
        "codex_model": (concordance.get("codex_models_seen") or ["gpt-5.6-terra"])[0],
        "by_model": concordance.get("by_model_column", {}),
        "dispute_overlap": concordance.get("dispute_overlap", {}),
        "per_cell": per_cell,
        "caption": ("Codex 5.6, one run, %d sampled comparisons, exploratory: "
                    "agreed %.1f%%" % (concordance.get("n_comparisons", 0),
                                       ov.get("concordance_pct", 0.0))),
    }


# ---------------------------------------------------------------------------
# Data assembly: per-task breakdown (the merged task explorer)
# ---------------------------------------------------------------------------

def _cell_runs(cell):
    """Ordered list of run records for a breakdown cell."""
    return [cell["runs"][rk] for rk in sorted(cell["runs"].keys())]


def _arm_rate(runs, arm):
    num = sum(r[arm + "_hits"] for r in runs)
    den = sum(r["n_must_hits"] for r in runs)
    return 100.0 * num / den if den else 0.0


def _cell_mean_hits(cell, arm):
    runs = _cell_runs(cell)
    if not runs:
        return None
    return sum(r[arm + "_hits"] for r in runs) / float(len(runs))


def build_tasks(breakdown, golden_rows, labels, warnings):
    """Assemble everything the per-task section renders, from the verified
    breakdown paired with the frozen golden suite by exact task id."""
    tmeta = breakdown["tasks_meta"]
    tdata = breakdown["tasks"]
    all_cells = breakdown["_meta"]["cells"]           # 16, includes fable@max
    populated = [c for c in all_cells
                 if tdata[next(iter(tdata))][c]["shape"] != "no_valid_data"]
    golden = {r["id"]: r for r in golden_rows}

    # order the model groups / efforts present in the breakdown
    def efforts_for(short):
        out = []
        for e in EFFORT_ORDER + ["none"]:
            if ("%s@%s" % (short, e)) in all_cells:
                out.append(e)
        return out

    # Non-confirmatory addendum cells (currently Fable at max): kept entirely
    # out of `cells` so the 15 confirmatory cells render byte-identically, and
    # attached per task under `extra_cells`. Badge/tooltip mirror the summary
    # addendum's locked copy. Only tasks the addendum actually scored get an
    # entry (mmar-t1 was excluded, so it gets none -- no stub).
    addenda = []
    for xc in breakdown.get("extra_cells", []):
        if xc.get("run_id") == "lattice-fable-max":
            badge, tip = LOCKED_COPY["badge"], LOCKED_COPY["hoverFull"]
        else:
            badge = "added later"
            tip = ("%s at %s was scored separately and is not one of the "
                   "confirmatory matrix cells." % (xc["model"], xc["effort"]))
        addenda.append({"cell": xc["cell"], "model": xc["model"],
                        "effort": xc["effort"], "badge": badge, "tip": tip,
                        "tasks": xc.get("tasks", {})})

    tasks = []
    for tid in tdata:
        meta = tmeta[tid]
        nmh = meta["n_must_hits"]
        lab = labels.get(tid, {})
        g = golden.get(tid)
        if g is None:
            warnings.append("%s: no golden-suite entry; prompt/checklist "
                            "omitted" % tid)
        # cross-check the label against the verified metric
        if lab.get("must_hits") not in (None, nmh):
            warnings.append("%s: label must-hits %s != verified n_must_hits %s"
                            % (tid, lab.get("must_hits"), nmh))

        all_runs = []
        for ck in populated:
            all_runs.extend(_cell_runs(tdata[tid][ck]))
        cold_pct = _arm_rate(all_runs, "cold")
        loaded_pct = _arm_rate(all_runs, "loaded")
        gap = loaded_pct - cold_pct
        n_runs = len(all_runs)
        perfect = all(r["loaded_hits"] == r["n_must_hits"] for r in all_runs)
        below = sum(1 for r in all_runs if r["loaded_hits"] < r["cold_hits"])
        if perfect:
            verdict, chip = "ok", ("loaded hit every item on all %d runs" % n_runs)
        elif below > 0:
            verdict, chip = "warn", ("skill scored lower than cold on %d of %d "
                                     "runs" % (below, n_runs))
        else:
            verdict, chip = "flat", "no clear lean either way across runs"

        # per-cell means (for the run grid change column, pip strips, deltas)
        cell_view = {}
        for ck in all_cells:
            cell = tdata[tid][ck]
            if cell["shape"] == "no_valid_data":
                cell_view[ck] = {"shape": "no_valid_data"}
                continue
            cold_mean = _cell_mean_hits(cell, "cold")
            load_mean = _cell_mean_hits(cell, "loaded")
            cell_view[ck] = {
                "shape": cell["shape"],
                "runs": _cell_runs(cell),
                "cold_mean": cold_mean,
                "load_mean": load_mean,
                "cold_pct": 100.0 * cold_mean / nmh,
                "load_pct": 100.0 * load_mean / nmh,
                "change_pp": (load_mean - cold_mean) / nmh * 100.0,
            }

        # Addendum cells for this task (currently Fable at max), built with the
        # same fields as a confirmatory single-run cell so the per-task grid can
        # render them without special-casing. Tasks the addendum did not score
        # (mmar-t1 was excluded) get no entry at all.
        extra_view = {}
        for ad in addenda:
            xt = ad["tasks"].get(tid)
            if xt is None or xt.get("shape") == "no_valid_data":
                continue
            xcold = _cell_mean_hits(xt, "cold")
            xload = _cell_mean_hits(xt, "loaded")
            extra_view[ad["cell"]] = {
                "shape": xt["shape"],
                "runs": _cell_runs(xt),
                "cold_mean": xcold,
                "load_mean": xload,
                "cold_pct": 100.0 * xcold / nmh,
                "load_pct": 100.0 * xload / nmh,
                "change_pp": (xload - xcold) / nmh * 100.0,
                "model": ad["model"],
                "effort": ad["effort"],
                "badge": ad["badge"],
                "tip": ad["tip"],
            }

        tasks.append({
            "id": tid,
            "title": lab.get("title", tid),
            "skill": meta["skill"],
            "fixture": meta["fixture"],
            "repo": lab.get("repo"),
            "n_must_hits": nmh,
            "must_hit_ids": meta.get("must_hit_ids", []),
            "must_hits": (g or {}).get("must_hits", []),
            "prompt": (g or {}).get("prompt", ""),
            "cold_pct": cold_pct,
            "loaded_pct": loaded_pct,
            "gap": gap,
            "n_runs": n_runs,
            "verdict": verdict,
            "chip": chip,
            "below": below,
            "cells": cell_view,
            "extra_cells": extra_view,
        })

    # default order: largest skill effect first
    tasks.sort(key=lambda t: t["gap"], reverse=True)

    n_loaded_perfect = sum(
        1 for t in tasks
        if all(r["loaded_hits"] == r["n_must_hits"]
               for ck in populated for r in _cell_runs(tdata[t["id"]][ck])))
    n_cold_perfect = sum(
        1 for t in tasks
        if all(r["cold_hits"] == r["n_must_hits"]
               for ck in populated for r in _cell_runs(tdata[t["id"]][ck])))
    total_runs = sum(t["n_runs"] for t in tasks)

    return {
        "order": [t["id"] for t in tasks],
        "by_id": {t["id"]: t for t in tasks},
        "list": tasks,
        "model_order": TASK_MODEL_ORDER,
        "efforts_for": {s: efforts_for(s) for s in TASK_MODEL_ORDER},
        "populated_cells": populated,
        "all_cells": all_cells,
        "n_tasks": len(tasks),
        "n_cells_with_data": len(populated),
        "total_runs": total_runs,
        "graded_answers": total_runs * 2,
        "n_loaded_perfect": n_loaded_perfect,
        "n_cold_perfect": n_cold_perfect,
        "metric_note": breakdown["_meta"]["metric"].get("n_must_hits", ""),
    }


def build_data(matrix, scanned, skipped, concordance, breakdown, golden_rows,
               labels, args, suite_hash, links_state):
    warnings, used = cross_check(matrix, scanned)
    open_cells, extras = find_open_and_extra(scanned, used)
    # An "extra" is a scored run dir outside the confirmatory matrix. Two kinds:
    # (1) a genuinely new model x effort condition the matrix never had (Fable
    # at max) -- render it as a clearly-marked addendum, separate from the 15;
    # (2) a re-scored / re-adjudicated view of a cell the matrix already carries
    # (its model@effort is a matrix key, e.g. the opus-medium batch1
    # re-adjudication) -- keep it off the page exactly as before. Never add
    # either kind to the matrix itself.
    extra_cells = []
    for ex in extras:
        key = "%s@%s" % (ex["model"], ex["effort"])
        known = ex["model"] != "unknown" and ex["effort"] != "unknown"
        if known and key not in matrix["cells"]:
            ex["is_addendum"] = True
            extra_cells.append(ex)
        else:
            warnings.append(
                "%s: scored data on disk but not a matrix cell; not displayed"
                % ex["run_id"])
    for d, reason in skipped:
        warnings.append("%s: skipped (%s)" % (d, reason))

    cells = {k: build_cell_display(k, c) for k, c in matrix["cells"].items()}

    models = [m for m in MODEL_ORDER
              if any(c["model"] == m for c in cells.values())]
    baselines = sorted({c["model"] for c in cells.values()
                        if c["effort"] == "none"})
    for m in sorted({c["model"] for c in cells.values()}):
        if m not in models and m not in baselines:
            models.append(m)

    judging = {
        "overall": matrix["judge_panel_overall"],
        "cells": {k: matrix["cells"][k]["judge_disagreement"]
                  for k in matrix["cell_order"]},
    }

    tasks = build_tasks(breakdown, golden_rows, labels, warnings)

    return {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
            .strftime("%Y-%m-%d %H:%M:%S UTC"),
        "regen_command": REGEN_COMMAND,
        "suite_hash": suite_hash,
        "links_state": links_state,
        "sources": {
            "matrix": args.matrix,
            "cells_pattern": args.cells,
            "cell_dirs_scanned": len(scanned),
            "concordance": args.concordance,
            "breakdown": args.breakdown,
            "golden": args.golden,
        },
        "cell_order": matrix["cell_order"],
        "cells": cells,
        "open_cells": open_cells,
        "extra_cells": extra_cells,
        "models": models,
        "baseline_models": baselines,
        "efforts": EFFORT_ORDER,
        "complete_case_tasks": matrix["complete_case_tasks"],
        "judging": judging,
        "concordance": build_concordance(concordance, cells),
        "tasks": tasks,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def cell_by(data, model, effort):
    for c in data["cells"].values():
        if c["model"] == model and c["effort"] == effort:
            return c
    return None


def open_cell_by(data, model, effort):
    for o in data["open_cells"]:
        if o["model"] == model and o["effort"] == effort:
            return o
    return None


def codex_chip(data, key):
    cx = data["concordance"]["per_cell"].get(key)
    if not cx:
        return '<span class="codex-chip not-sampled">Codex: not in the sample</span>'
    diff = cx["n_disagree"]
    cls = "codex-chip has-diff" if diff else "codex-chip"
    body = "Codex %d/%d agree" % (cx["n_agree"], cx["n_marks"])
    return '<span class="%s">%s</span>' % (cls, esc(body))


def sec_open(data, sid, title, teaser, is_open):
    # teaser is trusted template HTML (may contain entities like &middot;)
    return ('<details class="sec" id="%s"%s>\n'
            '<summary><h2 id="%s-h">%s</h2>'
            '<span class="teaser">%s</span></summary>\n'
            '<div class="sec-body">'
            % (sid, " open" if is_open else "", sid, esc(title), teaser))


def sec_close():
    return "</div>\n</details>\n"


# ---------------------------------------------------------------------------
# Section 1: results grid
# ---------------------------------------------------------------------------

def render_grid_cell(data, c):
    cls = "cell rep" if c["replicated"] else "cell"
    if c["replicated"]:
        badge = ('<span class="badge" title="mean of %d runs">&times;%d runs</span>'
                 % (c["repeats"], c["repeats"]))
    else:
        badge = ('<span class="badge one" title="one run, not a mean">'
                 'single run</span>')
    return (
        '<td class="%s">%s'
        '<span class="vals">'
        '<span class="v v-cold"><span class="sr">without skill </span><b>%s</b></span>'
        '<span class="v-arr" aria-hidden="true">&rarr;</span>'
        '<span class="v v-loaded"><span class="sr">with skill </span><b>%s</b></span>'
        '</span>'
        '<span class="v v-delta"><span class="sr">change </span><b>%s</b>'
        '<span class="pp"> pts</span></span>%s</td>'
        % (cls, badge, esc(fmt_pct(c["cold"])), esc(fmt_pct(c["loaded"])),
           esc(fmt_delta(c["delta"])), codex_chip(data, c["key"])))


def render_extra_cells(data):
    """Scored cells that sit outside the confirmatory matrix (currently the
    Fable-at-max addendum). Rendered as a clearly-labelled aside below the grid,
    never woven into the 15-cell table. Mirrors the grid's value idiom but
    carries its own 'added later' badge and a 'not part of the matrix' note."""
    extras = data.get("extra_cells") or []
    if not extras:
        return ""
    blocks = []
    for c in extras:
        if c["run_id"] == "lattice-fable-max":
            badge_txt, tip = LOCKED_COPY["badge"], LOCKED_COPY["hoverFull"]
        else:
            badge_txt = "added later"
            tip = ("%s at %s was scored separately and is not one of the "
                   "confirmatory matrix cells." % (c["model"], c["effort"]))
        runs = ("mean of %d repeat runs" % c["repeats"]) if c["replicated"] \
            else "single run"
        n_excl = len(c.get("excluded_tasks") or [])
        if n_excl:
            tasknote = (" &middot; %d of %d tasks (%s excluded)"
                        % (c["n_tasks"], c["n_tasks"] + n_excl,
                           ", ".join(esc(t) for t in c["excluded_tasks"])))
        else:
            tasknote = " &middot; %d tasks" % c["n_tasks"]
        blocks.append(
            '<div class="addendum">'
            '<div class="addendum-t">'
            '<span class="mdot" style="--c:%s"></span>'
            '<span class="addendum-cell"><b>%s</b> <span class="mut">at</span> '
            '%s</span>'
            '<span class="badge added" title="%s">%s</span>'
            '</div>'
            '<div class="addendum-vals">'
            '<span class="mut">without skill</span> <b>%s</b> '
            '<span class="v-arr" aria-hidden="true">&rarr;</span> '
            '<span class="mut">with skill</span> <b>%s</b> '
            '<span class="ad-delta">%s<span class="pp"> pts</span></span>'
            '</div>'
            '<div class="nlab">%s%s &middot; not part of the confirmatory '
            '15-cell matrix</div>'
            '</div>'
            % (model_color(c["model"]), esc(c["model"]), esc(c["effort"]),
               esc(tip), esc(badge_txt),
               esc(fmt_pct(c["cold"])), esc(fmt_pct(c["loaded"])),
               esc(fmt_delta(c["delta"])), runs, tasknote))
    return ('<div class="addendum-wrap" aria-label="Scored cells outside the '
            'confirmatory matrix">'
            '<div class="addendum-h">Addendum &middot; scored, but outside the '
            'confirmatory matrix</div>%s</div>' % "".join(blocks))


def render_matrix_section(data):
    efforts = data["efforts"]
    head = "".join('<th scope="col">%s</th>' % esc(e) for e in efforts)
    head += ('<th scope="col">no effort<span class="nlab">(reference)</span></th>')
    rows = []
    for model in data["models"] + data["baseline_models"]:
        is_baseline = model in data["baseline_models"]
        tag = ('<span class="nlab">%s</span>' % esc(BASELINE_LABEL)) \
            if is_baseline else ""
        dot = '<span class="mdot" style="--c:%s"></span>' % model_color(model)
        tds = []
        for effort in efforts:
            c = cell_by(data, model, effort)
            if c is not None:
                tds.append(render_grid_cell(data, c))
                continue
            o = open_cell_by(data, model, effort)
            if o is not None:
                tds.append(
                    '<td class="cell open">%s<span class="nlab">it got too '
                    'expensive to finish; one set of runs is still going, so '
                    'this box may fill in later</span></td>'
                    % esc(OPEN_CELL_LABEL))
            else:
                tds.append('<td class="cell empty" aria-label="no such '
                           'condition">-</td>')
        cb = cell_by(data, model, "none")
        tds.append(render_grid_cell(data, cb) if cb is not None
                   else '<td class="cell empty" aria-label="no such '
                        'condition">-</td>')
        rows.append('<tr class="%s"><th scope="row">%s%s%s</th>%s</tr>'
                    % ("baseline" if is_baseline else "", dot, esc(model), tag,
                       "".join(tds)))
    teaser = "skill off vs on, per cell"
    body = """
<div class="card">
<div class="toolbar" role="group" aria-label="controls">
  <span class="tlabel">show:</span>
  <button type="button" data-view="all" aria-pressed="true">all</button>
  <button type="button" data-view="cold" aria-pressed="false">without skill</button>
  <button type="button" data-view="loaded" aria-pressed="false">with skill</button>
  <button type="button" data-view="delta" aria-pressed="false">change</button>
  <span class="tsep"></span>
  <button type="button" id="codexbtn" class="toggle" aria-pressed="false">Codex cross-check: off</button>
  <noscript><span class="nlab">(toggles need JS; every value is shown below)</span></noscript>
</div>
<p class="caption">With the cross-check on, each box shows how many of its sampled
comparisons Codex agreed with. Full breakdown in section 5.</p>
<p class="cellkey">how to read each box: score <b>without the skill</b> &rarr;
<b>with it</b>, then the <b class="k-delta">change</b> in points underneath</p>
<div class="scroll"><table class="mx" id="mxtable">
<thead><tr><th scope="col">model \\ effort</th>%s</tr></thead>
<tbody>%s</tbody>
</table></div>
</div>
""" % (head, "".join(rows))
    return (sec_open(data, "matrix", "1. Skill effect across models and effort",
                     teaser, True) + body + render_extra_cells(data)
            + sec_close())


# ---------------------------------------------------------------------------
# Section 2: effort curves (static SVG, no JS required)
# ---------------------------------------------------------------------------

def _curve_frame(efforts, ymin):
    W, H = 380, 300
    ml, mr, mt, mb = 46, 16, 22, 62
    pw, ph = W - ml - mr, H - mt - mb

    def x(i):
        return ml + pw * (i / (len(efforts) - 1.0))

    def y(v):
        return mt + ph * (100.0 - v) / (100.0 - ymin)

    parts = []
    t = ymin
    while t <= 100:
        yy = y(t)
        parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" class="grid"/>'
                     % (ml, yy, W - mr, yy))
        parts.append('<text x="%d" y="%.1f" class="ax" text-anchor="end">%d</text>'
                     % (ml - 6, yy + 3.5, t))
        t += 5
    return W, H, ml, mr, mt, mb, x, y, parts


def render_curve_svg(data, model, ymin, color):
    efforts = data["efforts"]
    W, H, ml, mr, mt, mb, x, y, parts = _curve_frame(efforts, ymin)
    for i, e in enumerate(efforts):
        parts.append('<text x="%.1f" y="%d" class="ax" text-anchor="middle">%s</text>'
                     % (x(i), H - mb + 16, esc(e)))
    parts.append('<text x="%.1f" y="%d" class="axttl" text-anchor="middle">'
                 'effort level</text>' % (ml + (W - ml - mr) / 2.0, H - mb + 40))

    pts = []
    for i, e in enumerate(efforts):
        c = cell_by(data, model, e)
        if c is not None:
            pts.append((i, c))

    for arm, dash in (("cold", "5 4"), ("loaded", "")):
        if len(pts) >= 2:
            path = " ".join("%.1f,%.1f" % (x(i), y(c[arm])) for i, c in pts)
            da = (' stroke-dasharray="%s"' % dash) if dash else ""
            parts.append('<polyline points="%s" fill="none" stroke="%s" '
                         'stroke-width="2"%s/>' % (path, color, da))
        for i, c in pts:
            cx, cy = x(i), y(c[arm])
            arm_lbl = "with the skill" if arm == "loaded" else "without the skill"
            if c["replicated"]:
                vals = [r[arm] for r in c.get("per_repeat", [])]
                lo, hi = min(vals), max(vals)
                # vertical whisker across the run-to-run range
                parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                             'stroke="%s" stroke-width="1.6" opacity="0.4"/>'
                             % (cx, y(lo), cx, y(hi), color))
                # faint dots at the individual run values
                for v in vals:
                    parts.append('<circle cx="%.1f" cy="%.1f" r="1.7" '
                                 'fill="%s" opacity="0.35"/>' % (cx, y(v), color))
                tip = ("%s at %s: %s, mean %s, runs ranged %s to %s"
                       % (model, c["effort"], arm_lbl, fmt_pct(c[arm]),
                          fmt_pct(lo), fmt_pct(hi)))
                fill = color if arm == "loaded" else "var(--raised)"
                parts.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" '
                             'stroke="%s" stroke-width="2"><title>%s</title>'
                             '</circle>' % (cx, cy, fill, color, esc(tip)))
            else:
                tip = ("%s at %s: %s, single run %s"
                       % (model, c["effort"], arm_lbl, fmt_pct(c[arm])))
                fill = color if arm == "loaded" else "var(--raised)"
                parts.append('<circle cx="%.1f" cy="%.1f" r="3.6" fill="%s" '
                             'stroke="%s" stroke-width="1.8"><title>%s</title>'
                             '</circle>' % (cx, cy, fill, color, esc(tip)))

    for i, e in enumerate(efforts):
        o = open_cell_by(data, model, e)
        if o is not None:
            xx = x(i)
            anchor = "end" if xx > W - 70 else ("start" if xx < 70 else "middle")
            tx = xx - 4 if anchor == "end" else (xx + 4 if anchor == "start" else xx)
            parts.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" class="openline"/>'
                         % (xx, mt, xx, H - mb))
            parts.append('<text x="%.1f" y="%d" class="ax open" text-anchor="%s">'
                         'not finished</text>' % (tx, mt + 10, anchor))

    label = ("%s: checklist score against effort. Score runs %d to 100 on the "
             "vertical axis, effort low to max along the bottom. Solid line is "
             "with the skill, dashed is without; the vertical whisker at each "
             "point is the high-to-low range of its repeat runs. Exact values "
             "are in the grid above." % (model, ymin))
    return ('<svg viewBox="0 0 %d %d" role="img" aria-label="%s" '
            'preserveAspectRatio="xMidYMid meet">%s</svg>'
            % (W, H, esc(label), "".join(parts)))


def render_haiku_panel(data, model, ymin, color):
    """Dot-and-whisker reference panel for the no-effort-dial baseline."""
    c = cell_by(data, model, "none")
    if c is None:
        return ""
    efforts = ["one point"]
    W, H, ml, mr, mt, mb, x, y, parts = _curve_frame(efforts, ymin)
    cx = ml + (W - ml - mr) / 2.0
    parts.append('<text x="%.1f" y="%d" class="ax" text-anchor="middle">'
                 'no effort dial</text>' % (cx, H - mb + 16))
    y_cold, y_load = y(c["cold"]), y(c["loaded"])
    # thin connector between the two marks
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.4" opacity="0.6"/>'
                 % (cx, y_cold, cx, y_load, color))
    # open ring at without-skill, solid dot at with-skill
    parts.append('<circle cx="%.1f" cy="%.1f" r="5" fill="var(--raised)" '
                 'stroke="%s" stroke-width="2"><title>%s without the skill: %s '
                 '(single run)</title></circle>'
                 % (cx, y_cold, color, esc(model), esc(fmt_pct(c["cold"]))))
    parts.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="%s" '
                 'stroke-width="2"><title>%s with the skill: %s (single run)'
                 '</title></circle>'
                 % (cx, y_load, color, color, esc(model), esc(fmt_pct(c["loaded"]))))
    # value + arm labels beside each mark (number in ink, arm word muted)
    for yv, val, word in ((y_cold, c["cold"], "without the skill"),
                          (y_load, c["loaded"], "with the skill")):
        parts.append('<text x="%.1f" y="%.1f" text-anchor="start" '
                     'class="refmark"><tspan class="refnum">%s</tspan> '
                     '<tspan class="refarm">%s</tspan></text>'
                     % (cx + 12, yv + 4, esc(fmt_round_pct(val)), word))
    label = ("%s reference: without the skill %s, with the skill %s, one run, "
             "no effort setting." % (model, fmt_pct(c["cold"]),
                                     fmt_pct(c["loaded"])))
    return ('<svg viewBox="0 0 %d %d" role="img" aria-label="%s" '
            'preserveAspectRatio="xMidYMid meet">%s</svg>'
            % (W, H, esc(label), "".join(parts)))


def render_curves_section(data):
    vals = []
    for c in data["cells"].values():
        vals.extend([c["cold"], c["loaded"]])
        for r in c.get("per_repeat", []):
            vals.extend([r["cold"], r["loaded"]])
    ymin = int(min(vals) // 5 * 5) if vals else 75

    # Lay the four panels out in a fixed 2x2 order (Haiku, Sonnet, Opus, Fable).
    # Models with an effort dial draw a line chart; a no-effort baseline (Haiku)
    # draws a dot-and-whisker reference panel of the same size.
    by_short = {}
    for m in data["models"]:
        by_short[short_of(m)] = ("curve", m)
    for m in data["baseline_models"]:
        by_short[short_of(m)] = ("ref", m)
    charts = []
    for short in CURVES_ORDER:
        entry = by_short.get(short)
        if entry is None:
            continue
        kind, m = entry
        col = model_color(m)
        if kind == "curve":
            charts.append(
                '<figure class="card">'
                '<div class="card-t"><span class="mdot" style="--c:%s"></span>%s</div>'
                '<div class="card-s">checklist score against effort</div>'
                '%s</figure>'
                % (col, esc(m), render_curve_svg(data, m, ymin, col)))
        else:
            c = cell_by(data, m, "none")
            cap = ("%s &middot; one run, so there is no range across repeats."
                   % esc(m))
            charts.append(
                '<figure class="card haiku-panel">'
                '<div class="card-t"><span class="mdot" style="--c:%s"></span>%s</div>'
                '<div class="card-s">reference point, no effort dial</div>'
                '%s<div class="foot">%s</div></figure>'
                % (col, esc(m), render_haiku_panel(data, m, ymin, col), cap))

    ring = ('<svg width="26" height="16" viewBox="0 0 26 16" aria-hidden="true" '
            'class="lg-svg"><line x1="13" y1="2" x2="13" y2="14" '
            'stroke="var(--mut)" stroke-width="1.6" opacity="0.5"/>'
            '<circle cx="13" cy="8" r="3.4" fill="var(--raised)" '
            'stroke="var(--mut)" stroke-width="1.6"/></svg>')
    legend = (
        '<div class="legend curves-legend">'
        '<span class="lg-item"><span class="sw solid" style="--c:var(--acc)"></span>'
        'with skill</span>'
        '<span class="lg-item"><span class="sw dash" style="--c:var(--mut)"></span>'
        'without skill</span>'
        '<span class="lg-item">%s high and low across the 3 repeat runs '
        '(the line passes through the mean)</span></div>' % ring)

    teaser = "score vs effort, per model"
    body = """
<p class="lead">The same checklist scores drawn against effort. Each model has
its own colour. Haiku has no effort dial, so it sits in its own reference
panel.</p>
%s
<div class="charts">%s</div>
""" % (legend, "".join(charts))
    return (sec_open(data, "curves", "2. Effort curves per model", teaser, True)
            + body + sec_close())


# ---------------------------------------------------------------------------
# Section 3: task-by-task detail (merged task explorer)
# ---------------------------------------------------------------------------

def render_segbar(hits, nmh, arm, label, runlabel):
    segs = "".join('<i class="seg on"></i>' if i < hits else '<i class="seg"></i>'
                   for i in range(nmh))
    full = " full" if hits == nmh else ""
    rn = ('<span class="rn" aria-hidden="true">%s</span>' % esc(runlabel)) \
        if runlabel else ""
    return ('<span class="runcell%s" title="%s"><span class="bar %s">%s</span>%s'
            '<span class="sr">%s</span></span>'
            % (full, esc(label), arm, segs, rn, esc(label)))


def render_run_cell(cell, nmh, arm):
    arm_word = "with skill" if arm == "load" else "without skill"
    field = "loaded_hits" if arm == "load" else "cold_hits"
    single = cell["shape"] == "single"
    bars = []
    for idx, r in enumerate(cell["runs"], start=1):
        hits = r[field]
        if single:
            lab = "one run, %s: hit %d of %d must-hits" % (arm_word, hits, nmh)
        else:
            lab = "run %d, %s: hit %d of %d must-hits" % (idx, arm_word, hits, nmh)
        bars.append(render_segbar(hits, nmh, arm, lab, str(idx)))
    return ('<td class="arm %s"><span class="runrow">%s</span></td>'
            % (arm, "".join(bars)))


def render_run_grid(task):
    nmh = task["n_must_hits"]
    rows = []
    for short in TASK_MODEL_ORDER:
        full = SHORT2FULL[short]
        col = SERIES_COLORS[short]
        efforts = [e for e in EFFORT_ORDER + ["none"]
                   if ("%s@%s" % (short, e)) in task["cells"]]
        if not efforts:
            continue
        if short == "haiku":
            gh = ('<span class="mdot" style="--c:%s"></span>Haiku 4.5 '
                  '<span class="mut">&middot; no effort dial</span>' % col)
        else:
            gh = '<span class="mdot" style="--c:%s"></span>%s' % (col, esc(full))
        rows.append('<tr class="grow m-%s"><th scope="colgroup" colspan="4" '
                    'class="mcol">%s</th></tr>' % (short, gh))
        for e in efforts:
            ck = "%s@%s" % (short, e)
            cell = task["cells"][ck]
            elabel = "extra-high" if e == "xhigh" else e
            if cell["shape"] == "no_valid_data":
                # No confirmatory per-run data here (currently only fable@max).
                # If a non-confirmatory addendum scored this task, render its
                # real, badged box in the same slot; if it did not (mmar-t1 was
                # excluded), render nothing -- no stub.
                x = (task.get("extra_cells") or {}).get(ck)
                if x is not None:
                    xcp = x["change_pp"]
                    xdcls = ("up" if xcp > 0.5
                             else ("down" if xcp < -0.5 else "flat"))
                    xcond = ('%s<span class="badge added" title="%s">%s</span>'
                             % (esc(elabel), esc(x["tip"]), esc(x["badge"])))
                    rows.append(
                        '<tr class="crow m-%s"><td class="ecol">%s</td>%s%s'
                        '<td class="dcol %s">%s</td></tr>'
                        % (short, xcond, render_run_cell(x, nmh, "cold"),
                           render_run_cell(x, nmh, "load"), xdcls,
                           esc(fmt_signed_int(xcp))))
                continue
            change = fmt_signed_int(cell["change_pp"])
            cp = cell["change_pp"]
            dcls = "up" if cp > 0.5 else ("down" if cp < -0.5 else "flat")
            if short == "haiku":
                cond = ('<span class="mut">one run</span>'
                        '<span class="badge one">single run</span>')
            elif cell["shape"] == "single":
                cond = ('%s<span class="badge one">single run</span>'
                        % esc(elabel))
            else:
                cond = esc(elabel)
            rows.append(
                '<tr class="crow m-%s"><td class="ecol">%s</td>%s%s'
                '<td class="dcol %s">%s</td></tr>'
                % (short, cond, render_run_cell(cell, nmh, "cold"),
                   render_run_cell(cell, nmh, "load"), dcls, esc(change)))
    return (
        '<div class="grid-wrap"><div class="blk-h">Every individual run</div>'
        '<div class="scroll"><table class="rgrid">'
        '<thead><tr>'
        '<th scope="col" class="ecol">condition</th>'
        '<th scope="col" class="arm cold">without skill</th>'
        '<th scope="col" class="arm load">with skill</th>'
        '<th scope="col" class="dcol">change</th>'
        '</tr></thead><tbody>%s</tbody></table></div></div>'
        % "".join(rows))


def render_pip_strips(task):
    def strip(arm, label):
        pips = []
        first = True
        for short in TASK_MODEL_ORDER:
            efforts = [e for e in EFFORT_ORDER + ["none"]
                       if ("%s@%s" % (short, e)) in task["cells"]
                       and task["cells"]["%s@%s" % (short, e)]["shape"]
                       != "no_valid_data"]
            if not efforts:
                continue
            if not first:
                pips.append('<span class="pipgap"></span>')
            first = False
            col = SERIES_COLORS[short]
            for e in efforts:
                ck = "%s@%s" % (short, e)
                cell = task["cells"][ck]
                mean = cell[arm + "_mean"]
                cls = "pip-full" if abs(mean - task["n_must_hits"]) < 1e-9 else "pip-part"
                tip = "%s - %s skill mean %s/%d" % (
                    ck, "with" if arm == "load" else "without",
                    fmt_mean(mean), task["n_must_hits"])
                pips.append('<span class="pip %s m-%s" title="%s" '
                            'style="--mc:%s"></span>'
                            % (cls, short, esc(tip), col))
            # Addendum pip(s) for this model group (currently Fable at max):
            # same colour, appended inside the group so there is no gap before
            # it. Tasks the addendum did not score contribute nothing.
            for xk, x in (task.get("extra_cells") or {}).items():
                if x["model"] != short:
                    continue
                mean = x[arm + "_mean"]
                cls = ("pip-full"
                       if abs(mean - task["n_must_hits"]) < 1e-9 else "pip-part")
                tip = "%s - %s skill mean %s/%d (added later)" % (
                    xk, "with" if arm == "load" else "without",
                    fmt_mean(mean), task["n_must_hits"])
                pips.append('<span class="pip %s m-%s" title="%s" '
                            'style="--mc:%s"></span>'
                            % (cls, short, esc(tip), col))
        return ('<div class="striprow %s"><span class="strip-l">%s</span>'
                '<span class="strip">%s</span></div>'
                % (arm, label, "".join(pips)))
    return ('<div class="t-strips" aria-hidden="true">%s%s</div>'
            % (strip("cold", "without"), strip("load", "with")))


def render_cell_deltas(task):
    rows = []
    for short in TASK_MODEL_ORDER:
        for e in EFFORT_ORDER + ["none"]:
            ck = "%s@%s" % (short, e)
            cell = task["cells"].get(ck)
            if cell is None:
                continue
            if cell["shape"] == "no_valid_data":
                # Currently only fable@max. Show the real addendum averages
                # (badged) where the addendum scored the task; render nothing
                # where it did not (mmar-t1 was excluded).
                x = (task.get("extra_cells") or {}).get(ck)
                if x is not None:
                    xcp = x["change_pp"]
                    xdcls = ("up" if xcp > 0.5
                             else ("down" if xcp < -0.5 else "flat"))
                    rows.append(
                        '<tr><th scope="row">%s<span class="badge added" '
                        'title="%s">%s</span></th><td>%s</td>'
                        '<td class="hero">%s</td><td class="%s">%s</td></tr>'
                        % (esc(ck), esc(x["tip"]), esc(x["badge"]),
                           esc(fmt_pct(x["cold_pct"])),
                           esc(fmt_pct(x["load_pct"])), xdcls,
                           esc(fmt_signed_int(xcp))))
                continue
            cp = cell["change_pp"]
            dcls = "up" if cp > 0.5 else ("down" if cp < -0.5 else "flat")
            rows.append(
                '<tr><th scope="row">%s</th><td>%s</td>'
                '<td class="hero">%s</td><td class="%s">%s</td></tr>'
                % (esc(ck), esc(fmt_pct(cell["cold_pct"])),
                   esc(fmt_pct(cell["load_pct"])), dcls,
                   esc(fmt_signed_int(cp))))
    return (
        '<details class="celldeltas"><summary>Cell averages for this task'
        '</summary><p class="cd-note">change is in checklist points</p>'
        '<div class="scroll"><table class="cd">'
        '<thead><tr><th scope="col">condition</th>'
        '<th scope="col">without skill</th><th scope="col">with skill</th>'
        '<th scope="col">change</th></tr></thead><tbody>%s</tbody></table>'
        '</div></details>' % "".join(rows))


def render_task_card(task):
    nmh = task["n_must_hits"]
    repo = ("repo <code>%s</code> &middot; " % esc(task["repo"])) \
        if task.get("repo") else ""
    gapdir = "up" if task["gap"] > 0.5 else ("down" if task["gap"] < -0.5 else "flat")
    chip = '<span class="chip %s">%s</span>' % (task["verdict"], esc(task["chip"]))

    # must-hit checklist
    mh_items = []
    for it in task["must_hits"]:
        mh_items.append('<li><span class="mh-id">%s</span>'
                        '<span class="mh-tx">%s</span></li>'
                        % (esc_task(it.get("id", "")), esc_task(it.get("text", ""))))
    mh = ('<div class="mh"><div class="blk-h">Must-hit checklist &mdash; what a '
          'correct answer has to do</div><ol class="mh-list">%s</ol></div>'
          % "".join(mh_items))

    prompt = ('<details class="prompt"><summary>The prompt the model saw'
              '</summary><pre class="prompt-tx">%s</pre></details>'
              % esc_task(task["prompt"]))

    gl = task.get("github_links")
    if gl:
        file_links = "".join(
            '<li><a href="%s" target="_blank" rel="noopener">%s</a></li>'
            % (esc(f["url"]), esc(f["path"]))
            for f in gl.get("files", []) if f.get("verified_present"))
        links_html = ('<div class="fixture-links"><div class="blk-h">Browse this '
            'fixture on GitHub</div><p><a href="%s" target="_blank" rel="noopener">'
            'fixture root</a> &middot; <a href="%s" target="_blank" rel="noopener">'
            'generator script</a></p><ul class="file-links">%s</ul></div>'
            % (esc(gl["base_url"]), esc(gl["generator_script_url"]), file_links)) \
            if file_links else ""
    else:
        links_html = ""

    return """
<details class="task" id="%s" data-fixture="%s" data-gap="%.2f" data-title="%s" data-verdict="%s">
<summary>
  <div class="t-head">
    <div class="t-id">
      <span class="t-title">%s</span>
      <span class="t-meta"><code>%s</code> &middot; fixture <code>%s</code> &middot; %s%d must-hits</span>
    </div>
    <div class="t-score">
      <span class="sc"><span class="sc-l">without</span><b>%s</b></span>
      <span class="arrow" aria-hidden="true">&rarr;</span>
      <span class="sc"><span class="sc-l">with</span><b>%s</b></span>
      <span class="gap %s">%s pts</span>
      %s
    </div>
  </div>
  %s
</summary>
<div class="t-body">
  %s
  %s
  %s
  %s
  %s
</div>
</details>
""" % (esc(task["id"]), esc(task["fixture"]), task["gap"], esc(task["title"]),
       esc(task["verdict"]), esc(task["title"]), esc(task["id"]),
       esc(task["fixture"]), repo, nmh,
       esc(fmt_round_pct(task["cold_pct"])), esc(fmt_round_pct(task["loaded_pct"])),
       gapdir, esc(fmt_signed_int(task["gap"])), chip,
       render_pip_strips(task), mh, prompt, render_run_grid(task),
       render_cell_deltas(task), links_html)


def render_tasks_section(data):
    t = data["tasks"]
    tiles = """
<div class="tiles">
  <div class="tile"><b>%d</b><span>frozen tasks, one per skill</span></div>
  <div class="tile"><b>%d</b><span>model x effort cells with data</span></div>
  <div class="tile"><b>%s</b><span>individual runs behind these tasks</span></div>
  <div class="tile"><b>%s</b><span>graded answers, with the skill and without</span></div>
  <div class="tile"><b>%d / %d</b><span>tasks where the skill hit every item on every run</span></div>
  <div class="tile"><b>%d / %d</b><span>tasks where the baseline did the same</span></div>
</div>
""" % (t["n_tasks"], t["n_cells_with_data"], fmt_thousands(t["total_runs"]),
       fmt_thousands(t["graded_answers"]), t["n_loaded_perfect"], t["n_tasks"],
       t["n_cold_perfect"], t["n_tasks"])

    key = """
<div class="key">
<b>How to read.</b> Each task shows its score <b>without</b> the skill and
<b>with</b> it, then the change. Open one for its checklist and every run.
<div class="krow">
  <span class="ki"><span class="bar cold kbar"><i class="seg on"></i><i class="seg on"></i><i class="seg on"></i><i class="seg"></i></span> without skill</span>
  <span class="ki"><span class="bar load kbar"><i class="seg on"></i><i class="seg on"></i><i class="seg on"></i><i class="seg"></i></span> with skill</span>
  <span class="ki">filled = item hit, empty = missed</span>
</div>
<div class="krow">
  <span class="ki">whole row filled = every run hit every item, any empty = at least one run missed</span>
</div>
<div class="lgd-demo">
  <div class="lgd-labels">
    <span class="lgd-spacer"></span>
    <span class="lgd-grp" style="width:3.02rem">Fable</span>
    <span class="lgd-gap"></span>
    <span class="lgd-grp" style="width:3.82rem">Sonnet</span>
    <span class="lgd-gap"></span>
    <span class="lgd-grp" style="width:3.82rem">Opus</span>
    <span class="lgd-gap"></span>
    <span class="lgd-grp" style="width:.62rem">Haiku</span>
  </div>
  <div class="striprow cold"><span class="strip-l">without</span><span class="strip"><span class="pip pip-part m-fable" title="fable@low - without skill mean 3.7/4"></span><span class="pip pip-part m-fable" title="fable@medium - without skill mean 3/4"></span><span class="pip pip-full m-fable" title="fable@high - without skill mean 4/4"></span><span class="pip pip-full m-fable" title="fable@xhigh - without skill mean 4/4"></span><span class="pipgap"></span><span class="pip pip-part m-sonnet" title="sonnet@low - without skill mean 3/4"></span><span class="pip pip-part m-sonnet" title="sonnet@medium - without skill mean 3/4"></span><span class="pip pip-part m-sonnet" title="sonnet@high - without skill mean 3/4"></span><span class="pip pip-part m-sonnet" title="sonnet@xhigh - without skill mean 3/4"></span><span class="pip pip-part m-sonnet" title="sonnet@max - without skill mean 3/4"></span><span class="pipgap"></span><span class="pip pip-part m-opus" title="opus@low - without skill mean 3/4"></span><span class="pip pip-part m-opus" title="opus@medium - without skill mean 3.3/4"></span><span class="pip pip-part m-opus" title="opus@high - without skill mean 3.3/4"></span><span class="pip pip-part m-opus" title="opus@xhigh - without skill mean 3/4"></span><span class="pip pip-full m-opus" title="opus@max - without skill mean 4/4"></span><span class="pipgap"></span><span class="pip pip-part m-haiku" title="haiku@none - without skill mean 1/4"></span></span><span class="lgd-pct">3/15 &rarr; 81%</span></div>
  <div class="striprow load"><span class="strip-l">with</span><span class="strip"><span class="pip pip-full m-fable" title="fable@low - with skill mean 4/4"></span><span class="pip pip-full m-fable" title="fable@medium - with skill mean 4/4"></span><span class="pip pip-full m-fable" title="fable@high - with skill mean 4/4"></span><span class="pip pip-full m-fable" title="fable@xhigh - with skill mean 4/4"></span><span class="pipgap"></span><span class="pip pip-part m-sonnet" title="sonnet@low - with skill mean 3.7/4"></span><span class="pip pip-full m-sonnet" title="sonnet@medium - with skill mean 4/4"></span><span class="pip pip-part m-sonnet" title="sonnet@high - with skill mean 3.7/4"></span><span class="pip pip-full m-sonnet" title="sonnet@xhigh - with skill mean 4/4"></span><span class="pip pip-full m-sonnet" title="sonnet@max - with skill mean 4/4"></span><span class="pipgap"></span><span class="pip pip-part m-opus" title="opus@low - with skill mean 3.7/4"></span><span class="pip pip-full m-opus" title="opus@medium - with skill mean 4/4"></span><span class="pip pip-part m-opus" title="opus@high - with skill mean 3.7/4"></span><span class="pip pip-full m-opus" title="opus@xhigh - with skill mean 4/4"></span><span class="pip pip-full m-opus" title="opus@max - with skill mean 4/4"></span><span class="pipgap"></span><span class="pip pip-full m-haiku" title="haiku@none - with skill mean 4/4"></span></span><span class="lgd-pct">11/15 &rarr; 97%</span></div>
  <div class="lgd-cap"><span class="ki"><span class="pip pip-full"></span> filled = 100%, every run hit every must-hit</span> <span class="ki"><span class="pip pip-part"></span> outline = missed on at least one run</span></div>
  <div class="lgd-src">real example: &ldquo;Pre merge validation gate&rdquo;</div>
</div>
</div>
"""

    toolbar = """
<div class="toolbar" role="group" aria-label="controls">
  <span class="tlabel">sort:</span>
  <select id="sortsel" aria-label="Sort tasks">
    <option value="effect">skill effect</option>
    <option value="name">task name</option>
  </select>
  <button type="button" id="sortdir" data-dir="desc" aria-label="Toggle sort direction">largest first &darr;</button>
  <span class="tsep"></span>
  <span class="tlabel">model:</span>
  <button type="button" data-model="all" aria-pressed="true">all</button>
  <button type="button" data-model="fable">Fable</button>
  <button type="button" data-model="sonnet">Sonnet</button>
  <button type="button" data-model="opus">Opus</button>
  <span class="tsep"></span>
  <span class="tlabel">fixture:</span>
  <button type="button" data-fixture="all" aria-pressed="true">all</button>
  <button type="button" data-fixture="saasapp">saasapp</button>
  <button type="button" data-fixture="pipeline">pipeline</button>
  <button type="button" data-fixture="docsrepo">docsrepo</button>
  <span class="tsep"></span>
  <button type="button" id="expandall">expand all</button>
  <button type="button" id="collapseall">collapse all</button>
  <noscript><span class="tlabel">(controls need JS; every task and run is shown below without it)</span></noscript>
</div>
"""

    cards = "".join(render_task_card(t["by_id"][tid]) for tid in t["order"])
    teaser = "every run shown"
    body = """
<p class="lead">Every task the models saw, with every run behind the cell
averages in section 1.</p>
%s
%s
%s
<div class="tasks" id="taskgrid">%s</div>
""" % (tiles, key, toolbar, cards)
    return (sec_open(data, "tasks", "3. Task-by-task detail", teaser, False)
            + body + sec_close())


# ---------------------------------------------------------------------------
# Section 4: judging panel
# ---------------------------------------------------------------------------

def render_judging_section(data):
    ov = data["judging"]["overall"]
    adj = ov["adjudication"]
    tiles = """
<div class="tiles">
  <div class="tile"><b>%s</b><span>marks the two judges split on<br/>(%s of %s judged pairs)</span></div>
  <div class="tile"><b>%s</b><span>marks sent to the third judge<br/>(%s of %s judge calls, each pair is judged twice)</span></div>
  <div class="tile"><b>%d</b><span>left unresolved</span></div>
</div>
""" % (fmt_pct(ov["disagreement_rate_pct"]), fmt_thousands(ov["n_disagreed"]),
       fmt_thousands(ov["n_marks"]), fmt_pct(adj["adjudication_rate_pct"]),
       fmt_thousands(adj["n_adjudicated"]), fmt_thousands(adj["n_slot_marks"]),
       adj["n_unresolved"])
    rows = []
    for key in data["cell_order"]:
        jd = data["judging"]["cells"][key]
        a = jd["adjudication"]
        rows.append(
            '<tr><th scope="row">%s</th>'
            '<td>%d / %d<span class="q">%s</span></td>'
            '<td>%d / %d<span class="q">%s</span></td><td>%d</td></tr>'
            % (esc(key), jd["n_disagreed"], jd["n_marks"],
               fmt_pct(jd["disagreement_rate_pct"]), a["n_adjudicated"],
               a["n_slot_marks"], fmt_pct(a["adjudication_rate_pct"]),
               a["n_unresolved"]))
    teaser = "%s of marks split &middot; %d left unresolved" % (
        fmt_pct(ov["disagreement_rate_pct"]), adj["n_unresolved"])
    body = """
<p class="lead">Every blinded comparison was scored by two independent judges,
one Sonnet-class and one Opus-class. Where they split on a checklist mark, a
pinned third judge, Claude Fable 5, decided it, and the final mark is the
majority of the three. Disputed marks stay in every total.</p>
<div class="card">
%s
<div class="scroll"><table class="jd">
<thead><tr><th scope="col">condition</th><th scope="col">judges split</th>
<th scope="col">sent to third judge</th><th scope="col">unresolved</th></tr></thead>
<tbody>%s</tbody>
</table></div>
</div>
""" % (tiles, "".join(rows))
    return (sec_open(data, "judging", "4. How the scoring was judged", teaser,
                     False) + body + sec_close())


# ---------------------------------------------------------------------------
# Section 5: second-vendor spot-check (Codex)
# ---------------------------------------------------------------------------

def render_codex_section(data):
    cx = data["concordance"]
    by = cx["by_model"]
    cols = [("fable", "Fable"), ("sonnet", "Sonnet"), ("opus", "Opus"),
            ("haiku", "Haiku")]
    cells, head_parts = [], []
    for k, name in cols:
        b = by.get(k)
        if not b:
            continue
        head_parts.append('<th scope="col">%s</th>' % esc(name))
        cells.append('<td>%s<span class="q">%d/%d marks</span></td>'
                     % (fmt_pct(b["concordance_pct"]), b["n_agree"], b["n_marks"]))
    head = "".join(head_parts)
    do = cx["dispute_overlap"]
    tiles = """
<div class="tiles">
  <div class="tile"><b>%s</b><span>marks Codex agreed with<br/>(%d of %d)</span></div>
  <div class="tile"><b>%d</b><span>comparisons re-scored</span></div>
  <div class="tile"><b>%s</b><span>of the marks the Claude judges split on,<br/>Codex sided with the final call (%d of %d)</span></div>
</div>
""" % (fmt_pct(cx["overall_pct"]), cx["n_agree"], cx["n_marks"],
       cx["n_comparisons"], fmt_pct(do.get("concordance_pct", 0.0)),
       do.get("n_agree", 0), do.get("n_marks", 0))
    teaser = "agreement by model"
    body = """
<p class="lead">Codex 5.6 (%s) is the second-vendor model behind the %s
cross-check described at the top of the page.</p>
<div class="card">
%s
<div class="scroll"><table class="cx">
<thead><tr><th scope="col">agreement by model column</th>%s</tr></thead>
<tbody><tr><th scope="row">Codex vs final marks</th>%s</tr></tbody>
</table></div>
<div class="foot">Codex ran once at high reasoning effort; the %d comparisons
were drawn by a published hash rule.</div>
</div>
""" % (esc(cx["codex_model"]), fmt_pct(cx["overall_pct"]), tiles, head,
       "".join(cells), cx["n_comparisons"])
    return (sec_open(data, "codex", "5. Second-vendor spot-check (Codex 5.6)",
                     teaser, False) + body + sec_close())


# ---------------------------------------------------------------------------
# Section 6: provenance
# ---------------------------------------------------------------------------

def render_prov_section(data):
    s = data["sources"]
    notes = list(data["warnings"])
    gen_notes = [
        ("Six cells (Opus and Sonnet at medium, high, and extra-high) were "
         "first run once, then rerun fresh at 3 repeats; the earlier single "
         "runs live in results/_superseded and are not counted anywhere on "
         "this page. No cell has 4 counted runs."),
    ] + notes
    notes_html = "".join("<li>%s</li>" % esc(n) for n in gen_notes)
    teaser = "one build stamp &middot; sources listed"
    body = """
<div class="prov">
built %s from
<ul class="srclist">
<li><code>%s</code> (per-cell matrix aggregate)</li>
<li>%d run directories matching <code>%s</code> (per-cell cross-check)</li>
<li><code>%s</code> (verified per-task, per-run breakdown, all 16 cells)</li>
<li><code>%s</code> (frozen golden suite, suite hash <code>%s</code>)</li>
<li><code>%s</code> (second-vendor concordance)</li>
</ul>
Built by <code>eval/make_explorer.py</code> in the %s repo. Fixture and script
references are file paths; the materialized fixture tree is
<code>%s</code>, so task cards %s link out to the real files on GitHub.<br/>
rebuild with: <code>%s</code>
</div>
<div class="warn"><b>generation notes</b><ul>%s</ul></div>
""" % (esc(data["generated_utc"]), esc(s["matrix"]), s["cell_dirs_scanned"],
       esc(s["cells_pattern"]), esc(s["breakdown"]), esc(s["golden"]),
       esc(data["suite_hash"]), esc(s["concordance"]), esc(REPO_LABEL),
       esc(data["links_state"]),
       ("now" if data["links_state"] == "LIVE" else "do not yet"),
       esc(data["regen_command"]), notes_html)
    return (sec_open(data, "prov", "6. How this page was built", teaser, False)
            + body + sec_close())


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

CSS_BASE = """
:root{
--bg:#F6F5F1;--raised:#FFFFFF;--ink:#1B1B18;--mut:#6C6C64;
--line:#E6E3DC;--soft:#F0EEE7;--acc:#05705B;--hero:#FBF3EE;
--fable:#E8734A;--opus:#27A37A;--sonnet:#6C5CE0;--haiku:#8A94A0;
--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
--bg:#0F1216;--raised:#171C22;--ink:#E8EDF2;--mut:#98A2AE;
--line:#252C34;--soft:#1B2128;--acc:#2BD7AF;--hero:#1E2A2C;}}
:root[data-theme="dark"]{
--bg:#0F1216;--raised:#171C22;--ink:#E8EDF2;--mut:#98A2AE;
--line:#252C34;--soft:#1B2128;--acc:#2BD7AF;--hero:#1E2A2C;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
padding:0 1.2rem 4rem;max-width:1200px;margin-inline:auto}
h1{font-size:1.5rem;margin:0 0 .35rem;letter-spacing:-.01em}
h2{font-size:1.15rem;margin:0;letter-spacing:-.01em}
a{color:var(--acc);text-decoration:none}
code,.mono{font-family:var(--mono)}
.lead{color:var(--ink);font-size:.92rem;max-width:64rem;margin:.3rem 0 1rem}
.note{color:var(--mut);font-size:.85rem;max-width:64rem}
.mut{color:var(--mut)}
.caption{color:var(--ink);font-size:.82rem;background:var(--hero);
border:1px solid var(--line);border-radius:10px;padding:.55rem .8rem;
max-width:64rem;margin:.5rem 0}
.prov{border:1px solid var(--line);background:var(--raised);border-radius:12px;
padding:.8rem 1rem;font-size:.82rem;color:var(--mut)}
.prov code{color:var(--ink);font-size:.8rem;word-break:break-all}
.prov .srclist{margin:.4rem 0;padding-left:1.1rem}
.prov .srclist li{margin:.15rem 0}
.card{background:var(--raised);border:1px solid var(--line);border-radius:14px;
padding:1.1rem 1.15rem;margin:1rem 0}
.card-t{text-align:center;font-weight:600;font-size:1rem;margin:.1rem 0 .15rem}
.card-s{text-align:center;color:var(--mut);font-size:.8rem;margin:0 auto .8rem;
max-width:44rem}
.foot{color:var(--mut);font-size:.72rem;margin-top:.7rem;font-family:var(--mono);
line-height:1.5}
.mdot{display:inline-block;width:.6rem;height:.6rem;border-radius:50%;
background:var(--c);margin-right:.4rem;vertical-align:baseline}
.scroll{overflow-x:auto;margin:.5rem 0}
table{border-collapse:collapse;font-size:.82rem;min-width:100%}
th,td{padding:.5rem .6rem;text-align:left;vertical-align:top;
border-bottom:1px solid var(--line)}
.mx th,.mx td{border:1px solid var(--line)}
td{font-family:var(--mono);font-weight:400}
thead th{color:var(--mut);font-size:.74rem;font-weight:600;
border-bottom:1px solid var(--line)}
tbody th{color:var(--mut);font-size:.75rem;white-space:nowrap;font-weight:500}
td .q{display:block;color:var(--mut);font-size:.66rem;font-family:var(--mono);
margin-top:.1rem}
td.hero{background:var(--hero)}
.mx td.cell{min-width:8.4rem;position:relative}
.mx td.open{color:var(--mut);font-style:italic;font-size:.78rem}
.mx td.empty{color:var(--mut);text-align:center}
.mx tr.baseline th,.mx tr.baseline td{border-top:2px solid var(--line)}
.v{white-space:nowrap}
.vals{display:block;white-space:nowrap}
.v-cold,.v-loaded{display:inline}
.v-delta{display:block}
.v-arr{color:var(--mut);margin:0 .3rem;font-size:.8rem}
.v b{font-weight:600}
.v-delta .pp{color:var(--mut);font-size:.66rem;font-family:var(--mono)}
.sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;
clip:rect(0,0,0,0);white-space:nowrap;border:0}
#mxtable[data-view="all"] .v-delta{margin-top:.3rem;padding-top:.3rem;
border-top:1px solid var(--line)}
#mxtable[data-view="cold"] .v-arr,#mxtable[data-view="loaded"] .v-arr,
#mxtable[data-view="delta"] .v-arr{display:none}
.v-delta b{color:var(--acc);font-size:.98rem}
.badge{display:inline-block;color:var(--acc);border:1px solid var(--acc);
border-radius:999px;font-size:.6rem;line-height:1.5;padding:0 .42rem;
margin-bottom:.3rem;font-family:var(--mono);letter-spacing:.04em;opacity:.8}
.badge.one{color:var(--mut);border-color:var(--line);border-style:dashed;opacity:1}
.badge.added{color:var(--fable);border-color:var(--fable);border-style:solid;
opacity:1;margin-bottom:0;cursor:help}
.addendum-wrap{margin:.9rem 0 .2rem}
.addendum-h{font-family:var(--mono);font-size:.7rem;color:var(--mut);
text-transform:uppercase;letter-spacing:.05em;margin:.2rem 0 .5rem}
.addendum{background:var(--raised);border:1px solid var(--line);
border-left:3px solid var(--fable);border-radius:12px;padding:.75rem .95rem;
margin:.45rem 0}
.addendum-t{display:flex;align-items:center;gap:.5rem;flex-wrap:wrap}
.addendum-cell{font-size:.9rem}
.addendum-cell b{font-weight:600}
.addendum-vals{font-family:var(--mono);font-size:.88rem;margin-top:.4rem}
.addendum-vals b{font-weight:600}
.addendum-vals .ad-delta{color:var(--fable);font-weight:600}
.addendum-vals .pp{color:var(--mut);font-size:.66rem;font-weight:400}
.addendum .nlab{margin-top:.4rem}
.cellkey{font-family:var(--mono);font-size:.74rem;color:var(--mut);
margin:.1rem 0 .4rem}
.cellkey b{color:var(--ink);font-weight:600}
.cellkey .k-delta{color:var(--acc)}
.nlab{display:block;color:var(--mut);font-size:.66rem;margin-top:.2rem;
font-family:var(--mono)}
.codex-chip{display:none;margin-top:.35rem;border:1px dashed var(--sonnet);
color:var(--sonnet);border-radius:4px;font-size:.62rem;padding:.08rem .3rem;
font-family:var(--mono)}
.codex-chip.has-diff{border-style:solid;border-color:var(--acc);color:var(--acc)}
.codex-chip.not-sampled{border-style:dotted;border-color:var(--mut);color:var(--mut)}
#mxtable[data-codex="on"] .codex-chip{display:inline-block}
.toolbar{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin:.2rem 0 .6rem}
.tlabel{color:var(--mut);font-size:.78rem;font-family:var(--mono)}
.tsep{flex:0 0 1px;height:1.2rem;background:var(--line);margin:0 .3rem}
button{background:var(--soft);color:var(--ink);border:1px solid var(--line);
border-radius:7px;padding:.3rem .7rem;font-family:var(--mono);
font-size:.76rem;cursor:pointer}
button[aria-pressed="true"]{border-color:var(--acc);color:var(--acc);
background:var(--hero)}
button.toggle[aria-pressed="true"]{border-color:var(--sonnet);color:var(--sonnet)}
button:focus-visible,select:focus-visible,summary:focus-visible{
outline:2px solid var(--acc);outline-offset:2px}
select{background:var(--soft);color:var(--ink);border:1px solid var(--line);
border-radius:7px;padding:.3rem .5rem;font-family:var(--mono);font-size:.76rem;
max-width:100%}
#mxtable[data-view="cold"] .v:not(.v-cold){display:none}
#mxtable[data-view="loaded"] .v:not(.v-loaded){display:none}
#mxtable[data-view="delta"] .v:not(.v-delta){display:none}
.charts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
gap:1rem 1.1rem}
.charts figure{margin:0;min-width:0}
@media(max-width:640px){.charts{grid-template-columns:1fr}}
svg{width:100%;height:auto;display:block}
svg .grid{stroke:var(--line);stroke-width:1}
svg .ax{fill:var(--mut);font-family:var(--mono);font-size:11px}
svg .ax.open{fill:var(--mut);font-style:italic;font-size:10px}
svg .axttl{fill:var(--mut);font-family:var(--mono);font-size:11px}
svg .openline{stroke:var(--mut);stroke-dasharray:3 4;stroke-width:1}
svg .refmark{font-family:var(--mono)}
svg .refnum{fill:var(--ink);font-size:12px;font-weight:600}
svg .refarm{fill:var(--mut);font-size:10px}
.legend{display:flex;gap:1.1rem;justify-content:center;flex-wrap:wrap;
margin:0 0 .3rem;font-size:.74rem;color:var(--mut);font-family:var(--mono)}
.curves-legend{background:var(--hero);border:1px solid var(--line);
border-radius:10px;padding:.5rem .7rem;margin:.2rem 0 1rem}
.lg-item{display:inline-flex;align-items:center;gap:.35rem}
.lg-svg{vertical-align:middle;width:26px;height:16px;flex:0 0 auto}
.sw{display:inline-block;width:20px;height:0;border-top:2px solid var(--c)}
.sw.dash{border-top-style:dashed}
.tiles{display:flex;gap:.8rem;flex-wrap:wrap;margin:.4rem 0 1rem}
.tile{background:var(--soft);border:1px solid var(--line);border-radius:12px;
padding:.85rem 1.1rem;min-width:11rem;flex:1 1 11rem}
.tile b{display:block;font-size:1.6rem;font-family:var(--mono);
color:var(--acc);font-weight:600;line-height:1.15}
.tile span{color:var(--mut);font-size:.72rem;font-family:var(--mono)}
.warn{border:1px solid var(--line);background:var(--raised);border-radius:10px;
padding:.6rem .9rem;color:var(--mut);font-size:.78rem;font-family:var(--mono)}
footer{margin-top:3rem;color:var(--mut);font-size:.78rem;
border-top:1px solid var(--line);padding-top:1rem}
footer a{color:var(--acc)}
.hide{display:none !important}
"""

CSS_NAV = """
nav.site-nav{position:sticky;top:0;z-index:60;display:flex;align-items:center;
gap:20px;padding:13px 0;background:var(--bg);
border-bottom:1px solid var(--line);flex-wrap:wrap;margin:0 0 1.4rem;
border-radius:0}
nav.site-nav .brand{font-family:var(--mono);font-size:14px;color:var(--ink)}
nav.site-nav .brand b{color:var(--acc);font-weight:600}
nav.site-nav .brand-lab{font-family:var(--mono);font-size:14px;color:var(--mut);
margin-left:-12px}
nav.site-nav .brand-lab:hover{color:var(--acc)}
nav.site-nav .nav-right{margin-left:auto;display:flex;align-items:center;
gap:16px;flex-wrap:wrap}
nav.site-nav .lab-nav{display:flex;gap:14px;flex-wrap:wrap}
nav.site-nav .lab-nav a{font-family:var(--mono);font-size:12px;color:var(--mut);
padding:4px 2px;border-bottom:1px solid transparent}
nav.site-nav .lab-nav a:hover{color:var(--acc)}
nav.site-nav .lab-nav a[aria-current="page"]{color:var(--ink);
border-bottom-color:var(--acc)}
nav.site-nav .theme-toggle{display:flex;border:1px solid var(--line);
border-radius:0}
nav.site-nav .theme-toggle button{background:none;border:none;
border-right:1px solid var(--line);color:var(--mut);font-size:13px;
line-height:1;padding:7px 10px;cursor:pointer;border-radius:0;
transition:color .15s,background .15s}
nav.site-nav .theme-toggle button:last-child{border-right:none}
nav.site-nav .theme-toggle button:hover{color:var(--ink)}
nav.site-nav .theme-toggle button[aria-pressed="true"]{background:var(--acc);
color:#FFFFFF}
/* section-jump bar */
.jumpbar{position:sticky;top:49px;z-index:50;display:flex;gap:14px;flex-wrap:wrap;
align-items:center;padding:9px 0;margin:0 0 1.4rem;background:var(--bg);
border-bottom:1px solid var(--line)}
.jumpbar .jlabel{font-family:var(--mono);font-size:11px;color:var(--mut);
text-transform:uppercase;letter-spacing:.05em}
.jumpbar a{font-family:var(--mono);font-size:12px;color:var(--mut);
text-decoration:none;padding:2px 2px;border-bottom:1px solid transparent}
.jumpbar a:hover{color:var(--acc);border-bottom-color:var(--acc)}
@media(max-width:640px){
nav.site-nav{position:static;gap:8px 14px;padding-top:11px;padding-bottom:11px}
nav.site-nav .nav-right{gap:8px 12px}
nav.site-nav .lab-nav{gap:6px 12px}
.jumpbar{position:static}
body{padding:0 .8rem 3rem}
}
"""

CSS_SEC = """
/* collapsible section accordions */
details.sec{border:none;background:none;margin:0 0 .4rem;border-radius:0}
details.sec>summary{cursor:pointer;list-style:none;display:flex;align-items:baseline;
gap:.8rem;flex-wrap:wrap;padding:.9rem 0 .3rem;margin:1.8rem 0 0;
border-bottom:1px solid var(--line)}
details.sec:first-of-type>summary{margin-top:.4rem}
details.sec>summary::-webkit-details-marker{display:none}
details.sec>summary::before{content:"\\25B8";color:var(--mut);font-size:.8rem;
transition:transform .12s}
details.sec[open]>summary::before{transform:rotate(90deg);display:inline-block}
details.sec[open]>summary{color:inherit}
details.sec>summary:hover h2{color:var(--acc)}
.teaser{color:var(--mut);font-size:.75rem;font-family:var(--mono);margin-left:auto}
.sec-body{padding:.2rem 0 .6rem}

/* how-to-read key */
.key{background:var(--hero);border:1px solid var(--line);border-radius:12px;
padding:.7rem .95rem;margin:.8rem 0 1rem;font-size:.82rem;color:var(--ink);
max-width:66rem}
.key b{font-weight:600}
.key .krow{display:flex;gap:1.3rem;flex-wrap:wrap;margin-top:.5rem;
align-items:center;color:var(--mut);font-family:var(--mono);font-size:.76rem}
.key .ki{display:inline-flex;align-items:center;gap:.4rem}
.kbar{transform:scale(.85);transform-origin:left center}

/* one-time page primer: the shared facts, stated once */
.primer{background:var(--hero);border:1px solid var(--line);border-radius:12px;
  padding:1rem 1.15rem;margin:.4rem 0 1.6rem;max-width:66rem}
.primer .primer-h{font-family:var(--mono);font-size:.7rem;color:var(--mut);
  text-transform:uppercase;letter-spacing:.05em;margin:0 0 .45rem}
.primer .intro{color:var(--ink);font-size:.9rem;margin:0 0 .75rem;max-width:64rem}
.primer dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:.5rem .9rem}
.primer dt{color:var(--ink);font-weight:600;font-size:.82rem;white-space:nowrap}
.primer dd{margin:0;color:var(--mut);font-size:.82rem;line-height:1.5}
.primer dd b{color:var(--ink);font-weight:600}
@media(max-width:640px){
  .primer dl{grid-template-columns:1fr;gap:.15rem .9rem}
  .primer dt{margin-top:.55rem}
}

/* pip strips */
.pip{display:inline-block;width:.62rem;height:.62rem;border-radius:2px;
vertical-align:middle}
.pip-full{background:var(--acc)}
.pip-part{background:transparent;box-shadow:inset 0 0 0 1.5px var(--acc)}
/* without-skill strip reads neutral, with-skill strip reads accent */
.striprow.cold .pip-full{background:var(--mut)}
.striprow.cold .pip-part{box-shadow:inset 0 0 0 1.5px var(--mut)}
.pipgap{display:inline-block;width:.42rem}
.strip{display:inline-flex;gap:.18rem;align-items:center;flex-wrap:wrap}

/* task cards */
details.task{background:var(--raised);border:1px solid var(--line);
border-radius:14px;margin:1.3rem 0;overflow:hidden}
details.task>summary{cursor:pointer;list-style:none;padding:.9rem 1.05rem;
display:block}
details.task>summary::-webkit-details-marker{display:none}
details.task>summary:hover{background:var(--hero)}
details.task[open]>summary{border-bottom:1px solid var(--line)}
.t-head{display:flex;gap:1rem;align-items:flex-start;justify-content:space-between;
flex-wrap:wrap}
.t-title{font-weight:600;font-size:1.02rem;color:var(--ink);
letter-spacing:-.01em;display:block}
.t-meta{display:block;color:var(--mut);font-size:.74rem;font-family:var(--mono);
margin-top:.2rem}
.t-meta code{color:var(--ink)}
.t-score{display:flex;align-items:center;gap:.55rem;flex-wrap:wrap;
margin-left:auto}
.t-score .sc{display:inline-flex;flex-direction:column;align-items:center;
line-height:1.05}
.t-score .sc-l{color:var(--mut);font-size:.6rem;font-family:var(--mono);
text-transform:uppercase;letter-spacing:.04em}
.t-score .sc b{font-family:var(--mono);font-size:1.05rem;color:var(--ink)}
.t-score .arrow{color:var(--mut)}
.gap{font-family:var(--mono);font-size:.78rem;border:1px solid var(--line);
border-radius:999px;padding:.05rem .5rem}
.gap.up{color:var(--acc);border-color:var(--acc)}
.gap.down{color:var(--fable);border-color:var(--fable)}
.gap.flat{color:var(--mut)}
.chip{font-family:var(--mono);font-size:.66rem;border-radius:999px;
padding:.12rem .55rem;border:1px solid var(--line);white-space:nowrap}
.chip.ok{color:var(--acc);border-color:var(--acc)}
.chip.warn{color:var(--fable);border-color:var(--fable)}
.chip.flat{color:var(--mut)}
.t-strips{margin-top:.7rem;display:flex;flex-direction:column;gap:.28rem}
.striprow{display:flex;align-items:center;gap:.6rem}
.strip-l{color:var(--mut);font-size:.64rem;font-family:var(--mono);width:3.4rem;
text-align:right;text-transform:uppercase;letter-spacing:.03em}

/* legend demo strip: same pip/gap geometry as .strip, with model labels on top */
.lgd-demo{margin:.6rem 0 .3rem}
.lgd-demo .striprow{margin:.15rem 0;flex-wrap:wrap}
.lgd-labels{display:flex;align-items:flex-end;margin-bottom:.2rem}
.lgd-spacer{display:inline-block;width:3.4rem;flex:none;margin-right:.6rem}
.lgd-grp{font-family:var(--mono);font-size:.58rem;color:var(--mut);
text-align:center;letter-spacing:.02em;flex:none;margin-right:.18rem}
.lgd-gap{display:inline-block;width:.42rem;flex:none;margin-right:.18rem}
.lgd-cap{margin-top:.35rem;display:flex;gap:1.2rem;flex-wrap:wrap}
.lgd-src{margin-top:.3rem;font-family:var(--mono);font-size:.6rem;color:var(--faint)}
.lgd-pct{font-family:var(--mono);font-size:.64rem;color:var(--mut);white-space:nowrap}
@media(max-width:640px){ .lgd-spacer{width:2.6rem} .lgd-pct{flex-basis:100%} }

/* task body */
.t-body{padding:.5rem 1.05rem 1.1rem}
.blk-h{font-size:.7rem;font-family:var(--mono);color:var(--mut);
text-transform:uppercase;letter-spacing:.05em;margin:.9rem 0 .4rem}
.mh-list{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;
gap:.5rem}
.mh-list li{display:flex;gap:.6rem;align-items:flex-start;font-size:.85rem;
color:var(--ink);max-width:74rem}
.mh-id{flex:0 0 auto;width:1.35rem;height:1.35rem;border-radius:50%;
border:1px solid var(--line);color:var(--acc);font-family:var(--mono);
font-size:.72rem;display:inline-flex;align-items:center;justify-content:center;
margin-top:.05rem}
.mh-tx{flex:1 1 auto}
details.prompt{border:1px solid var(--line);border-radius:10px;margin:.4rem 0 0;
background:var(--bg)}
details.prompt>summary{cursor:pointer;padding:.5rem .8rem;font-family:var(--mono);
font-size:.8rem;color:var(--mut)}
details.prompt[open]>summary{border-bottom:1px solid var(--line);color:var(--acc)}
.prompt-tx{margin:0;padding:.8rem .95rem;white-space:pre-wrap;word-wrap:break-word;
font-family:var(--mono);font-size:.8rem;line-height:1.55;color:var(--ink)}

/* run grid: segmented mini-bars */
table.rgrid{border-collapse:collapse;font-size:.8rem;min-width:100%}
table.rgrid th,table.rgrid td{padding:.6rem .85rem;text-align:left;
border-bottom:1px solid var(--line);vertical-align:middle}
table.rgrid thead th{color:var(--mut);font-size:.68rem;font-family:var(--mono);
font-weight:600;text-transform:uppercase;letter-spacing:.03em}
/* separate the without / with arms with a faint rule */
table.rgrid .arm.load{border-left:1px solid var(--line)}
/* containing block for .sr children, same as .mx td.cell */
table.rgrid td.arm{position:relative}
.rgrid tr.grow th{background:var(--soft);font-family:var(--mono);color:var(--ink);
font-size:.76rem;font-weight:600;padding-top:.75rem;padding-bottom:.75rem;border-top:2px solid var(--line)}
.rgrid tr.grow.m-sonnet th,.rgrid tr.grow.m-haiku th{background:var(--soft)}
.rgrid .ecol{font-family:var(--mono);color:var(--mut);font-size:.75rem;
white-space:nowrap}
.rgrid .ecol .badge.one{margin-left:.4rem;margin-bottom:0}
.rgrid .ecol .badge.added{margin-left:.4rem}
.rgrid .stub{color:var(--mut);font-style:italic;font-family:var(--mono);
font-size:.75rem}
.runrow{display:inline-flex;gap:1.15rem;align-items:flex-start}
.runcell{display:inline-flex;flex-direction:column;align-items:center;gap:5px}
.bar{display:inline-flex;gap:3px;align-items:center}
.seg{width:10px;height:24px;border:1px solid var(--line);border-radius:2px;
box-sizing:border-box;background:var(--soft)}
.bar.cold .seg.on{background:var(--mut);border-color:var(--mut)}
.bar.load .seg.on{background:var(--acc);border-color:var(--acc)}
.runcell.full .bar{box-shadow:0 2px 0 -1px var(--acc)}
.runcell.full .bar.cold{box-shadow:0 2px 0 -1px var(--mut)}
.rn{font-size:.58rem;line-height:1;color:var(--mut);font-family:var(--mono)}
.dcol{font-family:var(--mono);font-size:.78rem;white-space:nowrap}
.dcol.up{color:var(--acc)}
.dcol.down{color:var(--fable)}
.dcol.flat{color:var(--mut)}
/* zebra by model group */
.rgrid tbody tr.crow.m-sonnet td,.rgrid tbody tr.crow.m-sonnet th,
.rgrid tbody tr.crow.m-haiku td,.rgrid tbody tr.crow.m-haiku th{
background:color-mix(in srgb,var(--soft) 45%,transparent)}

/* cell-averages sub-table */
details.celldeltas{border:1px solid var(--line);border-radius:10px;
margin:.7rem 0 0;background:var(--bg)}
details.celldeltas>summary{cursor:pointer;padding:.5rem .8rem;
font-family:var(--mono);font-size:.8rem;color:var(--mut)}
details.celldeltas[open]>summary{border-bottom:1px solid var(--line);
color:var(--acc)}
.cd-note{color:var(--mut);font-size:.72rem;font-family:var(--mono);
margin:.5rem .8rem 0}
table.cd{font-size:.78rem}
table.cd .up{color:var(--acc)}
table.cd .down{color:var(--fable)}
table.cd .flat{color:var(--mut)}

/* model filter */
.tasks[data-model="fable"] .crow:not(.m-fable),
.tasks[data-model="fable"] .grow:not(.m-fable),
.tasks[data-model="sonnet"] .crow:not(.m-sonnet),
.tasks[data-model="sonnet"] .grow:not(.m-sonnet),
.tasks[data-model="opus"] .crow:not(.m-opus),
.tasks[data-model="opus"] .grow:not(.m-opus){display:none}
.tasks[data-model="fable"] .pip:not(.m-fable),
.tasks[data-model="fable"] .pipgap,
.tasks[data-model="sonnet"] .pip:not(.m-sonnet),
.tasks[data-model="sonnet"] .pipgap,
.tasks[data-model="opus"] .pip:not(.m-opus),
.tasks[data-model="opus"] .pipgap{display:none}
@media(max-width:640px){
.t-score{margin-left:0}
.strip-l{width:2.6rem}
}
"""

JS = """
(function () {
  var table = document.getElementById('mxtable');
  var buttons = document.querySelectorAll('.toolbar button[data-view]');
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      buttons.forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
      b.setAttribute('aria-pressed', 'true');
      if (b.dataset.view === 'all') { table.removeAttribute('data-view'); }
      else { table.setAttribute('data-view', b.dataset.view); }
    });
  });
  var codex = document.getElementById('codexbtn');
  if (codex) {
    codex.addEventListener('click', function () {
      var on = table.getAttribute('data-codex') === 'on';
      if (on) { table.removeAttribute('data-codex'); }
      else { table.setAttribute('data-codex', 'on'); }
      codex.setAttribute('aria-pressed', on ? 'false' : 'true');
      codex.textContent = 'Codex cross-check: ' + (on ? 'off' : 'on');
    });
  }

  /* task explorer: sort / filter / expand */
  var wrap = document.getElementById('taskgrid');
  if (wrap) {
    var sortSel = document.getElementById('sortsel');
    var sortDir = document.getElementById('sortdir');
    function dirLabel(mode, dir) {
      if (mode === 'name') { return dir === 'asc' ? 'A \\u2192 Z' : 'Z \\u2192 A'; }
      return dir === 'desc' ? 'largest first \\u2193' : 'smallest first \\u2191';
    }
    function reorder() {
      var mode = sortSel ? sortSel.value : 'effect';
      var dir = sortDir ? sortDir.dataset.dir : 'desc';
      var cards = Array.prototype.slice.call(wrap.querySelectorAll('details.task'));
      cards.sort(function (a, b) {
        var r = (mode === 'name')
          ? a.dataset.title.localeCompare(b.dataset.title)
          : parseFloat(a.dataset.gap) - parseFloat(b.dataset.gap);
        return dir === 'asc' ? r : -r;
      });
      cards.forEach(function (c) { wrap.appendChild(c); });
      if (sortDir) { sortDir.textContent = dirLabel(mode, dir); }
    }
    if (sortSel) { sortSel.addEventListener('change', function () {
      if (sortDir) { sortDir.dataset.dir = (sortSel.value === 'name') ? 'asc' : 'desc'; }
      reorder();
    }); }
    if (sortDir) { sortDir.addEventListener('click', function () {
      sortDir.dataset.dir = (sortDir.dataset.dir === 'asc') ? 'desc' : 'asc';
      reorder();
    }); }
    var mbtns = document.querySelectorAll('button[data-model]');
    mbtns.forEach(function (b) { b.addEventListener('click', function () {
      mbtns.forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
      b.setAttribute('aria-pressed', 'true');
      if (b.dataset.model === 'all') { wrap.removeAttribute('data-model'); }
      else { wrap.setAttribute('data-model', b.dataset.model); }
    }); });
    var fbtns = document.querySelectorAll('button[data-fixture]');
    fbtns.forEach(function (b) { b.addEventListener('click', function () {
      fbtns.forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
      b.setAttribute('aria-pressed', 'true');
      var f = b.dataset.fixture;
      wrap.querySelectorAll('details.task').forEach(function (c) {
        c.classList.toggle('hide', !(f === 'all' || c.dataset.fixture === f));
      });
    }); });
    var ex = document.getElementById('expandall'), co = document.getElementById('collapseall');
    if (ex) { ex.addEventListener('click', function () {
      wrap.querySelectorAll('details.task').forEach(function (c) { if (!c.classList.contains('hide')) c.open = true; }); }); }
    if (co) { co.addEventListener('click', function () {
      wrap.querySelectorAll('details.task').forEach(function (c) { c.open = false; }); }); }
  }

  /* accordion section state, persisted per section id */
  var SECKEY = 'hamz-lattice-sections';
  var secs = Array.prototype.slice.call(document.querySelectorAll('details.sec'));
  function loadSec() { try { return JSON.parse(localStorage.getItem(SECKEY)) || {}; } catch (e) { return {}; } }
  function saveSec() { var o = {}; secs.forEach(function (s) { o[s.id] = s.open; });
    try { localStorage.setItem(SECKEY, JSON.stringify(o)); } catch (e) {} }
  var st = loadSec();
  secs.forEach(function (s) {
    if (Object.prototype.hasOwnProperty.call(st, s.id)) { s.open = st[s.id]; }
    s.addEventListener('toggle', saveSec);
  });

  /* deep links: open every ancestor details element of the target, then scroll */
  function openTo(hash) {
    if (!hash || hash.charAt(0) !== '#' || hash.length < 2) { return; }
    var el;
    try { el = document.querySelector(hash); } catch (e) { return; }
    if (!el) { return; }
    var p = el.closest('details');
    while (p) { p.open = true; p = p.parentElement ? p.parentElement.closest('details') : null; }
    el.scrollIntoView();
  }
  window.addEventListener('hashchange', function () { openTo(location.hash); });
  if (location.hash) { openTo(location.hash); }

  /* theme toggle */
  var root = document.documentElement;
  var tbtns = Array.prototype.slice.call(document.querySelectorAll('.theme-toggle button'));
  function curTheme() { try { return localStorage.getItem('hamz-theme') || 'system'; } catch (e) { return 'system'; } }
  function paintTheme(v) { tbtns.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.themeSet === v ? 'true' : 'false'); }); }
  function applyTheme(v) {
    if (v === 'light' || v === 'dark') { root.setAttribute('data-theme', v); }
    else { root.removeAttribute('data-theme'); }
    try { localStorage.setItem('hamz-theme', v); } catch (e) {}
    paintTheme(v);
  }
  tbtns.forEach(function (b) { b.addEventListener('click', function () { applyTheme(b.dataset.themeSet); }); });
  paintTheme(curTheme());
})();
"""

NAV_HTML = """
<nav class="site-nav" aria-label="Lab">
  <a class="brand" href="https://www.hamz.ai"><b>hamz</b>.ai</a>
  <a class="brand-lab" href="../../">/ lab</a>
  <div class="nav-right">
    <div class="lab-nav">
      <a href="../">Lattice</a>
      <a href="../../skills/">Skills</a>
      <a href="../../evidence/">The skills study</a>
      <a href="../../learn/">Learn</a>
      <a href="../../chain/">Chain</a>
      <a href="../../notes/">Notes</a>
      <a href="../../../builder/">Builder</a>
    </div>
    <div class="theme-toggle" role="group" aria-label="Colour theme">
      <button type="button" data-theme-set="system" aria-pressed="true"  title="Match system" aria-label="System theme">&#9680;</button>
      <button type="button" data-theme-set="light"  aria-pressed="false" title="Light"        aria-label="Light theme">&#9728;</button>
      <button type="button" data-theme-set="dark"   aria-pressed="false" title="Dark"         aria-label="Dark theme">&#9790;</button>
    </div>
  </div>
</nav>
"""

JUMPBAR_HTML = """
<nav class="jumpbar" aria-label="Sections">
  <span class="jlabel">jump to</span>
  <a href="#matrix">Matrix</a>
  <a href="#curves">Curves</a>
  <a href="#tasks">Tasks</a>
  <a href="#judging">Judging</a>
  <a href="#codex">Codex</a>
  <a href="#prov">Provenance</a>
</nav>
"""

PRIMER_HTML = """
<section class="primer" aria-label="How to read this page">
<div class="primer-h">How to read this page</div>
<p class="intro">Every number here is read straight from the committed result files at build time; the template only adds labels. Read each rate as a rough signal, not a precise measurement: these are small samples.</p>
<dl>
  <dt>The %d tasks</dt>
  <dd>Every populated cell, curve, and panel is scored on the same tasks, the ones valid in every condition. That shared set is the only clean basis for comparing across boxes.</dd>
  <dt>%d conditions</dt>
  <dd>Fable, Sonnet, and Opus across five effort levels, plus Haiku once for reference. %d of those cells make up the confirmatory matrix; Fable at max finished later and ships as an addendum outside it, marked <b>added later</b>.</dd>
  <dt>Runs per cell</dt>
  <dd>A cell marked <b>&times;3 runs</b> is the mean of three repeat runs; every other cell is a <b>single run</b>. The single-run cells are Fable at medium, Fable at extra-high, and the Haiku reference.</dd>
  <dt>What a score is</dt>
  <dd>Each task ships a short checklist a correct answer must satisfy; a cell's score is the share of those items hit. Change is the with-skill score minus the without-skill score, in percentage points. The checklists and pass rules were locked and hash-stamped before the first run.</dd>
  <dt>Codex cross-check</dt>
  <dd>A second vendor's model, Codex 5.6, independently re-scored %d sampled comparisons against the same instructions and agreed with the final marks <b>%s</b> of the time. It is an exploratory spot-check and changes none of these numbers. Section 5 has the breakdown; the toggle in section 1 marks the boxes it re-scored.</dd>
</dl>
</section>
"""


def _embed_data(data):
    """Lean copy for the embedded transparency blob: keep every number, drop
    the prose (prompt and checklist text already appear in the HTML)."""
    slim = dict(data)
    t = data["tasks"]
    slim_tasks = dict(t)
    slim_tasks["list"] = [
        {k: v for k, v in task.items() if k not in ("prompt", "must_hits")}
        for task in t["list"]]
    slim_tasks["by_id"] = {task["id"]: task for task in slim_tasks["list"]}
    slim["tasks"] = slim_tasks
    return slim


def render_page(data, favicon_uri):
    embedded = json.dumps(_embed_data(data), ensure_ascii=True, sort_keys=True,
                          separators=(",", ":")).replace("</", "<\\/")
    theme_init = ('<script>(function(){try{var s=localStorage.getItem'
                  '("hamz-theme");if(s==="light"||s==="dark")'
                  'document.documentElement.setAttribute("data-theme",s);}'
                  'catch(e){}})();</script>')
    favicon = ('<link rel="icon" type="image/png" href="%s">' % favicon_uri) \
        if favicon_uri else ""
    primer = PRIMER_HTML % (
        len(data["complete_case_tasks"]),
        len(data["cells"]), len(data["cells"]),
        data["concordance"]["n_comparisons"],
        fmt_pct(data["concordance"]["overall_pct"]))
    head = """<!doctype html>
<html lang="en">
<head>
%s
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="robots" content="noindex"/>
%s
<title>Skills x Effort Lattice: Results Explorer</title>
<style>%s%s%s</style>
</head>
<body>
%s
%s
<header>
<h1>Skills x Effort Lattice: Results Explorer</h1>
</header>
%s
""" % (theme_init, favicon, CSS_BASE, CSS_NAV, CSS_SEC, NAV_HTML, JUMPBAR_HTML,
       primer)

    body = (render_matrix_section(data)
            + render_curves_section(data)
            + render_tasks_section(data)
            + render_judging_section(data)
            + render_codex_section(data)
            + render_prov_section(data))

    foot = """
<footer>
<p>Shared task set (%d tasks): <span class="mono">%s</span></p>
<p>One self-contained file: no network requests, no external assets. Tables and
charts render without JavaScript; the show controls, the section accordions, and
the task filters enhance them when JavaScript is available.</p>
</footer>
<script id="lattice-data" type="application/json">%s</script>
<script>%s</script>
</body>
</html>
""" % (len(data["complete_case_tasks"]),
       esc(", ".join(data["complete_case_tasks"])), embedded, JS)
    return head + body + foot


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--concordance", default=DEFAULT_CONCORDANCE)
    ap.add_argument("--breakdown", default=DEFAULT_BREAKDOWN)
    ap.add_argument("--golden", default=DEFAULT_GOLDEN)
    ap.add_argument("--links", default=DEFAULT_LINKS)
    args = ap.parse_args(argv)

    matrix = load_json(args.matrix)
    scanned, skipped = scan_cell_dirs(args.cells)
    concordance = load_json(args.concordance)
    breakdown = load_json(args.breakdown)
    golden_rows = load_jsonl(args.golden)
    labels = load_json(TASK_LABELS_FILE) if os.path.isfile(TASK_LABELS_FILE) else {}
    favicon_uri = read_text_asset(FAVICON_FILE)

    with open(args.golden, "rb") as f:
        suite_hash = hashlib.sha256(f.read()).hexdigest()

    # fixture/script link-out gate: publish links only when owner-confirmed OK
    links_state = "no links file"
    task_links = {}
    if os.path.isfile(args.links):
        links_doc = load_json(args.links)
        lm = links_doc.get("_meta", {}).get("publication_status", {})
        links_state = lm.get("state", "unknown")
        if links_state == "LIVE":
            task_links = links_doc.get("tasks", {})

    data = build_data(matrix, scanned, skipped, concordance, breakdown,
                      golden_rows, labels, args, suite_hash, links_state)
    if task_links:
        for tid, task in data["tasks"]["by_id"].items():
            task["github_links"] = task_links.get(tid)
    page = render_page(data, favicon_uri)

    if "—" in page:
        sys.exit("refusing to write: an em-dash reached the output; fix the "
                 "offending label or data field")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(page)
    for w in data["warnings"]:
        print("note: %s" % w, file=sys.stderr)
    t = data["tasks"]
    print("wrote %s (%d conditions, %d open cells, %d tasks, %d runs, codex %s%%)"
          % (args.out, len(data["cells"]), len(data["open_cells"]),
             t["n_tasks"], t["total_runs"], data["concordance"]["overall_pct"]))


if __name__ == "__main__":
    main()
