#!/usr/bin/env python3
"""Emit the unified lattice results explorer as one self-contained HTML file.

Reads the final matrix artifact (results/matrix/matrix.json) plus the
per-cell scores.json files under the run directories, cross-checks the
matrix numbers against the per-cell artifacts, folds in the second-vendor
concordance spot-check (results/concordance/codex-concordance.json), and
writes a single HTML page with the data embedded as JSON. Stdlib only.
No network, no external assets. Every number on the page comes from the
JSON read at generation time; the template contributes labels only.

Usage (from the repo root):
  python3 eval/make_explorer.py --matrix results/matrix/matrix.json \
      --cells 'results/lattice-*' --out results/matrix/explorer.html
"""

import argparse
import datetime
import glob
import html
import json
import os
import sys

REGEN_COMMAND = (
    "python3 eval/make_explorer.py --matrix results/matrix/matrix.json "
    "--cells 'results/lattice-*' --out results/matrix/explorer.html"
)
DEFAULT_CONCORDANCE = "results/concordance/codex-concordance.json"

# Presentation-only configuration (labels and ordering, never numbers).
EFFORT_ORDER = ["low", "medium", "high", "xhigh", "max"]
MODEL_ORDER = ["claude-fable-5", "claude-sonnet-5", "claude-opus-4-8"]
BASELINE_LABEL = "no effort setting, shown for reference"
OPEN_CELL_LABEL = "max run not finished"

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


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    return html.escape(str(s), quote=True)


def fmt_pct(v):
    return "{:.1f}%".format(v)


def fmt_delta(v):
    return "{:+.1f}".format(v)


# ---------------------------------------------------------------------------
# Data assembly
# ---------------------------------------------------------------------------

def scan_cell_dirs(pattern):
    """Return ({basename: {dir, scores, meta}}, [(dir, reason) skipped])."""
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
    """Verify matrix per-cell aggregates against the per-cell scores.json."""
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
        for field, sfield in (("n_expectations", "n_expectations"),
                              ("cold_hits", "cold_hits"),
                              ("loaded_hits", "loaded_hits")):
            if sa.get(sfield) != ma.get(field):
                warnings.append(
                    "%s: %s mismatch (matrix %s vs scores.json %s)"
                    % (key, field, ma.get(field), sa.get(sfield)))
    return warnings, used


def find_open_and_extra(scanned, used):
    """Split non-matrix run dirs into open cells (no scored data) and extras."""
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
            extras.append(base)
    return open_cells, extras


def build_cell_display(key, cell):
    """Display record for one matrix cell, on the shared 16-task basis."""
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


def build_concordance(concordance, cells):
    """Fold the second-vendor spot-check into per-cell and overall tallies.

    Every number here is read from the concordance JSON at generation time
    and mapped onto the matrix cells by run id. Nothing here feeds any rate,
    difference, or verdict shown elsewhere on the page.
    """
    run_to_key = {c["run_id"]: c["key"] for c in cells.values() if c.get("run_id")}
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


