"""scores.json and REPORT.md emitters, plus run-directory replay.

Everything here is deterministic given the persisted run artifacts, so
--replay can recompute both files byte-for-byte from judge-outputs/,
order-key.json, and run-meta.json alone. The matrix bootstrap uses a
fixed, recorded seed, so matrix outputs are deterministic too.
"""
import json
import random
from pathlib import Path

from .scoring import score_run

LIMITATIONS = """\
1. Single-run variance. Unless repeats > 1, each arm was sampled once per
   task; per-task results near ties are not statistically meaningful. Treat
   the aggregate delta and only large per-task swings as signal.
2. Vocabulary echo limits blinding. Judges never see condition labels,
   skill names, paths, or tool logs, and inputs are verifier-checked, but a
   skill that works changes answer content. Blinding removes provenance,
   not the measured effect. Judge inputs are committed for audit.
3. Same-family judging. Claude judges Claude output; criterion-referenced
   binary scoring with mandatory evidence quotes narrows self-preference,
   but a cross-vendor judge would be stronger.
4. Explicit loading, not triggering. These results say nothing about
   whether the description gets the file read autonomously in real
   sessions.
5. Synthetic fixtures. Trap states reconstruct real failure classes in
   small repos; deltas may be conservative or optimistic, direction
   unknown.
6. Read-only is enforced by construction (disposable workspaces,
   per-staging template verification, and post-run snapshot diffs over
   the working tree and git refs), not sandboxing."""

# Panel runs replace limitation 3 with the two-judge-panel description;
# legacy single-judge runs keep LIMITATIONS verbatim so their committed
# reports replay byte-for-byte.
LIMITATIONS_PANEL = LIMITATIONS.replace(
    """3. Same-family judging. Claude judges Claude output; criterion-referenced
   binary scoring with mandatory evidence quotes narrows self-preference,
   but a cross-vendor judge would be stronger.""",
    """3. Same-vendor judging. Every comparison is graded by a two-judge
   panel (one Sonnet-class and one Opus-class judge, exact IDs pinned,
   both at medium effort) behind the identical blinding stack, and a
   must-hit scores only when both judges mark it identically;
   disagreements leave both arms and are published as a rate. Both
   judges are still Claude models: the residual same-vendor risk is
   mitigated, not removed, by the pre-registered exploratory Codex
   concordance sample re-scored on the committed judge inputs, which
   are public precisely so third parties can extend the cross-vendor
   audit.""",
)

# Adjudicated runs (run-meta carries an adjudicator block) describe the
# three-judge path; committed pre-adjudicator panel runs keep
# LIMITATIONS_PANEL verbatim so they replay byte-for-byte.
LIMITATIONS_ADJUDICATED = LIMITATIONS.replace(
    """3. Same-family judging. Claude judges Claude output; criterion-referenced
   binary scoring with mandatory evidence quotes narrows self-preference,
   but a cross-vendor judge would be stronger.""",
    """3. Same-vendor judging. Every comparison is graded by a two-judge
   panel (one Sonnet-class and one Opus-class judge, exact IDs pinned,
   both at medium effort) behind the identical blinding stack; each
   report-slot mark they disagree on is scored once by a pinned
   adjudicator on a minimal input, the final mark is the two-of-three
   majority, disputed marks never leave any denominator, and
   disagreement plus adjudication rates are published. All three judges
   are still Claude models: the residual same-vendor risk is mitigated,
   not removed, by the pre-registered exploratory Codex concordance
   sample re-scored on the committed judge inputs, which are public
   precisely so third parties can extend the cross-vendor audit.""",
)


def scores_text(scores):
    return json.dumps(scores, indent=2, sort_keys=True) + "\n"


def _pct(x, n):
    return f"{x}/{n} ({100 * x / n:.1f}%)" if n else f"{x}/0"


def render_report(run_meta, scores, comprehension, scrub_manifest):
    agg = scores["aggregate"]
    freeze = run_meta.get("freeze") or {}
    lines = [
        f"# A/B eval report: {run_meta['run_id']}",
        "",
        f"- Consumer model: {run_meta['model']}",
        f"- Consumer effort: {run_meta.get('effort', 'default')}",
    ]
    # Provenance lines that only exist for runs whose run-meta recorded
    # them (kept conditional so committed pre-existing runs still replay
    # byte-for-byte).
    effective = run_meta.get("consumer_models_effective")
    if effective:
        lines.append(f"- Consumer models effective: {', '.join(effective)}")
    mot = run_meta.get("max_output_tokens")
    if isinstance(mot, dict) and mot.get("value"):
        lines.append(
            f"- Max output tokens (pinned, both arms): {mot['value']}"
        )
    panel = run_meta.get("judge_panel")
    if panel:
        lines.append(
            f"- Judge panel: {' + '.join(panel['models'])} "
            f"(both pinned at --effort {panel['effort']})"
        )
    else:
        lines.append(f"- Judge model: {run_meta['judge_model']} (default effort)")
    adjudicator_meta = run_meta.get("adjudicator")
    if adjudicator_meta:
        lines.append(
            f"- Adjudicator: {adjudicator_meta['model']} (pinned at "
            f"--effort {adjudicator_meta['effort']}, invoked once per "
            f"disputed report-slot mark, two-of-three majority)"
        )
    lines += [
        f"- claude CLI: {run_meta.get('claude_cli_version', 'unknown')}",
        f"- Seed: {run_meta['seed']}",
        f"- Preregistered: {'yes' if run_meta.get('preregistered') else 'NO (ran with --allow-unfrozen)'}",
        f"- Freeze: {freeze.get('frozen_at', 'none')} (task file sha256 {str(freeze.get('task_file_sha256'))[:12]})",
        f"- Repeats: {run_meta.get('repeats', 1)} consumer / {run_meta.get('judge_repeats', 1)} judge",
        f"- Wall clock: {run_meta.get('wall_clock_seconds', 'unknown')} s",
        "",
        "## Aggregate",
        "",
        f"Cold {_pct(agg['cold_hits'], agg['n_expectations'])} | "
        f"Loaded {_pct(agg['loaded_hits'], agg['n_expectations'])} | "
        f"Delta +{agg['loaded_hits'] - agg['cold_hits']}",
        "",
        "The denominator is the frozen must-hit count over included tasks,",
        "computed from the data.",
    ]
    disagreement = scores.get("judge_disagreement")
    adjudication = (disagreement or {}).get("adjudication")
    if disagreement and adjudication:
        rate = disagreement["disagreement_rate_pct"]
        adj_rate = adjudication["adjudication_rate_pct"]
        by_slot = disagreement.get("by_slot") or {}
        by_arm = disagreement.get("by_arm") or {}
        lines += [
            "",
            f"Judge panel disagreement: {disagreement['n_disagreed']} of "
            f"{disagreement['n_marks']} must-hit marks "
            f"({'-' if rate is None else f'{rate}%'}) carried a disputed "
            f"report slot.",
            "",
            f"Adjudication: {adjudication['n_disputed_slot_marks']} of "
            f"{adjudication['n_slot_marks']} report-slot marks disputed; "
            f"{adjudication['n_adjudicated']} adjudicated by "
            f"{adjudication['model']} at --effort {adjudication['effort']} "
            f"({'-' if adj_rate is None else f'{adj_rate}%'} of all slot "
            f"marks) and kept in every denominator; "
            f"{adjudication['n_unresolved']} unresolved after retry "
            f"(judge-failure exclusion). Disputed slots by report slot: "
            f"report_1 {by_slot.get('report_1', 0)}, report_2 "
            f"{by_slot.get('report_2', 0)}; by arm: cold "
            f"{by_arm.get('cold', 0)}, loaded {by_arm.get('loaded', 0)}.",
            "",
            f"Combination rule: {disagreement['unit']}.",
        ]
        floor = disagreement.get("failure_floor") or {}
        if floor.get("floor_excluded_comparisons"):
            lines += [
                "",
                "Judge-failure floor: comparisons excluded because more "
                "than one third of their must-hit marks were judge-failure "
                "exclusions: "
                + ", ".join(floor["floor_excluded_comparisons"]) + ".",
            ]
    elif disagreement:
        rate = disagreement["disagreement_rate_pct"]
        lines += [
            "",
            f"Judge panel disagreement: {disagreement['n_disagreed']} of "
            f"{disagreement['n_marks']} marks "
            f"({'-' if rate is None else f'{rate}%'}) excluded from both "
            f"arms of their comparisons.",
            "",
            f"Agreement unit: {disagreement['unit']}.",
        ]
    repeats_detail = scores.get("repeats_detail")
    if repeats_detail:
        mean = repeats_detail["mean_over_repeats"]
        lines += [
            "",
            "Repeat-level aggregates (replicated cell; every repeat ran "
            "in its own isolated workspace with no shared session state):",
            "",
            "| Repeat | Cold | Loaded | Delta (pp) |",
            "|---|---|---|---|",
        ]
        for rk in sorted(repeats_detail["per_repeat"], key=lambda k: int(k[1:])):
            b = repeats_detail["per_repeat"][rk]
            lines.append(
                f"| {rk} | {b['cold_hits']}/{b['n_expectations']}"
                f" ({_fmt_rate(b['cold_rate_pct'])})"
                f" | {b['loaded_hits']}/{b['n_expectations']}"
                f" ({_fmt_rate(b['loaded_rate_pct'])})"
                f" | {_fmt_delta(b['delta_pp'])} |"
            )
        lines += [
            "",
            f"Endpoint mean over repeats: cold "
            f"{_fmt_rate(mean['cold_rate_pct'])} | loaded "
            f"{_fmt_rate(mean['loaded_rate_pct'])} | delta "
            f"{_fmt_delta(mean['delta_pp'])} pp.",
        ]
    lines += [
        "",
        "## Per-skill results",
        "",
        "| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |",
        "|---|---|---|---|---|---|",
    ]
    for skill in sorted(scores["skills"]):
        s = scores["skills"][skill]
        lines.append(
            f"| {skill} | {s['tasks']} | {s['cold_hits']}/{s['n_must_hits']} "
            f"| {s['loaded_hits']}/{s['n_must_hits']} "
            f"| {s['loaded_hits'] - s['cold_hits']:+d} "
            f"| {'PASS' if s['pass'] else 'FAIL'} |"
        )
    lines += ["", "## Per-task must-hits", ""]
    for task_id in sorted(scores["tasks"]):
        t = scores["tasks"][task_id]
        lines += [
            f"### {task_id} ({t['skill']})",
            "",
            f"Cold {t['cold_hits']}/{t['n_must_hits']}, "
            f"loaded {t['loaded_hits']}/{t['n_must_hits']}, "
            f"threshold {t['threshold']}: "
            f"{'PASS' if t['pass'] else 'FAIL'}"
            f"{' (regression)' if t['regression'] else ''}",
            "",
            "| Expectation | Cold | Loaded |",
            "|---|---|---|",
        ]
        for mh_id in t["per_expectation"]:
            e = t["per_expectation"][mh_id]
            lines.append(f"| {mh_id} | {e['cold']} | {e['loaded']} |")
        if t.get("disagreed_must_hits"):
            lines += [
                "",
                "Judge panel disagreed (excluded from both arms): "
                + ", ".join(t["disagreed_must_hits"]),
            ]
        verdicts = scores.get("comparative_verdicts", {}).get(task_id) or []
        if verdicts:
            lines += ["", f"Judge comparative verdict (no score weight): {verdicts[0]}"]
        lines.append("")
    lines += [
        "## Comprehension check (stage B, unblinded, non-scoring)",
        "",
        "| Task | Skill read in the with-skill run |",
        "|---|---|",
    ]
    for task_id in sorted(comprehension or {}):
        c = comprehension[task_id]
        reads = c if isinstance(c, list) else [c]
        ok = all(r.get("skill_read") for r in reads)
        lines.append(f"| {task_id} | {'yes' if ok else 'NO'} |")
    n_subs = len(scrub_manifest.get("substitutions", [])) if scrub_manifest else 0
    mutations = run_meta.get("workspace_mutation_warnings") or []
    arm_failures = {}
    for e in run_meta.get("excluded_tasks") or []:
        for a in e.get("failed_arms", ()):
            arm_failures[a] = arm_failures.get(a, 0) + 1
    lines += [
        "",
        "## Run notes",
        "",
        f"- Excluded tasks: {', '.join(scores['excluded_tasks']) or 'none'}",
    ]
    if arm_failures:
        # A failure in one arm removes the whole task from every
        # denominator, so the direction of exclusions must be visible.
        lines.append(
            "- Exclusions by failing arm: "
            + ", ".join(f"{a} {n}" for a, n in sorted(arm_failures.items()))
        )
    if disagreement and disagreement.get("tasks_excluded_zero_agreement"):
        lines.append(
            "- Tasks excluded by judge-panel zero agreement (every "
            "must-hit disagreed): "
            + ", ".join(disagreement["tasks_excluded_zero_agreement"])
        )
    floor_block = (disagreement or {}).get("failure_floor") or {}
    if floor_block.get("tasks_excluded_no_scorable_marks"):
        lines.append(
            "- Tasks excluded with no scorable marks (judge-failure "
            "exclusions only; adjudicated disagreements never exclude): "
            + ", ".join(floor_block["tasks_excluded_no_scorable_marks"])
        )
    lines += [
        f"- Scrub substitutions: {n_subs}",
        f"- Workspace mutation warnings: {', '.join(mutations) or 'none'}",
        "",
        "## Limitations",
        "",
        (LIMITATIONS_ADJUDICATED if run_meta.get("adjudicator")
         else LIMITATIONS_PANEL if panel else LIMITATIONS),
        "",
    ]
    return "\n".join(lines)