def build_data(matrix, scanned, skipped, concordance, args):
    warnings, used = cross_check(matrix, scanned)
    open_cells, extras = find_open_and_extra(scanned, used)
    for base in extras:
        warnings.append(
            "%s: scored data on disk but not a matrix cell; not displayed"
            % base)
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

    return {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
            .strftime("%Y-%m-%d %H:%M:%S UTC"),
        "regen_command": REGEN_COMMAND,
        "sources": {
            "matrix": args.matrix,
            "cells_pattern": args.cells,
            "cell_dirs_scanned": len(scanned),
            "concordance": args.concordance,
        },
        "cell_order": matrix["cell_order"],
        "cells": cells,
        "open_cells": open_cells,
        "models": models,
        "baseline_models": baselines,
        "efforts": EFFORT_ORDER,
        "complete_case_tasks": matrix["complete_case_tasks"],
        "skills": matrix["skills"],
        "per_skill_note": matrix["per_skill_note"],
        "judging": judging,
        "concordance": build_concordance(concordance, cells),
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


def nlab(c):
    runs = ("%d runs each" % c["repeats"]) if c["replicated"] else "1 run each"
    return "%d tasks, %s" % (c["n_tasks"], runs)


def codex_chip(data, key):
    cx = data["concordance"]["per_cell"].get(key)
    if not cx:
        return ""
    diff = cx["n_disagree"]
    cls = "codex-chip has-diff" if diff else "codex-chip"
    body = "Codex %d/%d agree" % (cx["n_agree"], cx["n_marks"])
    return '<span class="%s">%s</span>' % (cls, esc(body))


# ---------------------------------------------------------------------------
# Rendering: results grid
# ---------------------------------------------------------------------------

def render_grid_cell(data, c):
    cls = "cell rep" if c["replicated"] else "cell"
    badge = ('<span class="badge">mean of %d runs</span>' % c["repeats"]) \
        if c["replicated"] else ""
    return (
        '<td class="%s">%s'
        '<span class="v v-cold"><em>without</em> <b>%s</b></span>'
        '<span class="v v-loaded"><em>with</em> <b>%s</b></span>'
        '<span class="v v-delta"><em>change</em> <b>%s</b></span>'
        '<span class="nlab">%s</span>%s</td>'
        % (cls, badge, esc(fmt_pct(c["cold"])), esc(fmt_pct(c["loaded"])),
           esc(fmt_delta(c["delta"])), esc(nlab(c)), codex_chip(data, c["key"])))


def render_matrix_section(data):
    efforts = data["efforts"]
    head = "".join('<th scope="col">%s</th>' % esc(e) for e in efforts)
    head += '<th scope="col">no effort<span class="nlab">(reference)</span></th>'
    rows = []
    for model in data["models"] + data["baseline_models"]:
        is_baseline = model in data["baseline_models"]
        tag = ('<span class="nlab">%s</span>' % esc(BASELINE_LABEL)) \
            if is_baseline else ""
        dot = ('<span class="mdot" style="--c:%s"></span>'
               % model_color(model))
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
                tds.append('<td class="cell empty" aria-label="no such condition">-</td>')
        cb = cell_by(data, model, "none")
        tds.append(render_grid_cell(data, cb) if cb is not None
                   else '<td class="cell empty" aria-label="no such condition">-</td>')
        rows.append('<tr class="%s"><th scope="row">%s%s%s</th>%s</tr>'
                    % ("baseline" if is_baseline else "", dot, esc(model), tag,
                       "".join(tds)))
    n_conditions = len(data["cells"])
    cx = data["concordance"]
    return """
<section id="matrix" aria-labelledby="matrix-h">
<h2 id="matrix-h">1. Skill effect across models and effort</h2>
<p class="lead">Each box is one model run at one effort level, scored two ways:
without the skill installed and with it. Each task carries a short checklist of
things a correct answer must do, and a score is the share of those checklist
items hit. Change is the with-skill score minus the without-skill score, in
percentage points. The rules and pass criteria were locked and publicly
hash-stamped before the first run. Every box is a small sample, so read each
number as a rough signal, not a precise measurement.</p>
<div class="card">
<div class="card-t">%d conditions on one shared task set</div>
<div class="card-s">the %d tasks that were valid in every condition, the only
basis that compares cleanly across boxes</div>
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
<p class="caption">%s. A spot-check by a second vendor, not a re-run of the
experiment. Turn it on to mark the boxes whose comparisons Codex re-scored.</p>
<div class="scroll"><table class="mx" id="mxtable">
<thead><tr><th scope="col">model \\ effort</th>%s</tr></thead>
<tbody>%s</tbody>
</table></div>
<div class="foot">Methodology: without = no skill installed; with = skill
installed; change = with minus without, in percentage points, weighted by the
checklist. Boxes marked "mean of 3 runs" carry an accent border and average
three repeat runs; the rest are a single run. Numbers read this generation
from the matrix artifact. Codex counts read from the concordance file.</div>
</div>
</section>
""" % (n_conditions, len(data["complete_case_tasks"]), esc(cx["caption"]),
       head, "".join(rows))


# ---------------------------------------------------------------------------
# Rendering: effort curves (static SVG, no JS required)
# ---------------------------------------------------------------------------

def render_curve_svg(data, model, ymin, color):
    efforts = data["efforts"]
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
    for i, e in enumerate(efforts):
        parts.append('<text x="%.1f" y="%d" class="ax" text-anchor="middle">%s</text>'
                     % (x(i), H - mb + 16, esc(e)))
    parts.append('<text x="%.1f" y="%d" class="axttl" text-anchor="middle">'
                 'effort level</text>' % (ml + pw / 2.0, H - mb + 40))

    pts = []
    for i, e in enumerate(efforts):
        c = cell_by(data, model, e)
        if c is not None:
            pts.append((i, c))

    # cold = dashed line, loaded = solid line, both in the model colour.
    for arm, dash in (("cold", "5 4"), ("loaded", "")):
        if len(pts) >= 2:
            path = " ".join("%.1f,%.1f" % (x(i), y(c[arm])) for i, c in pts)
            da = (' stroke-dasharray="%s"' % dash) if dash else ""
            parts.append('<polyline points="%s" fill="none" stroke="%s" '
                         'stroke-width="2"%s/>' % (path, color, da))
        for i, c in pts:
            cx, cy = x(i), y(c[arm])
            arm_lbl = "with the skill" if arm == "loaded" else "without the skill"
            tip = "%s at %s: %s %s (%s)" % (
                model, c["effort"], arm_lbl, fmt_pct(c[arm]), nlab(c))
            if c["replicated"]:
                for r in c.get("per_repeat", []):
                    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                                 'stroke="%s" stroke-width="1.4" opacity="0.4"/>'
                                 % (cx - 5, y(r[arm]), cx + 5, y(r[arm]), color))
                fill = "var(--raised)" if arm == "loaded" else color
                parts.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" '
                             'stroke="%s" stroke-width="2"><title>%s</title></circle>'
                             % (cx, cy, fill, color, esc(tip)))
            else:
                fill = color if arm == "loaded" else "var(--raised)"
                parts.append('<circle cx="%.1f" cy="%.1f" r="3.4" fill="%s" '
                             'stroke="%s" stroke-width="1.6"><title>%s</title>'
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
             "with the skill, dashed is without. Exact values are in the grid "
             "above." % (model, ymin))
    return ('<svg viewBox="0 0 %d %d" role="img" aria-label="%s" '
            'preserveAspectRatio="xMidYMid meet">%s</svg>'
            % (W, H, esc(label), "".join(parts)))


def render_curves_section(data):
    vals = []
    for c in data["cells"].values():
        if c["model"] in data["baseline_models"]:
            continue
        vals.extend([c["cold"], c["loaded"]])
        for r in c.get("per_repeat", []):
            vals.extend([r["cold"], r["loaded"]])
    ymin = int(min(vals) // 5 * 5) if vals else 75

    charts = []
    for m in data["models"]:
        col = model_color(m)
        legend = (
            '<div class="legend">'
            '<span class="lg-item"><span class="sw dash" style="--c:%s"></span>'
            'without the skill</span>'
            '<span class="lg-item"><span class="sw solid" style="--c:%s"></span>'
            'with the skill</span></div>' % (col, col))
        charts.append(
            '<figure class="card">'
            '<div class="card-t"><span class="mdot" style="--c:%s"></span>%s</div>'
            '<div class="card-s">checklist score against effort, %d shared tasks</div>'
            '%s%s'
            '<div class="foot">Methodology: each point is the score with or '
            'without the skill on the %d shared tasks. Low and max are the mean '
            'of 3 repeat runs (ring marker, side ticks at each run); the other '
            'levels are a single run (small dot). Small samples, read as a '
            'rough signal.</div></figure>'
            % (col, esc(m), len(data["complete_case_tasks"]), legend,
               render_curve_svg(data, m, ymin, col),
               len(data["complete_case_tasks"])))

    base_notes = []
    for m in data["baseline_models"]:
        c = cell_by(data, m, "none")
        if c is not None:
            base_notes.append(
                "%s has no effort setting, so it sits outside the effort "
                "comparison: without the skill %s, with the skill %s, change "
                "%s (%s)."
                % (m, fmt_pct(c["cold"]), fmt_pct(c["loaded"]),
                   fmt_delta(c["delta"]), nlab(c)))
    base_html = ('<p class="note">%s</p>' % esc(" ".join(base_notes))) \
        if base_notes else ""
    return """
<section id="curves" aria-labelledby="curves-h">
<h2 id="curves-h">2. Effort curves per model</h2>
<p class="lead">The same checklist scores drawn against effort. Each model has
its own colour. The solid line is with the skill installed, the dashed line is
without. Low and max were run three times; the middle levels once.</p>
<div class="charts">%s</div>
%s
</section>
""" % ("".join(charts), base_html)


# ---------------------------------------------------------------------------
# Rendering: per-skill drill-down
# ---------------------------------------------------------------------------

def render_skills_section(data):
    order = data["cell_order"]
    blocks = []
    skills = sorted(data["skills"].keys())
    for skill in skills:
        per_cell = data["skills"][skill]
        rows = []
        for key in order:
            r = per_cell.get(key)
            if r is None:
                ex = data["cells"][key].get("excluded_tasks", [])
                why = ("task set aside in this condition (%s)" % ", ".join(ex)) \
                    if ex else "no data in this condition"
                rows.append('<tr><th scope="row">%s</th>'
                            '<td colspan="4" class="mut">%s</td></tr>'
                            % (esc(key), esc(why)))
                continue
            pc = data["cells"].get(key, {})
            runs = "3 runs each" if pc.get("replicated") else "1 run each"
            sample = "%d task, %s" % (r["n_tasks"], runs)
            rows.append(
                '<tr><th scope="row">%s</th>'
                '<td>%d/%d<span class="q">%s</span></td>'
                '<td class="hero">%d/%d<span class="q">%s</span></td>'
                '<td>%s<span class="q">points</span></td>'
                '<td class="mut">%s</td></tr>'
                % (esc(key),
                   r["cold_hits"], r["n_must_hits"], fmt_pct(r["cold_rate_pct"]),
                   r["loaded_hits"], r["n_must_hits"], fmt_pct(r["loaded_rate_pct"]),
                   esc(fmt_delta(r["delta_pp"])), esc(sample)))
        blocks.append(
            '<details id="sk-%d"><summary>%s</summary>'
            '<div class="scroll"><table class="sk">'
            '<thead><tr><th scope="col">condition</th>'
            '<th scope="col">without skill</th>'
            '<th scope="col">with skill</th><th scope="col">change</th>'
            '<th scope="col">sample</th></tr></thead>'
            '<tbody>%s</tbody></table></div></details>'
            % (len(blocks), esc(skill), "".join(rows)))
    options = "".join('<option value="sk-%d">%s</option>' % (i, esc(s))
                      for i, s in enumerate(skills))
    return """
<section id="skills" aria-labelledby="skills-h">
<h2 id="skills-h">3. Per-skill detail (%d skills)</h2>
<p class="lead">%s Each cell below shows checklist hits for that skill's one
task within each condition. Every per-skill cell is a single task, so these are
the roughest signals on the page.</p>
<div class="card">
<div class="toolbar">
  <label class="tlabel" for="skillsel">jump to skill:</label>
  <select id="skillsel"><option value="">(choose)</option>%s</select>
  <noscript><span class="nlab">(selector needs JS; every skill is expandable below)</span></noscript>
</div>
%s
<div class="foot">Methodology: without and with are checklist hits for that
skill's task in each condition; change is with minus without, in percentage
points. One task per cell.</div>
</div>
</section>
""" % (len(skills), esc(data["per_skill_note"]), options, "".join(blocks))


# ---------------------------------------------------------------------------
# Rendering: judging panel
# ---------------------------------------------------------------------------

def render_judging_section(data):
    ov = data["judging"]["overall"]
    adj = ov["adjudication"]
    tiles = """
<div class="tiles">
  <div class="tile"><b>%s</b><span>marks the two judges split on<br/>(%d of %d)</span></div>
  <div class="tile"><b>%s</b><span>marks sent to the third judge<br/>(%d of %d)</span></div>
  <div class="tile"><b>%d</b><span>left unresolved</span></div>
</div>
""" % (fmt_pct(ov["disagreement_rate_pct"]), ov["n_disagreed"], ov["n_marks"],
       fmt_pct(adj["adjudication_rate_pct"]), adj["n_adjudicated"],
       adj["n_slot_marks"], adj["n_unresolved"])
    rows = []
    for key in data["cell_order"]:
        jd = data["judging"]["cells"][key]
        a = jd["adjudication"]
        rows.append(
            '<tr><th scope="row">%s</th>'
            '<td>%d / %d<span class="q">%s</span></td>'
            '<td>%d / %d<span class="q">%s</span></td><td>%d</td></tr>'
            % (esc(key),
               jd["n_disagreed"], jd["n_marks"], fmt_pct(jd["disagreement_rate_pct"]),
               a["n_adjudicated"], a["n_slot_marks"], fmt_pct(a["adjudication_rate_pct"]),
               a["n_unresolved"]))
    return """
<section id="judging" aria-labelledby="judging-h">
<h2 id="judging-h">4. How the scoring was judged</h2>
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
<div class="foot">Methodology: split and sent-to-third counts are per checklist
mark; disputed marks are kept in every denominator. No mark was left
unresolved.</div>
</div>
</section>
""" % (tiles, "".join(rows))


# ---------------------------------------------------------------------------
# Rendering: second-vendor spot-check (Codex)
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
        cells.append(
            '<td>%s<span class="q">%d/%d marks</span></td>'
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
    return """
<section id="codex" aria-labelledby="codex-h">
<h2 id="codex-h">5. Second-vendor spot-check (Codex 5.6)</h2>
<p class="caption">%s</p>
<p class="lead">A different vendor's model, Codex 5.6 (%s), re-scored %d of the
comparisons using the same frozen instructions the Claude judges saw. This is a
confidence spot-check, not a re-run of the experiment, and it changes none of
the numbers above. Use the toggle in section 1 to see which boxes these
comparisons came from.</p>
<div class="card">
<div class="card-t">Codex agreed with the final marks %s of the time</div>
<div class="card-s">%d of %d individual checklist marks matched</div>
%s
<div class="scroll"><table class="cx">
<thead><tr><th scope="col">agreement by model column</th>%s</tr></thead>
<tbody><tr><th scope="row">Codex vs final marks</th>%s</tr></tbody>
</table></div>
<div class="foot">Methodology: Codex ran once at high reasoning effort over 50
comparisons picked by a published hash rule, scoring the same blinded content
the judges scored. Exploratory only: it never touches a rate, difference, or
verdict.</div>
</div>
</section>
""" % (esc(cx["caption"]), esc(cx["codex_model"]), cx["n_comparisons"],
       fmt_pct(cx["overall_pct"]), cx["n_agree"], cx["n_marks"], tiles,
       head, "".join(cells))


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

CSS = """
:root{
--bg:#F6F5F1;--raised:#FFFFFF;--ink:#1B1B18;--mut:#6C6C64;
--line:#E6E3DC;--soft:#F0EEE7;--acc:#C7643C;--hero:#FBF3EE;
--fable:#E8734A;--opus:#27A37A;--sonnet:#6C5CE0;--haiku:#8A94A0;
--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}
@media (prefers-color-scheme: dark){:root{
--bg:#0F1216;--raised:#171C22;--ink:#E8EDF2;--mut:#98A2AE;
--line:#252C34;--soft:#1B2128;--acc:#E8734A;--hero:#1E2A2C;}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
padding:2.2rem 1.2rem 4rem;max-width:1200px;margin-inline:auto}
h1{font-size:1.5rem;margin:0 0 .35rem;letter-spacing:-.01em}
h2{font-size:1.15rem;margin:2.8rem 0 .4rem;letter-spacing:-.01em}
a{color:var(--acc)}
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
details.build{margin:.4rem 0 0}
details.build>summary{cursor:pointer;color:var(--mut);font-size:.78rem;
font-family:var(--mono)}
details.build .prov,details.build .warn{margin-top:.5rem}
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
td{font-family:var(--mono);font-weight:400}
thead th{color:var(--mut);font-size:.74rem;font-weight:600;
border-bottom:1px solid var(--line)}
tbody th{color:var(--mut);font-size:.75rem;white-space:nowrap;font-weight:500}
td .q{display:block;color:var(--mut);font-size:.66rem;font-family:var(--mono);
margin-top:.1rem}
td.hero{background:var(--hero)}
.mx td.cell{min-width:8.4rem;position:relative}
.mx td.rep{box-shadow:inset 0 0 0 1px var(--opus)}
.mx td.open{color:var(--mut);font-style:italic;font-size:.78rem}
.mx td.empty{color:var(--mut);text-align:center}
.mx tr.baseline th,.mx tr.baseline td{border-top:2px solid var(--line)}
.v{display:block;white-space:nowrap}
.v em{font-style:normal;color:var(--mut);font-size:.66rem;
display:inline-block;width:3.9rem}
.v b{font-weight:600}
.v-loaded b{color:var(--opus)}
.badge{display:inline-block;border:1px solid var(--opus);color:var(--opus);
border-radius:4px;font-size:.6rem;padding:0 .3rem;margin-bottom:.2rem;
font-family:var(--mono)}
.nlab{display:block;color:var(--mut);font-size:.66rem;margin-top:.2rem;
font-family:var(--mono)}
.codex-chip{display:none;margin-top:.35rem;border:1px dashed var(--sonnet);
color:var(--sonnet);border-radius:4px;font-size:.62rem;padding:.08rem .3rem;
font-family:var(--mono)}
.codex-chip.has-diff{border-style:solid;border-color:var(--acc);color:var(--acc)}
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
border-radius:7px;padding:.3rem .5rem;font-family:var(--mono);font-size:.76rem}
#mxtable[data-view="cold"] .v:not(.v-cold){display:none}
#mxtable[data-view="loaded"] .v:not(.v-loaded){display:none}
#mxtable[data-view="delta"] .v:not(.v-delta){display:none}
.charts{display:flex;gap:1rem;flex-wrap:wrap}
.charts figure{margin:0;flex:1 1 320px;min-width:280px;max-width:440px}
svg{width:100%;height:auto;display:block}
svg .grid{stroke:var(--line);stroke-width:1}
svg .ax{fill:var(--mut);font-family:var(--mono);font-size:11px}
svg .ax.open{fill:var(--mut);font-style:italic;font-size:10px}
svg .axttl{fill:var(--mut);font-family:var(--mono);font-size:11px}
svg .openline{stroke:var(--mut);stroke-dasharray:3 4;stroke-width:1}
.legend{display:flex;gap:1.1rem;justify-content:center;flex-wrap:wrap;
margin:0 0 .3rem;font-size:.74rem;color:var(--mut);font-family:var(--mono)}
.lg-item{display:inline-flex;align-items:center;gap:.35rem}
.sw{display:inline-block;width:20px;height:0;border-top:2px solid var(--c)}
.sw.dash{border-top-style:dashed}
details{border:1px solid var(--line);border-radius:10px;margin:.4rem 0;
background:var(--bg)}
summary{cursor:pointer;padding:.5rem .8rem;font-family:var(--mono);
font-size:.85rem;list-style-position:inside}
details[open] summary{border-bottom:1px solid var(--line);color:var(--acc)}
details .scroll{margin:.4rem .6rem .6rem}
.tiles{display:flex;gap:.8rem;flex-wrap:wrap;margin:.4rem 0 1rem}
.tile{background:var(--soft);border:1px solid var(--line);border-radius:12px;
padding:.85rem 1.1rem;min-width:12rem;flex:1 1 12rem}
.tile b{display:block;font-size:1.7rem;font-family:var(--mono);
color:var(--acc);font-weight:600}
.tile span{color:var(--mut);font-size:.73rem;font-family:var(--mono)}
.warn{border:1px solid var(--line);background:var(--raised);border-radius:10px;
padding:.6rem .9rem;color:var(--mut);font-size:.78rem;font-family:var(--mono)}
footer{margin-top:3rem;color:var(--mut);font-size:.78rem}
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
  var sel = document.getElementById('skillsel');
  if (sel) {
    sel.addEventListener('change', function () {
      if (!sel.value) { return; }
      document.querySelectorAll('#skills details').forEach(function (d) {
        d.open = (d.id === sel.value);
      });
      var t = document.getElementById(sel.value);
      if (t) { t.scrollIntoView({ block: 'nearest' }); }
    });
  }
})();
"""


def render_page(data):
    embedded = json.dumps(data, ensure_ascii=True, sort_keys=True,
                          separators=(",", ":")).replace("</", "<\\/")
    warn_html = ""
    if data["warnings"]:
        items = "".join("<li>%s</li>" % esc(w) for w in data["warnings"])
        warn_html = ('<div class="warn"><b>generation notes</b>'
                     '<ul>%s</ul></div>' % items)
    head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="robots" content="noindex"/>
<title>Skills x Effort Lattice: Results Explorer</title>
<style>%s</style>
</head>
<body>
<header>
<h1>Skills x Effort Lattice: Results Explorer</h1>
<p class="lead">Every number below is read from the committed result files at
the moment this page was built; the template only supplies labels. Every box is
a small sample, so read each rate and change as a rough signal, not a precise
measurement.</p>
<details class="build">
<summary>How this page was built</summary>
<div class="prov">
built %s from <code>%s</code>, %d run directories matching <code>%s</code>,
and <code>%s</code><br/>
rebuild with: <code>%s</code>
</div>
%s
</details>
</header>
""" % (CSS, esc(data["generated_utc"]), esc(data["sources"]["matrix"]),
       data["sources"]["cell_dirs_scanned"],
       esc(data["sources"]["cells_pattern"]),
       esc(data["sources"]["concordance"]),
       esc(data["regen_command"]), warn_html)

    body = (render_matrix_section(data)
            + render_curves_section(data)
            + render_skills_section(data)
            + render_judging_section(data)
            + render_codex_section(data))

    foot = """
<footer>
<p>Shared task set (%d tasks): <span class="mono">%s</span></p>
<p>One self-contained file: no network requests, no external assets. Tables and
charts render without JavaScript; the show controls, the Codex toggle, and the
skill selector enhance them when JavaScript is available.</p>
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
    ap.add_argument("--matrix", required=True,
                    help="path to results/matrix/matrix.json")
    ap.add_argument("--cells", required=True,
                    help="glob for per-cell run dirs, e.g. 'results/lattice-*'")
    ap.add_argument("--out", required=True, help="output HTML path")
    ap.add_argument("--concordance", default=DEFAULT_CONCORDANCE,
                    help="path to the Codex concordance spot-check JSON")
    args = ap.parse_args(argv)

    matrix = load_json(args.matrix)
    scanned, skipped = scan_cell_dirs(args.cells)
    concordance = load_json(args.concordance)
    data = build_data(matrix, scanned, skipped, concordance, args)
    page = render_page(data)

    if "—" in page:
        sys.exit("refusing to write: an em-dash reached the output; "
                 "fix the offending label or data field")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(page)
    for w in data["warnings"]:
        print("note: %s" % w, file=sys.stderr)
    print("wrote %s (%d conditions, %d open cells, %d skills, codex %s%%)"
          % (args.out, len(data["cells"]), len(data["open_cells"]),
             len(data["skills"]), data["concordance"]["overall_pct"]))


if __name__ == "__main__":
    main()