def load_run_dir(run_dir):
    """Read the persisted artifacts needed to (re)compute scores and report."""
    run_dir = Path(run_dir)
    meta = json.loads((run_dir / "run-meta.json").read_text(encoding="utf-8"))
    order_key = json.loads((run_dir / "order-key.json").read_text(encoding="utf-8"))
    judge_outputs = {}
    for p in sorted((run_dir / "judge-outputs").glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "adjudicator_model" in data \
                and "pair" in data:
            # Adjudication record: grouped under the reserved
            # "_adjudication" key next to the pair's per-judge outputs.
            entry = judge_outputs.setdefault(data["pair"], {})
            entry["_adjudication"] = data
            continue
        if isinstance(data, dict) and "judge_model" in data and "pair" in data:
            # Two-judge panel layout: one file per (pair, judge), grouped
            # here into {pair: {judge_model: judgments}} for scoring.
            entry = judge_outputs.setdefault(data["pair"], {})
            entry[data["judge_model"]] = data["judgments"]
            continue
        judge_outputs[p.stem] = data["judgments"] if "judgments" in data else [data]
    comp_path = run_dir / "comprehension.json"
    comprehension = (
        json.loads(comp_path.read_text(encoding="utf-8")) if comp_path.is_file() else {}
    )
    scrub_path = run_dir / "scrub-manifest.json"
    scrub_manifest = (
        json.loads(scrub_path.read_text(encoding="utf-8")) if scrub_path.is_file() else {}
    )
    return meta, judge_outputs, order_key, comprehension, scrub_manifest


def recompute(run_dir):
    """Recompute (scores_text, report_text) from a run directory's raw data."""
    meta, judge_outputs, order_key, comprehension, scrub_manifest = load_run_dir(run_dir)
    scores = score_run(meta, judge_outputs, order_key)
    return scores_text(scores), render_report(meta, scores, comprehension, scrub_manifest)


# ---------------------------------------------------------------- matrix

# Cells order by model, then by effort along this axis; unknown efforts
# sort after the known ones, alphabetically. "none" is the effort label of
# effort-invariant models (haiku-class), which are excluded from every
# effort-trend view.
EFFORT_ORDER = {"low": 0, "medium": 1, "high": 2, "xhigh": 3, "max": 4,
                "default": 5, "none": 6}

# Explicit effort levels usable for matched-effort cross-model comparison.
MATCHED_EFFORTS = ("low", "medium", "high", "xhigh", "max")

# Pre-registered minimum effect for the confirmatory endpoint verdicts:
# H1 is supported only when cold(max) - cold(low) >= 3 pp, H2 only when
# D(low) - D(max) >= 3 pp. Strict inequalities alone are never sufficient.
MIN_EFFECT_PP = 3.0
VERDICT_SUPPORTED = "directionally supported under the pre-registered rule"
VERDICT_NOT_SUPPORTED = "not supported under the pre-registered rule"
VERDICT_NOT_EVALUABLE = "not evaluable (missing endpoint data)"

# Task-cluster bootstrap: descriptive sensitivity only, non-inferential.
# The seed is fixed and recorded so the resampling is deterministic and
# cannot be reseeded after seeing any scores.
BOOTSTRAP_SEED = 20260710
BOOTSTRAP_ITERATIONS = 1000

# Invalidation classification: harness-censored means the harness cut a
# run off (timeout or the pinned output ceiling); everything else is a
# natural completion that was invalid (for example a missing Answers
# section or a cross-model fallback).
HARNESS_CENSOR_MARKERS = ("timed out", "timeout", "truncated", "ceiling")


class MatrixError(Exception):
    pass


def _rates(cold, loaded, n):
    return {
        "cold_rate_pct": round(100 * cold / n, 1) if n else None,
        "loaded_rate_pct": round(100 * loaded / n, 1) if n else None,
        "delta_pp": round(100 * (loaded - cold) / n, 1) if n else None,
    }


def _small_n_label(n_tasks, repeats):
    runs = "single run" if repeats == 1 else f"{repeats} runs"
    plural = "s" if n_tasks != 1 else ""
    return f"n={n_tasks} task{plural}, {runs} per arm: directional only"


def _equal_skill_delta_pp(task_scores):
    """Mean of per-skill delta percentage points, each skill weighted
    equally regardless of its must-hit count. None when no skill has a
    positive must-hit denominator."""
    per_skill = {}
    for t in task_scores.values():
        agg = per_skill.setdefault(t["skill"], {"cold": 0, "loaded": 0, "n": 0})
        agg["cold"] += t["cold_hits"]
        agg["loaded"] += t["loaded_hits"]
        agg["n"] += t["n_must_hits"]
    deltas = [
        100 * (a["loaded"] - a["cold"]) / a["n"]
        for a in per_skill.values() if a["n"]
    ]
    return round(sum(deltas) / len(deltas), 1) if deltas else None


def _headroom_recovered_pct(cold, loaded, n):
    """Headroom-normalized delta: (L - C) / (1 - C) as a percentage of the
    cold arm's remaining headroom. None when undefined (n = 0 or the cold
    arm is already at ceiling)."""
    if not n or cold >= n:
        return None
    return round(100 * (loaded - cold) / (n - cold), 1)


def _mean_over_repeats(per_repeat, task_ids):
    """Mean rates across repeats over the given task subset, plus the
    retained repeat-level values. per_repeat is scores["repeats_detail"]
    ["per_repeat"]. Returns None when there is no repeat data."""
    if not per_repeat:
        return None
    repeat_blocks = {}
    valid = []
    for rk in sorted(per_repeat, key=lambda k: int(k[1:])):
        tasks_r = per_repeat[rk].get("tasks") or {}
        sel = [tasks_r[t] for t in task_ids if t in tasks_r]
        n = sum(t["n_must_hits"] for t in sel)
        cold = sum(t["cold_hits"] for t in sel)
        loaded = sum(t["loaded_hits"] for t in sel)
        block = {
            "n_expectations": n,
            "cold_hits": cold,
            "loaded_hits": loaded,
            **_rates(cold, loaded, n),
        }
        repeat_blocks[rk] = block
        if n:
            valid.append(block)
    mean = {
        key: (round(sum(b[key] for b in valid) / len(valid), 1)
              if valid else None)
        for key in ("cold_rate_pct", "loaded_rate_pct", "delta_pp")
    }
    return {
        "n_repeats": len(repeat_blocks),
        "per_repeat": repeat_blocks,
        **mean,
        "note": (
            "replicated endpoint mean: rates are the unweighted mean of "
            "the per-repeat rates retained here"
        ),
    }


def _aggregate_over(task_scores, task_ids, repeats, basis, per_repeat=None):
    """One aggregate block over the given subset of a cell's scored tasks.

    basis is "available-case" (every task valid in that cell) or
    "complete-case" (only tasks valid in every cell of the matrix, i.e.
    paired exclusion applied across all cells so numbers are comparable).
    per_repeat is the cell's retained repeat-level task data when the cell
    ran replicated; the block then also carries mean_over_repeats, which
    replicated endpoint views and verdicts use instead of the
    majority-vote point values.
    """
    sel = {tid: task_scores[tid] for tid in task_ids}
    n = sum(s["n_must_hits"] for s in sel.values())
    cold = sum(s["cold_hits"] for s in sel.values())
    loaded = sum(s["loaded_hits"] for s in sel.values())
    block = {
        "basis": basis,
        "n_tasks": len(sel),
        "n_expectations": n,
        "cold_hits": cold,
        "loaded_hits": loaded,
        **_rates(cold, loaded, n),
        "delta_pp_equal_skill": _equal_skill_delta_pp(sel),
        "headroom_recovered_pct": _headroom_recovered_pct(cold, loaded, n),
        "ceiling_tasks": {
            "cold": sum(1 for s in sel.values()
                        if s["cold_hits"] == s["n_must_hits"]),
            "loaded": sum(1 for s in sel.values()
                          if s["loaded_hits"] == s["n_must_hits"]),
        },
        "label": _small_n_label(len(sel), repeats),
    }
    mean = _mean_over_repeats(per_repeat, sorted(sel))
    if mean is not None:
        block["mean_over_repeats"] = mean
        block["label"] += " (replicated endpoint mean over repeats)"
    return block


def _endpoint_complete_case(cell_task_scores, low_id, endpoint_id):
    """Per-model-column complete-case task set for H1, H2, retention, and
    H4 (pre-registered: effort-sweep-preregistration.md section 5, line
    115): tasks valid at BOTH the low and endpoint cells of ONE model's
    column, and nothing else. Deliberately narrower than the cross-model
    'complete_case_tasks' set (used only by the descriptive Complete-case
    aggregate table and the matched-effort/defaults-as-shipped views):
    per the pre-registered rule, "Interior cells never enter this set and
    cannot remove a task from it" -- and neither can any other model's
    column."""
    low_tasks = set(cell_task_scores.get(low_id, {}))
    endpoint_tasks = set(cell_task_scores.get(endpoint_id, {}))
    return sorted(low_tasks & endpoint_tasks)


def _cc_endpoint(cell, field="aggregate_complete_case", label="complete-case"):
    """Verdict-facing complete-case endpoint values for a cell: the
    replicated mean over repeats when the cell ran replicated, else the
    single-run point values. `field`/`label` select which complete-case
    aggregate to read: the cross-model complete-case by default (used by
    the descriptive Complete-case aggregate table and the matched-effort/
    defaults-as-shipped views), or the pre-registered per-model-column
    endpoint complete-case (see _endpoint_complete_case) for H1, H2,
    retention, and H4."""
    cc = cell[field]
    mean = cc.get("mean_over_repeats")
    if mean:
        return {"cold": mean["cold_rate_pct"],
                "loaded": mean["loaded_rate_pct"],
                "delta": mean["delta_pp"],
                "basis": f"{label}, replicated mean over "
                         f"{mean['n_repeats']} repeats"}
    return {"cold": cc["cold_rate_pct"], "loaded": cc["loaded_rate_pct"],
            "delta": cc["delta_pp"], "basis": f"{label}, single run"}


def _cc_endpoint_scoped(cell):
    """H1/H2/retention/H4-facing endpoint values, scoped to the
    pre-registered per-model-column complete-case set rather than the
    cross-model one (see _endpoint_complete_case, _cc_endpoint)."""
    if "aggregate_endpoint_complete_case" not in cell:
        return {"cold": None, "loaded": None, "delta": None,
                "basis": "endpoint complete-case: not computed"}
    return _cc_endpoint(cell, field="aggregate_endpoint_complete_case",
                        label="endpoint complete-case")


# Fable's confirmatory endpoint was amended 2026-07-10 from low-vs-max to
# low-vs-high (effort-sweep-amendment-2026-07-10-fable-endpoint.md,
# section (a)): fable-max never completed across three 5-hour windows, so
# it was declared a pre-registered open cell instead, with high (Fable's
# shipped default) taking its place as the second confirmatory point.
# Sonnet and Opus are unaffected and keep low-vs-max.
CONFIRMATORY_ENDPOINT_EFFORT_OVERRIDE = {"claude-fable-5": "high"}


def _confirmatory_endpoint_effort(model):
    """The effort level paired with 'low' as this model's confirmatory
    endpoint (see CONFIRMATORY_ENDPOINT_EFFORT_OVERRIDE)."""
    return CONFIRMATORY_ENDPOINT_EFFORT_OVERRIDE.get(model, "max")


def _endpoint_cells(cells, model):
    """(low_cell, endpoint_cell) for a model, or None when either is
    missing. endpoint_cell is at effort 'max' for every model except where
    CONFIRMATORY_ENDPOINT_EFFORT_OVERRIDE names a different effort."""
    endpoint_effort = _confirmatory_endpoint_effort(model)
    by_effort = {
        c["effort"]: c for c in cells.values() if c["model"] == model
    }
    if "low" not in by_effort or endpoint_effort not in by_effort:
        return None
    return by_effort["low"], by_effort[endpoint_effort]


def _hypothesis_verdicts(cells):
    """Confirmatory H1/H2 endpoint verdicts per model, 3 pp minimum effect.

    H1 and H2 are the only confirmatory hypotheses. Verdicts derive from
    the complete-case endpoint cells (low, max) alone; interior cells
    (medium, high, xhigh) cannot affect them under any circumstance, and
    effort-invariant models never appear. Replicated endpoint cells
    contribute their mean rates over repeats.
    """
    out = {
        "role": "confirmatory (H1 and H2 only)",
        "rule": (
            f"pre-registered minimum effect {MIN_EFFECT_PP:g} pp: H1 is "
            f"supported only when cold(max) - cold(low) >= "
            f"{MIN_EFFECT_PP:g} pp; H2 only when D(low) - D(max) >= "
            f"{MIN_EFFECT_PP:g} pp; strict inequalities alone are never "
            f"sufficient"
        ),
        "scope": (
            "endpoint cells only (low+max, except low+high for any model "
            "in CONFIRMATORY_ENDPOINT_EFFORT_OVERRIDE, currently Fable "
            "per the 2026-07-10 endpoint amendment), complete-case, "
            "replicated means when the endpoint ran repeated; interior "
            "cells (medium, high, xhigh) cannot affect H1 or H2 under any "
            "circumstance; effort-invariant models are outside all "
            "effort-trend hypotheses"
        ),
        "h1": {},
        "h2": {},
    }
    for model in sorted({c["model"] for c in cells.values()}):
        endpoints = _endpoint_cells(cells, model)
        if endpoints is None:
            continue
        endpoint_effort = endpoints[1]["effort"]
        low, high = (_cc_endpoint_scoped(c) for c in endpoints)
        basis = f"low: {low['basis']}; {endpoint_effort}: {high['basis']}"
        if low["cold"] is None or high["cold"] is None:
            out["h1"][model] = {"verdict": VERDICT_NOT_EVALUABLE,
                                "endpoint_effort": endpoint_effort,
                                "basis": basis}
        else:
            diff = round(high["cold"] - low["cold"], 1)
            out["h1"][model] = {
                "cold_low_pct": low["cold"],
                "cold_max_pct": high["cold"],
                "endpoint_effort": endpoint_effort,
                "difference_pp": diff,
                "verdict": (VERDICT_SUPPORTED if diff >= MIN_EFFECT_PP
                            else VERDICT_NOT_SUPPORTED),
                "basis": basis,
            }
        if low["delta"] is None or high["delta"] is None:
            out["h2"][model] = {"verdict": VERDICT_NOT_EVALUABLE,
                                "endpoint_effort": endpoint_effort,
                                "basis": basis}
        else:
            shrink = round(low["delta"] - high["delta"], 1)
            out["h2"][model] = {
                "delta_low_pp": low["delta"],
                "delta_max_pp": high["delta"],
                "endpoint_effort": endpoint_effort,
                "shrinkage_pp": shrink,
                "verdict": (VERDICT_SUPPORTED if shrink >= MIN_EFFECT_PP
                            else VERDICT_NOT_SUPPORTED),
                "basis": basis,
            }
    return out


def _retention(cells):
    """Retention ratio R = D(endpoint)/D(low) per model (endpoint is max,
    except where CONFIRMATORY_ENDPOINT_EFFORT_OVERRIDE names a different
    effort -- currently high for Fable, per the 2026-07-10 endpoint
    amendment), on the complete-case must-hit-weighted delta (the
    replicated mean when the endpoint ran repeated), defined only when
    D(low) > 0 (pre-registered rule); when D(low) <= 0, R is null and
    absolute deltas stand alone."""
    entries = []
    for model in sorted({c["model"] for c in cells.values()}):
        endpoints = _endpoint_cells(cells, model)
        if endpoints is None:
            continue
        endpoint_effort = endpoints[1]["effort"]
        d_low = _cc_endpoint_scoped(endpoints[0])["delta"]
        d_max = _cc_endpoint_scoped(endpoints[1])["delta"]
        defined = d_low is not None and d_max is not None and d_low > 0
        entries.append({
            "model": model,
            "basis": "complete-case",
            "endpoint_effort": endpoint_effort,
            "delta_low_pp": d_low,
            "delta_max_pp": d_max,
            "retention_ratio_R": round(d_max / d_low, 3) if defined else None,
            "note": (
                f"R = D({endpoint_effort})/D(low) on the complete-case "
                f"must-hit-weighted delta; small-n, directional only"
                if defined else
                "R undefined: D(low) <= 0; report absolute deltas only"
            ),
        })
    return entries


def _cc_summary(cell):
    """Complete-case numbers for a cross-model view row (the replicated
    mean delta when the cell ran repeated)."""
    cc = cell["aggregate_complete_case"]
    return {
        "cell": f"{cell['model']}@{cell['effort']}",
        "delta_pp": _cc_endpoint(cell)["delta"],
        "delta_pp_equal_skill": cc["delta_pp_equal_skill"],
        "headroom_recovered_pct": cc["headroom_recovered_pct"],
        "label": cc["label"],
    }


def _views(cells):
    """Cross-model views over the lattice cells.

    matched_effort (primary): models compared at the same explicit effort
    level. defaults_as_shipped (labeled secondary): each model at its own
    shipped default (effort "default" or "none"), so cross-model
    differences conflate model tier and effort level. h4_shrinkage:
    per-model low-to-max delta shrinkage side by side, directional only.
    All numbers are complete-case and every entry carries its small-n
    label.
    """
    matched = {}
    for effort in MATCHED_EFFORTS:
        row = {
            c["model"]: _cc_summary(c)
            for c in cells.values() if c["effort"] == effort
        }
        if row:
            matched[effort] = dict(sorted(row.items()))
    defaults = {}
    for c in cells.values():
        if c["effort"] in ("default", "none"):
            defaults[c["model"]] = {**_cc_summary(c), "effort": c["effort"]}
    return {
        "matched_effort": {
            "role": "primary",
            "basis": "complete-case",
            "note": (
                "cross-model comparisons hold the requested effort level "
                "fixed; effort-invariant models (effort none) never appear "
                "here"
            ),
            "efforts": matched,
        },
        "defaults_as_shipped": {
            "role": "secondary (labeled)",
            "basis": "complete-case",
            "note": (
                "each model at its own shipped default effort; the levels "
                "differ across models, so cross-model differences here "
                "conflate model tier and effort level"
            ),
            "models": dict(sorted(defaults.items())),
        },
        "h3_visibility_tags": {
            "role": "EXPLORATORY",
            "note": (
                "H3 (visibility-tag heterogeneity) is exploratory only: "
                "it is computed over tagged task strata outside this "
                "matrix, carries no confirmatory verdict, and no lattice "
                "number here feeds it"
            ),
        },
        "h4_shrinkage": {
            "role": "EXPLORATORY (directional only)",
            "note": (
                "H4: per-model low-to-max delta shrinkage reported side by "
                "side; exploratory, nothing stronger than direction is "
                "claimed, and effort-invariant models are excluded from "
                "all effort-trend views"
            ),
            "entries": _retention(cells),
        },
    }


def _matched_delta(block):
    """Delta from an aggregate block: the replicated mean over repeats when
    the cell ran repeated, else the single-run point delta."""
    mean = block.get("mean_over_repeats")
    return mean["delta_pp"] if mean else block["delta_pp"]


def _h4_matched_low_high(cells, cell_task_scores, cell_repeat_tasks):
    """ADDITIVE exploratory view: the amendment's deferred matched
    low-to-high H4 (effort-sweep-amendment-2026-07-10-fable-endpoint.md
    section (c)). All three effort-bearing models' shrinkage on ONE common
    low-to-high basis, so the cross-model comparison is basis-matched. For
    Fable, high is its replicated confirmatory endpoint. For Sonnet and
    Opus, high is an interior cell, not their confirmatory endpoint (which
    is max), but now a 3-run replicated mean like their endpoints; it's
    descriptive only and feeds no verdict. Each model's D(low) and
    D(high) use that model's own low+high endpoint complete-case set (see
    _endpoint_complete_case), so no other column's or interior cell's
    exclusions can move it. This adds keys only and changes no existing
    key, number, or verdict: every H1/H2/retention/H4 value stands
    untouched.
    """
    entries = []
    for model in sorted({c["model"] for c in cells.values()}):
        by_effort = {c["effort"]: cid for cid, c in cells.items()
                     if c["model"] == model}
        low_id = by_effort.get("low")
        high_id = by_effort.get("high")
        if low_id is None or high_id is None:
            continue
        endpoint_cc = _endpoint_complete_case(
            cell_task_scores, low_id, high_id)
        low_block = _aggregate_over(
            cell_task_scores[low_id], endpoint_cc, cells[low_id]["repeats"],
            "matched low-to-high endpoint complete-case",
            per_repeat=cell_repeat_tasks[low_id])
        high_block = _aggregate_over(
            cell_task_scores[high_id], endpoint_cc, cells[high_id]["repeats"],
            "matched low-to-high endpoint complete-case",
            per_repeat=cell_repeat_tasks[high_id])
        d_low = _matched_delta(low_block)
        d_high = _matched_delta(high_block)
        shrink = (round(d_low - d_high, 1)
                  if d_low is not None and d_high is not None else None)
        high_interior = cells[high_id]["repeats"] == 1
        # Whether "high" is this model's confirmatory endpoint is a property
        # of CONFIRMATORY_ENDPOINT_EFFORT_OVERRIDE, not of the cell's repeat
        # count. Those two facts used to coincide (only Fable's high was
        # ever replicated) but stopped coinciding once Sonnet/Opus's
        # interior cells were also replicated -- inferring "confirmatory
        # endpoint" from "replicated" is what caused this note to go wrong.
        high_is_confirmatory = _confirmatory_endpoint_effort(model) == "high"
        if high_is_confirmatory:
            note = "high is this model's replicated confirmatory endpoint"
        elif high_interior:
            note = ("high is an interior cell, not this model's "
                    "confirmatory endpoint (which is "
                    f"{_confirmatory_endpoint_effort(model)}): "
                    "single-run, no repeats, descriptive only")
        else:
            note = ("high is an interior cell, not this model's "
                    "confirmatory endpoint (which is "
                    f"{_confirmatory_endpoint_effort(model)}): "
                    f"a {cells[high_id]['repeats']}-run replicated mean "
                    "like its endpoints, descriptive only")
        entries.append({
            "model": model,
            "endpoint_effort": "high",
            "n_tasks": len(endpoint_cc),
            "delta_low_pp": d_low,
            "delta_high_pp": d_high,
            "shrinkage_pp": shrink,
            "high_cell_repeats": cells[high_id]["repeats"],
            "high_cell_replicated": not high_interior,
            "high_cell_interior_single_run": high_interior,
            "high_is_confirmatory_endpoint": high_is_confirmatory,
            "note": note,
        })
    return {
        "role": "EXPLORATORY (directional only), ADDITIVE",
        "basis": (
            "matched low-to-high, per-model-column endpoint complete-case"
        ),
        "note": (
            "matched cross-model shrinkage on one common low-to-high basis "
            "for all three effort-bearing models; fulfills the deferred "
            "follow-up disclosed in effort-sweep-amendment-2026-07-10-"
            "fable-endpoint.md section (c). Exploratory and directional "
            "only: Fable's high is its replicated confirmatory endpoint; "
            "for Sonnet and Opus, high is an interior cell (not their "
            "confirmatory endpoint, which is max), now a replicated mean "
            "like their endpoints but still descriptive only, feeding no "
            "verdict -- see each entry's own note for its exact repeat "
            "count. This view adds keys only and changes no existing "
            "H1/H2/retention/H4 number or verdict"
        ),
        "entries": entries,
    }


def _task_cluster_bootstrap(cell_task_scores, complete_case):
    """Task-cluster bootstrap over the complete-case task set, per cell.

    Descriptive sensitivity ONLY, non-inferential: whole tasks (clusters)
    are resampled with replacement and the must-hit-weighted delta is
    recomputed per resample. The seed is fixed per cell id, so the output
    is deterministic and independent of argument order.
    """
    out = {
        "label": (
            "task-cluster bootstrap: descriptive sensitivity only, "
            "non-inferential; whole tasks (clusters) resampled with "
            "replacement, must-hit-weighted delta per resample"
        ),
        "basis": "complete-case",
        "seed": BOOTSTRAP_SEED,
        "iterations": BOOTSTRAP_ITERATIONS,
        "cells": {},
    }
    for cid in sorted(cell_task_scores):
        ts = cell_task_scores[cid]
        ids = [t for t in complete_case if t in ts]
        if not ids:
            out["cells"][cid] = None
            continue
        rng = random.Random(f"{BOOTSTRAP_SEED}:{cid}")
        deltas = []
        for _ in range(BOOTSTRAP_ITERATIONS):
            sample = [ids[rng.randrange(len(ids))] for _ in ids]
            n = sum(ts[t]["n_must_hits"] for t in sample)
            if not n:
                continue
            cold = sum(ts[t]["cold_hits"] for t in sample)
            loaded = sum(ts[t]["loaded_hits"] for t in sample)
            deltas.append(100 * (loaded - cold) / n)
        if not deltas:
            out["cells"][cid] = None
            continue
        deltas.sort()

        def pct(p, d=deltas):
            return round(d[min(len(d) - 1, int(p * len(d)))], 1)

        out["cells"][cid] = {
            "n_resamples": len(deltas),
            "delta_pp_p2_5": pct(0.025),
            "delta_pp_p50": pct(0.5),
            "delta_pp_p97_5": pct(0.975),
        }
    return out


def _classify_invalidation(reason):
    lowered = (reason or "").lower()
    if any(m in lowered for m in HARNESS_CENSOR_MARKERS):
        return "harness_censored"
    return "natural_completion"


def _cell_invalidation(meta):
    """Per-arm invalidation counts for one cell, natural-completion vs
    harness-censored, from the run's recorded exclusions."""
    planned = len(meta.get("tasks") or {})
    arms = {
        arm: {"n_invalid": 0, "natural_completion": 0, "harness_censored": 0}
        for arm in ("cold", "loaded")
    }
    judging = {"n_tasks": 0, "natural_completion": 0, "harness_censored": 0}
    for e in meta.get("excluded_tasks") or []:
        kind = _classify_invalidation(e.get("reason"))
        failed_arms = e.get("failed_arms") or []
        if failed_arms:
            for arm in failed_arms:
                if arm in arms:
                    arms[arm]["n_invalid"] += 1
                    arms[arm][kind] += 1
        else:
            judging["n_tasks"] += 1
            judging[kind] += 1
    for arm in arms.values():
        arm["rate_pct"] = (
            round(100 * arm["n_invalid"] / planned, 1) if planned else None
        )
    return {"planned_tasks": planned, "arms": arms, "judging": judging}


def matrix_scores(run_dirs):
    """Aggregate completed cell runs into one model x effort matrix.

    Each run directory is one cell (consumer model x effort). Scores are
    recomputed from each run's raw judge outputs, never read from its
    scores.json, so every matrix number derives from committed raw data
    and every denominator is computed.
    """
    cells = {}
    cell_task_scores = {}
    cell_repeat_tasks = {}
    for run_dir in run_dirs:
        run_dir = Path(run_dir)
        if not (run_dir / "run-meta.json").is_file():
            raise MatrixError(f"{run_dir}: not a run directory (no run-meta.json)")
        meta, judge_outputs, order_key, _, _ = load_run_dir(run_dir)
        scores = score_run(meta, judge_outputs, order_key)
        model = meta.get("model", "unknown")
        effort = meta.get("effort", "default")
        cell_id = f"{model}@{effort}"
        if cell_id in cells:
            raise MatrixError(
                f"two run directories describe the same cell {cell_id}: "
                f"{cells[cell_id]['run_dir']} and {run_dir}; pass one run "
                f"per cell"
            )
        repeats = int(meta.get("repeats", 1))
        cell_task_scores[cell_id] = scores["tasks"]
        repeats_detail = scores.get("repeats_detail")
        cell_repeat_tasks[cell_id] = (
            repeats_detail["per_repeat"] if repeats_detail else None
        )
        cells[cell_id] = {
            "run_id": meta.get("run_id", run_dir.name),
            "run_dir": str(run_dir),
            "model": model,
            "effort": effort,
            "preregistered": bool(meta.get("preregistered")),
            "repeats": repeats,
            "replicated": repeats > 1,
            "judge_repeats": int(meta.get("judge_repeats", 1)),
            "n_tasks": len(scores["tasks"]),
            "excluded_tasks": scores["excluded_tasks"],
            "invalidation": _cell_invalidation(meta),
            "skills": scores["skills"],
        }
        disagreement = scores.get("judge_disagreement")
        if disagreement:
            # Publish the panel disagreement rate in matrix outputs too.
            cells[cell_id]["judge_disagreement"] = {
                "n_marks": disagreement["n_marks"],
                "n_disagreed": disagreement["n_disagreed"],
                "disagreement_rate_pct": disagreement["disagreement_rate_pct"],
            }
            adjudication = disagreement.get("adjudication")
            if adjudication:
                # Adjudicated cells also publish their adjudication rate
                # and any judge-failure floor exclusions per cell, which
                # is the by-model and by-effort breakdown.
                floor = disagreement.get("failure_floor") or {}
                cells[cell_id]["judge_disagreement"]["adjudication"] = {
                    "n_slot_marks": adjudication["n_slot_marks"],
                    "n_disputed_slot_marks":
                        adjudication["n_disputed_slot_marks"],
                    "n_adjudicated": adjudication["n_adjudicated"],
                    "n_unresolved": adjudication["n_unresolved"],
                    "adjudication_rate_pct":
                        adjudication["adjudication_rate_pct"],
                    "by_slot": disagreement.get("by_slot"),
                    "by_arm": disagreement.get("by_arm"),
                    "floor_excluded_comparisons":
                        floor.get("floor_excluded_comparisons") or [],
                }

    # Available-case: every task valid in that cell. Complete-case: only
    # tasks valid in EVERY cell (the multi-cell extension of paired
    # exclusion), so complete-case numbers are comparable across cells.
    complete_case = sorted(
        set.intersection(*(set(ts) for ts in cell_task_scores.values()))
    ) if cell_task_scores else []
    for cid, cell in cells.items():
        ts = cell_task_scores[cid]
        cell["aggregate"] = _aggregate_over(
            ts, sorted(ts), cell["repeats"], "available-case",
            per_repeat=cell_repeat_tasks[cid],
        )
        cell["aggregate_complete_case"] = _aggregate_over(
            ts, complete_case, cell["repeats"], "complete-case",
            per_repeat=cell_repeat_tasks[cid],
        )

    # Per-model-column endpoint complete-case (pre-registered: see
    # _endpoint_complete_case): H1, H2, retention, and H4 must use this
    # narrower set, not the cross-model one above -- no other model's
    # column, and no interior cell, can remove a task from it.
    for model in sorted({c["model"] for c in cells.values()}):
        by_effort = {c["effort"]: cid for cid, c in cells.items()
                     if c["model"] == model}
        low_id = by_effort.get("low")
        endpoint_id = by_effort.get(_confirmatory_endpoint_effort(model))
        if low_id is None or endpoint_id is None:
            continue
        endpoint_cc = _endpoint_complete_case(
            cell_task_scores, low_id, endpoint_id)
        for cid in (low_id, endpoint_id):
            cells[cid]["aggregate_endpoint_complete_case"] = _aggregate_over(
                cell_task_scores[cid], endpoint_cc, cells[cid]["repeats"],
                "endpoint complete-case",
                per_repeat=cell_repeat_tasks[cid],
            )

    cell_order = sorted(
        cells,
        key=lambda c: (cells[c]["model"],
                       EFFORT_ORDER.get(cells[c]["effort"], len(EFFORT_ORDER)),
                       cells[c]["effort"]),
    )
    skills = {}
    for name in sorted({s for c in cells.values() for s in c["skills"]}):
        row = {}
        for cid in cell_order:
            s = cells[cid]["skills"].get(name)
            if s is None:
                row[cid] = None
                continue
            row[cid] = {
                "n_tasks": s["tasks"],
                "n_must_hits": s["n_must_hits"],
                "cold_hits": s["cold_hits"],
                "loaded_hits": s["loaded_hits"],
                **_rates(s["cold_hits"], s["loaded_hits"], s["n_must_hits"]),
                "label": _small_n_label(s["tasks"], cells[cid]["repeats"]),
            }
        skills[name] = row
    for c in cells.values():
        del c["skills"]  # the per-skill view lives under "skills"
    panel_cells = [c for c in cells.values() if c.get("judge_disagreement")]
    overall_marks = sum(c["judge_disagreement"]["n_marks"]
                        for c in panel_cells)
    overall_disagreed = sum(c["judge_disagreement"]["n_disagreed"]
                            for c in panel_cells)
    adj_cells = [c["judge_disagreement"]["adjudication"] for c in panel_cells
                 if c["judge_disagreement"].get("adjudication")]
    overall = {
        "n_marks": overall_marks,
        "n_disagreed": overall_disagreed,
        "disagreement_rate_pct": (
            round(100 * overall_disagreed / overall_marks, 1)
            if overall_marks else None
        ),
    }
    if adj_cells:
        slot_marks = sum(a["n_slot_marks"] for a in adj_cells)
        adjudicated = sum(a["n_adjudicated"] for a in adj_cells)
        overall["adjudication"] = {
            "n_slot_marks": slot_marks,
            "n_disputed_slot_marks": sum(a["n_disputed_slot_marks"]
                                         for a in adj_cells),
            "n_adjudicated": adjudicated,
            "n_unresolved": sum(a["n_unresolved"] for a in adj_cells),
            "adjudication_rate_pct": (
                round(100 * adjudicated / slot_marks, 1)
                if slot_marks else None
            ),
        }
    return {
        "cells": cells,
        "cell_order": cell_order,
        "skills": skills,
        "per_skill_note": (
            "per-skill PASS/FAIL verdicts are deliberately suppressed in "
            "lattice outputs and subordinated to the per-cell run "
            "reports; skills appear here as rates only"
        ),
        "complete_case_tasks": complete_case,
        "retention": _retention(cells),
        "views": _views(cells),
        "h4_matched_low_high": _h4_matched_low_high(
            cells, cell_task_scores, cell_repeat_tasks),
        "hypothesis_verdicts": _hypothesis_verdicts(cells),
        "invalidation_note": (
            "invalidation rates by model x effort x arm live on each "
            "cell's invalidation block; natural-completion invalidations "
            "(the run finished but was invalid) are distinguished from "
            "harness-censored ones (timeout or the pinned output ceiling)"
        ),
        "judge_panel_overall": overall if panel_cells else None,
        "bootstrap": _task_cluster_bootstrap(cell_task_scores, complete_case),
    }


def matrix_text(matrix):
    return json.dumps(matrix, indent=2, sort_keys=True) + "\n"


def _fmt_delta(v):
    return "-" if v is None else f"{v:+.1f}"


def _fmt_rate(v):
    return "-" if v is None else f"{v}%"


def _aggregate_row(cid, a):
    ceiling = a.get("ceiling_tasks") or {}
    mean = a.get("mean_over_repeats")
    if mean:
        # Replicated endpoint cells are visually distinct: the rates and
        # delta are BOLD means over repeats, marked with the repeat count.
        # Single-run interior cells stay unmarked and carry no
        # uncertainty display.
        n_rep = mean["n_repeats"]
        cold = f"**{_fmt_rate(mean['cold_rate_pct'])}** (R{n_rep} mean)"
        loaded = f"**{_fmt_rate(mean['loaded_rate_pct'])}** (R{n_rep} mean)"
        delta = f"**{_fmt_delta(mean['delta_pp'])}** (R{n_rep} mean)"
    else:
        cold = (f"{a['cold_hits']}/{a['n_expectations']}"
                f" ({_fmt_rate(a['cold_rate_pct'])})")
        loaded = (f"{a['loaded_hits']}/{a['n_expectations']}"
                  f" ({_fmt_rate(a['loaded_rate_pct'])})")
        delta = _fmt_delta(a['delta_pp'])
    return (
        f"| {cid} | {a['n_tasks']} "
        f"| {cold}"
        f" | {loaded}"
        f" | {delta}"
        f" | {_fmt_delta(a['delta_pp_equal_skill'])}"
        f" | {_fmt_rate(a['headroom_recovered_pct'])}"
        f" | {ceiling.get('cold', 0)}/{ceiling.get('loaded', 0)}"
        f" | {a['label']} |"
    )


def render_matrix(matrix):
    cells = matrix["cells"]
    order = matrix["cell_order"]
    lines = [
        "# Matrix report: must-hit rates per skill x cell",
        "",
        "A cell is one consumer model x effort run. Every number below is",
        "recomputed from that run's raw judge outputs, and every denominator",
        "is computed from the data. All cells are small-n: treat every rate",
        "and delta as directional, not inferential.",
        "",
        "Two bases are reported. Available-case uses every task valid in",
        "that cell. Complete-case restricts every cell to the tasks valid",
        "in ALL cells (paired exclusion extended across the matrix), so",
        "only complete-case numbers are comparable across cells. Delta is",
        "must-hit-weighted; eq-skill delta weights every skill equally;",
        "headroom is the share of the cold arm's remaining headroom the",
        "loaded arm recovered, (L - C) / (1 - C), undefined at cold",
        "ceiling; ceiling counts tasks where an arm hit every must-hit.",
        "",
        "Replicated endpoint cells (run at --repeats N) show BOLD mean",
        "rates over repeats, marked (RN mean); single-run interior cells",
        "are unmarked point values with no uncertainty display. Per-skill",
        "PASS/FAIL verdicts are deliberately suppressed in lattice",
        "outputs; skills appear as rates only, subordinated to the",
        "per-cell run reports.",
        "",
        "## Cells (available-case)",
        "",
        "| Cell | Tasks | Cold | Loaded | Delta (pp) | Eq-skill delta (pp) "
        "| Headroom | Ceiling c/l | n |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for cid in order:
        lines.append(_aggregate_row(cid, cells[cid]["aggregate"]))
    lines += [
        "",
        "| Cell | Run | Preregistered |",
        "|---|---|---|",
    ]
    for cid in order:
        c = cells[cid]
        lines.append(
            f"| {cid} | {c['run_id']} "
            f"| {'yes' if c['preregistered'] else 'NO'} |"
        )
    complete = matrix.get("complete_case_tasks") or []
    lines += [
        "",
        "## Complete-case aggregate (tasks valid in every cell)",
        "",
        f"Common complete-case task set ({len(complete)}): "
        f"{', '.join(complete) or 'none'}.",
        "",
        "| Cell | Tasks | Cold | Loaded | Delta (pp) | Eq-skill delta (pp) "
        "| Headroom | Ceiling c/l | n |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for cid in order:
        lines.append(_aggregate_row(cid, cells[cid]["aggregate_complete_case"]))
    lines += ["", "## Retention (low vs max, complete-case)", ""]
    retention = matrix.get("retention") or []
    overridden = [r for r in retention if r.get("endpoint_effort") != "max"]
    if overridden:
        lines.append(
            "Note: " + "; ".join(
                f"{r['model']}'s endpoint below is low vs "
                f"{r['endpoint_effort']} (not max) per the posted "
                f"endpoint amendment" for r in overridden
            ) + ". Every 'D(max)' figure below is that model's amended "
            "endpoint value, not a literal max-effort run."
        )
        lines.append("")
    if retention:
        for r in retention:
            ratio = ("R = " + format(r["retention_ratio_R"], ".3f")
                     if r["retention_ratio_R"] is not None else "R undefined")
            lines.append(
                f"- {r['model']}: D(low) {_fmt_delta(r['delta_low_pp'])} pp, "
                f"D(max) {_fmt_delta(r['delta_max_pp'])} pp, {ratio} "
                f"({r['note']})"
            )
    else:
        lines.append(
            "- Not applicable: retention needs a low and a max cell for "
            "the same model."
        )
    verdicts = matrix.get("hypothesis_verdicts") or {}
    lines += [
        "",
        "## Hypothesis verdicts (confirmatory: H1 and H2 only)",
        "",
        f"Rule: {verdicts.get('rule', '')}.",
        "",
        f"Scope: {verdicts.get('scope', '')}.",
        "",
    ]
    h1 = verdicts.get("h1") or {}
    h2 = verdicts.get("h2") or {}

    def _endpoint_override_note(entries):
        overridden = {model: e["endpoint_effort"]
                      for model, e in entries.items()
                      if e.get("endpoint_effort") not in (None, "max")}
        if not overridden:
            return None
        parts = "; ".join(f"{m} = low vs {eff}" for m, eff in
                           sorted(overridden.items()))
        return (f"Note: 'max' columns below are literal max-effort for "
                f"every model except: {parts} (posted endpoint amendment).")

    if h1 or h2:
        if h1:
            lines += [
                "### H1 (cold-arm endpoint gain)",
                "",
                "| Model | cold(low) | cold(max) | Difference (pp) | Verdict |",
                "|---|---|---|---|---|",
            ]
            for model, e in sorted(h1.items()):
                lines.append(
                    f"| {model} | {_fmt_rate(e.get('cold_low_pct'))} "
                    f"| {_fmt_rate(e.get('cold_max_pct'))} "
                    f"| {_fmt_delta(e.get('difference_pp'))} "
                    f"| {e['verdict']} |"
                )
            note = _endpoint_override_note(h1)
            if note:
                lines += ["", note]
            lines.append("")
        if h2:
            lines += [
                "### H2 (delta shrinkage low to max)",
                "",
                "| Model | D(low) pp | D(max) pp | Shrinkage (pp) | Verdict |",
                "|---|---|---|---|---|",
            ]
            for model, e in sorted(h2.items()):
                lines.append(
                    f"| {model} | {_fmt_delta(e.get('delta_low_pp'))} "
                    f"| {_fmt_delta(e.get('delta_max_pp'))} "
                    f"| {_fmt_delta(e.get('shrinkage_pp'))} "
                    f"| {e['verdict']} |"
                )
            note = _endpoint_override_note(h2)
            if note:
                lines += ["", note]
            lines.append("")
        lines.append(
            "H3 and H4 are EXPLORATORY (see the cross-model views); "
            "H1 and H2 above are the only confirmatory hypotheses."
        )
    else:
        lines.append(
            "- Not evaluable: H1/H2 need a low and a max endpoint cell "
            "for at least one model."
        )
    views = matrix.get("views") or {}
    matched = (views.get("matched_effort") or {}).get("efforts") or {}
    lines += [
        "",
        "## Cross-model views (complete-case)",
        "",
        "### Matched effort (primary)",
        "",
        "Models compared at the same explicit effort level. Effort-",
        "invariant models (effort none) never appear here.",
        "",
    ]
    if matched:
        lines += [
            "| Effort | Model | Cell | Delta (pp) | Eq-skill delta (pp) "
            "| Headroom | n |",
            "|---|---|---|---|---|---|---|",
        ]
        for effort in [e for e in MATCHED_EFFORTS if e in matched]:
            for model, entry in matched[effort].items():
                lines.append(
                    f"| {effort} | {model} | {entry['cell']} "
                    f"| {_fmt_delta(entry['delta_pp'])} "
                    f"| {_fmt_delta(entry['delta_pp_equal_skill'])} "
                    f"| {_fmt_rate(entry['headroom_recovered_pct'])} "
                    f"| {entry['label']} |"
                )
    else:
        lines.append("- No cells at an explicit effort level.")
    defaults = (views.get("defaults_as_shipped") or {}).get("models") or {}
    lines += [
        "",
        "### Defaults as shipped (secondary, labeled)",
        "",
        "Each model at its own shipped default effort. The levels differ",
        "across models, so cross-model differences here conflate model",
        "tier and effort level.",
        "",
    ]
    if defaults:
        lines += [
            "| Model | Effort | Cell | Delta (pp) | Eq-skill delta (pp) "
            "| Headroom | n |",
            "|---|---|---|---|---|---|---|",
        ]
        for model, entry in defaults.items():
            lines.append(
                f"| {model} | {entry['effort']} | {entry['cell']} "
                f"| {_fmt_delta(entry['delta_pp'])} "
                f"| {_fmt_delta(entry['delta_pp_equal_skill'])} "
                f"| {_fmt_rate(entry['headroom_recovered_pct'])} "
                f"| {entry['label']} |"
            )
    else:
        lines.append("- No cells at a default or none effort.")
    lines += [
        "",
        "### H3 visibility tags (EXPLORATORY)",
        "",
        "H3 (visibility-tag heterogeneity) is exploratory only: computed",
        "over tagged task strata outside this matrix, with no confirmatory",
        "verdict; no lattice number here feeds it.",
    ]
    h4 = (views.get("h4_shrinkage") or {}).get("entries") or []
    lines += [
        "",
        "### H4 shrinkage side by side (EXPLORATORY, directional only)",
        "",
        "Per-model low-to-max delta shrinkage; exploratory, nothing",
        "stronger than direction is claimed. Effort-invariant models are",
        "excluded from all effort-trend views.",
        "",
    ]
    if h4:
        h4_overridden = [r for r in h4 if r.get("endpoint_effort") != "max"]
        if h4_overridden:
            lines.append(
                "Note: " + "; ".join(
                    f"{r['model']} is low vs {r['endpoint_effort']} (not "
                    f"max) per the posted endpoint amendment -- NOT yet "
                    f"the amendment's matched low-to-high basis for every "
                    f"model (amendment section (c) is a disclosed, "
                    f"deferred follow-up); Sonnet/Opus below remain "
                    f"low-to-max" for r in h4_overridden
                )
            )
            lines.append("")
        lines += [
            "| Model | D(low) pp | D(max) pp | R |",
            "|---|---|---|---|",
        ]
        for r in h4:
            ratio = (format(r["retention_ratio_R"], ".3f")
                     if r["retention_ratio_R"] is not None else "undefined")
            lines.append(
                f"| {r['model']} | {_fmt_delta(r['delta_low_pp'])} "
                f"| {_fmt_delta(r['delta_max_pp'])} | {ratio} |"
            )
    else:
        lines.append(
            "- Not applicable: H4 needs a low and a max cell for at least "
            "one model."
        )
    matched_h4 = matrix.get("h4_matched_low_high") or {}
    matched_entries = matched_h4.get("entries") or []
    lines += [
        "",
        "## H4 matched low-to-high view (EXPLORATORY, additive)",
        "",
        "Matched cross-model shrinkage on one common low-to-high basis for",
        "all three effort-bearing models, so the comparison is basis-",
        "matched. This fulfills the deferred follow-up disclosed in the",
        "posted amendment (effort-sweep-amendment-2026-07-10-fable-"
        "endpoint.md section (c)). Exploratory and directional only; it is",
        "additive and changes no H1/H2/retention/H4 number or verdict above.",
        "Fable's high is its replicated confirmatory endpoint; for Sonnet",
        "and Opus, high is an interior cell (not their confirmatory",
        "endpoint, which is max), descriptive only -- see the table's own",
        "High cell column for whether each is single-run or replicated.",
        "",
    ]
    if matched_entries:
        lines += [
            "| Model | D(low) pp | D(high) pp | Shrinkage (pp) | High cell |",
            "|---|---|---|---|---|",
        ]
        for e in matched_entries:
            if e["high_is_confirmatory_endpoint"]:
                high_label = f"replicated confirmatory endpoint (R{e['high_cell_repeats']} mean)"
            elif e["high_cell_interior_single_run"]:
                high_label = "interior, single-run (no repeats, descriptive only)"
            else:
                high_label = f"interior, R{e['high_cell_repeats']} mean (descriptive only)"
            lines.append(
                f"| {e['model']} | {_fmt_delta(e['delta_low_pp'])} "
                f"| {_fmt_delta(e['delta_high_pp'])} "
                f"| {_fmt_delta(e['shrinkage_pp'])} | {high_label} |"
            )
    else:
        lines.append(
            "- Not applicable: the matched view needs a low and a high cell "
            "for at least one model."
        )
    lines += ["", "## Judge panel disagreement and adjudication", ""]
    panel_cells = [cid for cid in order if cells[cid].get("judge_disagreement")]
    if panel_cells:
        for cid in panel_cells:
            d = cells[cid]["judge_disagreement"]
            rate = d["disagreement_rate_pct"]
            adj = d.get("adjudication")
            if adj:
                adj_rate = adj["adjudication_rate_pct"]
                floor = adj.get("floor_excluded_comparisons") or []
                lines.append(
                    f"- {cid}: {d['n_disagreed']} of {d['n_marks']} marks "
                    f"disagreed ({'-' if rate is None else f'{rate}%'}); "
                    f"{adj['n_adjudicated']} of {adj['n_slot_marks']} "
                    f"report-slot marks adjudicated "
                    f"({'-' if adj_rate is None else f'{adj_rate}%'}), kept "
                    f"in every denominator; {adj['n_unresolved']} "
                    f"unresolved (judge-failure exclusion)"
                    + (f"; floor-excluded comparisons: {', '.join(floor)}"
                       if floor else "")
                )
            else:
                lines.append(
                    f"- {cid}: {d['n_disagreed']} of {d['n_marks']} marks "
                    f"disagreed ({'-' if rate is None else f'{rate}%'}), "
                    f"excluded from both arms"
                )
        overall = matrix.get("judge_panel_overall")
        if overall:
            rate = overall["disagreement_rate_pct"]
            line = (
                f"- Overall: {overall['n_disagreed']} of "
                f"{overall['n_marks']} marks disagreed "
                f"({'-' if rate is None else f'{rate}%'})"
            )
            adj = overall.get("adjudication")
            if adj:
                adj_rate = adj["adjudication_rate_pct"]
                line += (
                    f"; {adj['n_adjudicated']} of {adj['n_slot_marks']} "
                    f"report-slot marks adjudicated "
                    f"({'-' if adj_rate is None else f'{adj_rate}%'}), "
                    f"{adj['n_unresolved']} unresolved"
                )
            lines.append(line)
    else:
        lines.append("- No two-judge-panel cells in this matrix.")
    lines += [
        "",
        "## Invalidation rates by model x effort x arm",
        "",
        "Natural completion: the run finished but was invalid (for",
        "example a missing Answers section or a cross-model fallback).",
        "Harness censored: the harness cut the run off (timeout or the",
        "pinned output ceiling). Judging rows count task exclusions from",
        "judge or adjudicator failures.",
        "",
        "| Cell | Arm | Invalid / planned tasks | Rate | Natural "
        "completion | Harness censored |",
        "|---|---|---|---|---|---|",
    ]
    for cid in order:
        inv = cells[cid].get("invalidation") or {}
        planned = inv.get("planned_tasks", 0)
        for arm in ("cold", "loaded"):
            a = (inv.get("arms") or {}).get(arm) or {}
            lines.append(
                f"| {cid} | {arm} | {a.get('n_invalid', 0)}/{planned} "
                f"| {_fmt_rate(a.get('rate_pct'))} "
                f"| {a.get('natural_completion', 0)} "
                f"| {a.get('harness_censored', 0)} |"
            )
        j = inv.get("judging") or {}
        if j.get("n_tasks"):
            lines.append(
                f"| {cid} | judging | {j['n_tasks']}/{planned} | - "
                f"| {j.get('natural_completion', 0)} "
                f"| {j.get('harness_censored', 0)} |"
            )
    bootstrap = matrix.get("bootstrap") or {}
    lines += [
        "",
        "## Task-cluster bootstrap (descriptive, non-inferential)",
        "",
        f"{bootstrap.get('label', '')}. Seed {bootstrap.get('seed')}, "
        f"{bootstrap.get('iterations')} iterations, "
        f"{bootstrap.get('basis')} basis.",
        "",
    ]
    boot_cells = bootstrap.get("cells") or {}
    if any(boot_cells.get(cid) for cid in order):
        lines += [
            "| Cell | Delta p2.5 | Delta p50 | Delta p97.5 | Resamples |",
            "|---|---|---|---|---|",
        ]
        for cid in order:
            b = boot_cells.get(cid)
            if b is None:
                lines.append(f"| {cid} | - | - | - | - |")
                continue
            lines.append(
                f"| {cid} | {_fmt_delta(b['delta_pp_p2_5'])} "
                f"| {_fmt_delta(b['delta_pp_p50'])} "
                f"| {_fmt_delta(b['delta_pp_p97_5'])} "
                f"| {b['n_resamples']} |"
            )
    else:
        lines.append("- Not applicable: no complete-case tasks to resample.")
    lines += [
        "",
        "## Per skill x cell",
        "",
        "Cell format: cold hits/n (rate), loaded hits/n (rate), delta in",
        "percentage points, then that cell's n label. Per-skill PASS/FAIL",
        "is deliberately suppressed in lattice outputs; this table",
        "reports rates only.",
        "",
        "| Skill | " + " | ".join(order) + " |",
        "|---|" + "---|" * len(order),
    ]
    for skill in sorted(matrix["skills"]):
        row = [skill]
        for cid in order:
            e = matrix["skills"][skill].get(cid)
            if e is None:
                row.append("-")
                continue
            row.append(
                f"cold {e['cold_hits']}/{e['n_must_hits']}"
                f" ({_fmt_rate(e['cold_rate_pct'])}),"
                f" loaded {e['loaded_hits']}/{e['n_must_hits']}"
                f" ({_fmt_rate(e['loaded_rate_pct'])}),"
                f" delta {_fmt_delta(e['delta_pp'])} pp"
                f" [{e['label']}]"
            )
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Notes", ""]
    noted = False
    for cid in order:
        if cells[cid]["excluded_tasks"]:
            noted = True
            lines.append(
                f"- {cid}: excluded tasks "
                f"{', '.join(cells[cid]['excluded_tasks'])} "
                f"(denominator shrunk accordingly)"
            )
    if not noted:
        lines.append("- No excluded tasks in any cell.")
    lines.append("")
    return "\n".join(lines)


def replay_diff(run_dir):
    """Byte-diff recomputed scores.json and REPORT.md against committed files.

    Returns a list of mismatch descriptions; empty means the committed
    outputs reproduce exactly from the committed raw judge data.
    """
    run_dir = Path(run_dir)
    new_scores, new_report = recompute(run_dir)
    errs = []
    for name, new_text in (("scores.json", new_scores), ("REPORT.md", new_report)):
        path = run_dir / name
        if not path.is_file():
            errs.append(f"{run_dir.name}: missing {name}")
            continue
        old = path.read_text(encoding="utf-8")
        if old != new_text:
            errs.append(
                f"{run_dir.name}: {name} does not reproduce from raw judge "
                f"outputs (committed file differs from recomputation)"
            )
    return errs
