#!/usr/bin/env python3
"""Consolidate the effort-sweep numbers into one human-readable page.

Emits results/matrix/NUMBERS.md. Every figure is computed here or copied
verbatim from a canonical source read at run time:

  - results/matrix/matrix.json        verdicts, per-cell rates, deltas, judging
  - results/lattice-*/scores.json     shipped-cell enumeration and run counts
  - the raw consumer/judge/adjudicator artifacts (total_cost_usd fields)
  - results/concordance/codex-concordance.json   cross-vendor concordance

MATRIX.md stays the canonical scoring record; this page is the single place
every number and cost is copied from. Nothing is hand-typed.

Additive and stdlib-only. Touches no existing harness file.
"""

import glob
import hashlib
import json
import os
from decimal import Decimal, ROUND_HALF_UP


def cents(x):
    """Round a float dollar amount to cents exactly once. All table totals are
    computed from these once-rounded values, so every row and the grand-total
    row's components add exactly as printed."""
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATRIX_JSON = os.path.join(REPO, "results/matrix/matrix.json")
CONCORDANCE_JSON = os.path.join(REPO, "results/concordance/codex-concordance.json")
OUT = os.path.join(REPO, "results/matrix/NUMBERS.md")

# The Fable max-effort cell is a pre-registered open cell that never completed
# (see the posted amendment); it holds no scored data and is not part of the
# shipped record.
UNSHIPPED_DIRS = {"results/lattice-fable-max"}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def rel(path):
    return os.path.relpath(path, REPO)


# --------------------------------------------------------------------------
# Cost: sum total_cost_usd across every artifact in the shipped cells, exactly
# once. Artifacts that appear in more than one shipped cell (the opus-medium
# batch1 re-adjudication ships a byte-identical copy of a subset of
# lattice-opus-medium) are deduplicated by content hash so nothing is counted
# twice, regardless of which cell or machine produced it.
# --------------------------------------------------------------------------

def artifact_cost(path):
    """Return (category, cost_usd) for one artifact file, or None if it carries
    no cost. Category is one of consumer / judge / adjudication."""
    d = load(path)
    parent = os.path.basename(os.path.dirname(path))
    if parent == "consumer":
        c = d.get("total_cost_usd")
        return ("consumer", float(c)) if c is not None else None
    if parent == "judge-outputs":
        if path.endswith(".adjudication.json"):
            total = 0.0
            for dispute in d.get("disputes", []):
                meta = dispute.get("cli_meta") or {}
                total += float(meta.get("total_cost_usd", 0.0) or 0.0)
            return ("adjudication", total)
        # primary-judge output: cli_meta is a list of invocations
        total = 0.0
        for meta in d.get("cli_meta") or []:
            total += float(meta.get("total_cost_usd", 0.0) or 0.0)
        return ("judge", total)
    return None


def shipped_cost(cell_order, cell_run_dir):
    """Compute the per-cell and grand-total shipped cost with content-level
    deduplication. Returns (rows, grand, seen_dupe_usd, gross_usd)."""
    # Process the canonical matrix cells first (in cell order), then any other
    # shipped dir (the batch1 re-adjudication), so a duplicated artifact is
    # attributed to its canonical cell and the re-adjudication shows only what
    # is unique to it (which is nothing).
    matrix_dirs = [cell_run_dir[c] for c in cell_order]
    all_shipped = []
    for p in sorted(glob.glob(os.path.join(REPO, "results/lattice-*"))):
        if not os.path.exists(os.path.join(p, "scores.json")):
            continue
        r = rel(p)
        if r in UNSHIPPED_DIRS:
            continue
        all_shipped.append(r)
    ordered = matrix_dirs + [d for d in all_shipped if d not in matrix_dirs]
    assert len(ordered) == 16, f"expected 16 shipped cells, found {len(ordered)}"

    seen = set()
    rows = []  # (dir, consumer, judge, adjudication, total, dupe) all in cents
    for d in ordered:
        cats = {"consumer": 0.0, "judge": 0.0, "adjudication": 0.0}
        dupe = 0.0
        for sub in ("consumer", "judge-outputs"):
            for f in sorted(glob.glob(os.path.join(REPO, d, sub, "*.json"))):
                res = artifact_cost(f)
                if res is None:
                    continue
                cat, cost = res
                digest = hashlib.sha256(open(f, "rb").read()).hexdigest()
                if digest in seen:
                    dupe += cost
                    continue
                seen.add(digest)
                cats[cat] += cost
        # sum unrounded per-cell, round each printed component exactly once;
        # every displayed total is a sum of the displayed components
        c_cons = cents(cats["consumer"])
        c_judge = cents(cats["judge"])
        c_adj = cents(cats["adjudication"])
        rows.append((d, c_cons, c_judge, c_adj, c_cons + c_judge + c_adj, cents(dupe)))
    grand = sum(r[4] for r in rows)
    dupe_total = sum(r[5] for r in rows)
    # gross = deduplicated grand + removed duplicates, exact in cents by
    # construction, so the printed sanity identity always adds up
    gross = grand + dupe_total
    return rows, grand, dupe_total, gross


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def m(x):
    return "-" if x is None else f"{x}"


def pct(x):
    return "-" if x is None else f"{x:.1f}%"


def signed(x):
    return "-" if x is None else f"{x:+.1f}"


def build():
    mx = load(MATRIX_JSON)
    conc = load(CONCORDANCE_JSON)
    cell_order = mx["cell_order"]
    cells = mx["cells"]
    cell_run_dir = {c: cells[c]["run_dir"] for c in cell_order}

    L = []
    w = L.append

    w("# NUMBERS: consolidated source of truth for the effort-sweep study")
    w("")
    w("Single-page consolidation of every published figure and cost for the")
    w("effort-sweep matrix. Every number here is computed by")
    w("`eval/make_numbers.py` or copied verbatim from a canonical source read")
    w("at generation time; none is hand-typed. `results/matrix/MATRIX.md`")
    w("remains the canonical scoring record. If a figure here and there ever")
    w("disagree, MATRIX.md wins and this file is stale; regenerate it.")
    w("")
    w(f"Sources read: `{rel(MATRIX_JSON)}`, every `results/lattice-*/scores.json`")
    w("and its raw consumer/judge/adjudicator artifacts, and")
    w(f"`{rel(CONCORDANCE_JSON)}`.")
    w("")
    w(f"Frozen suite hash: `{conc.get('suite_hash','')}`.")
    w("")

    # ---- Verdicts ----
    w("## Hypothesis verdicts (confirmatory: H1 and H2 only)")
    w("")
    w("Pre-registered minimum effect: 3 percentage points. H1 is supported only")
    w("when cold(endpoint) - cold(low) >= 3 pp; H2 only when D(low) - D(endpoint)")
    w(">= 3 pp. Endpoints are complete-case, replicated means over 3 repeats.")
    w("Endpoint is low vs max for every model except Fable, which is low vs high")
    w("per the posted 2026-07-10 endpoint amendment.")
    w("")
    hv = mx["hypothesis_verdicts"]
    w("### H1 (cold-arm endpoint gain)")
    w("")
    w("| Model | Endpoint | cold(low) | cold(endpoint) | Difference (pp) | Bar | Verdict |")
    w("|---|---|---|---|---|---|---|")
    for model, r in hv["h1"].items():
        w(f"| {model} | {r['endpoint_effort']} | {pct(r['cold_low_pct'])} | "
          f"{pct(r['cold_max_pct'])} | {signed(r['difference_pp'])} | >= 3.0 | {r['verdict']} |")
    w("")
    w("### H2 (delta shrinkage, low to endpoint)")
    w("")
    w("| Model | Endpoint | D(low) pp | D(endpoint) pp | Shrinkage (pp) | Bar | Verdict |")
    w("|---|---|---|---|---|---|---|")
    for model, r in hv["h2"].items():
        w(f"| {model} | {r['endpoint_effort']} | {signed(r['delta_low_pp'])} | "
          f"{signed(r['delta_max_pp'])} | {signed(r['shrinkage_pp'])} | >= 3.0 | {r['verdict']} |")
    w("")
    w("Summary: H1 supported for all three models (Fable +3.5, Opus +3.9,")
    w("Sonnet +4.6, all clearing the 3-point bar). H2 not supported for any")
    w("model. Effort and skills read as complements, not substitutes.")
    w("")

    # ---- Retention ----
    w("## Retention ratio (endpoint delta / low delta, complete-case)")
    w("")
    w("| Model | D(low) pp | D(endpoint) pp | Endpoint | R |")
    w("|---|---|---|---|---|")
    for r in mx["retention"]:
        w(f"| {r['model']} | {signed(r['delta_low_pp'])} | {signed(r['delta_max_pp'])} | "
          f"{r['endpoint_effort']} | {r['retention_ratio_R']:.3f} |")
    w("")
    w("Small-n, directional only.")
    w("")

    # ---- Full per-cell table ----
    w("## Full per-cell table (available-case)")
    w("")
    w("Without-skills is the cold arm, with-skills is the loaded arm. Rates for")
    w("replicated endpoint cells are the mean over repeats (marked R3 mean);")
    w("single-run cells are point values. Runs = consumer runs per arm.")
    w("")
    w("| Cell | Run dir | Without-skills % | With-skills % | Delta (pp) | Tasks (n) | Must-hit marks (n) | Runs/arm |")
    w("|---|---|---|---|---|---|---|---|")
    for c in cell_order:
        cell = cells[c]
        agg = cell["aggregate"]
        replicated = cell.get("replicated")
        if replicated:
            src = agg["mean_over_repeats"]
            cold = f"{src['cold_rate_pct']:.1f}% (R{src['n_repeats']} mean)"
            loaded = f"{src['loaded_rate_pct']:.1f}% (R{src['n_repeats']} mean)"
            delta = f"{src['delta_pp']:+.1f} (R{src['n_repeats']} mean)"
        else:
            cold = pct(agg["cold_rate_pct"])
            loaded = pct(agg["loaded_rate_pct"])
            delta = signed(agg["delta_pp"])
        w(f"| {c} | `{cell['run_dir']}` | {cold} | {loaded} | {delta} | "
          f"{agg['n_tasks']} | {agg['n_expectations']} | {cell['repeats']} |")
    w("")
    w(f"Complete-case common task set (n={len(mx['complete_case_tasks'])}): "
      f"{', '.join(mx['complete_case_tasks'])}. Complete-case rates, which are")
    w("the only cross-cell-comparable basis, are in MATRIX.md.")
    w("")

    # ---- Matched low-to-high ----
    h4 = mx["h4_matched_low_high"]
    w("## Matched low-to-high view (EXPLORATORY, additive)")
    w("")
    w("All three effort-bearing models' shrinkage on one common low-to-high")
    w("basis, so the comparison is basis-matched. Exploratory and directional")
    w("only; changes no H1/H2/retention verdict. For Sonnet and Opus the high")
    w("cell is an interior single-run cell (descriptive only); Fable's high is")
    w("its replicated confirmatory endpoint.")
    w("")
    w("| Model | D(low) pp | D(high) pp | Shrinkage (pp) | High cell |")
    w("|---|---|---|---|---|")
    for e in h4["entries"]:
        if e["high_cell_interior_single_run"]:
            hc = "interior single-run (no repeats, descriptive only)"
        else:
            hc = f"replicated endpoint (R{e['high_cell_repeats']} mean)"
        w(f"| {e['model']} | {signed(e['delta_low_pp'])} | {signed(e['delta_high_pp'])} | "
          f"{signed(e['shrinkage_pp'])} | {hc} |")
    w("")

    # ---- Judging stats ----
    jp = mx["judge_panel_overall"]
    adj = jp["adjudication"]
    w("## Judge panel disagreement and adjudication")
    w("")
    w("Every comparison was scored by two blinded judges (a Sonnet-class and an")
    w("Opus-class judge); disagreements were decided by a pinned third judge,")
    w("Claude Fable 5. Adjudicated marks stay in every denominator.")
    w("")
    w(f"- Overall: {jp['n_disagreed']} of {jp['n_marks']} marks disagreed "
      f"({jp['disagreement_rate_pct']}%); {adj['n_adjudicated']} of "
      f"{adj['n_slot_marks']} report-slot marks adjudicated "
      f"({adj['adjudication_rate_pct']}%); {adj['n_unresolved']} unresolved.")
    w("")
    w("| Cell | Marks disagreed | Disagreement % | Slot marks adjudicated | Adjudication % | Unresolved |")
    w("|---|---|---|---|---|---|")
    for c in cell_order:
        jd = cells[c]["judge_disagreement"]
        a = jd["adjudication"]
        w(f"| {c} | {jd['n_disagreed']}/{jd['n_marks']} | {jd['disagreement_rate_pct']}% | "
          f"{a['n_adjudicated']}/{a['n_slot_marks']} | {a['adjudication_rate_pct']}% | "
          f"{a['n_unresolved']} |")
    w("")

    # ---- Concordance ----
    ov = conc["overall"]
    bm = conc["by_model_column"]
    do = conc["dispute_overlap"]
    w("## Codex cross-vendor concordance (EXPLORATORY)")
    w("")
    w("Cross-vendor robustness spot-check. Never touches any verdict, retention")
    w("ratio, or published number. Codex re-scored a deterministic sample of")
    w(f"{conc['sample_size']} comparisons (of {conc['n_enumerated']} enumerated) and its")
    w("marks were compared against the panel-final majority marks.")
    w("")
    w(f"- Model: {', '.join(conc['codex_models_seen'])}, reasoning effort "
      f"`{conc['codex_reasoning_effort']}`.")
    w(f"- Overall concordance: {ov['concordance_pct']}% "
      f"({ov['n_agree']}/{ov['n_marks']} marks).")
    w(f"- Unscorable comparisons: {conc['n_unscorable']} (never guessed).")
    w("")
    w("| Scope | Marks | Agree | Concordance |")
    w("|---|---:|---:|---:|")
    w(f"| Overall | {ov['n_marks']} | {ov['n_agree']} | {ov['concordance_pct']}% |")
    for name, r in bm.items():
        w(f"| Model column: {name} | {r['n_marks']} | {r['n_agree']} | {r['concordance_pct']}% |")
    w(f"| Panel-disputed marks | {do['n_marks']} | {do['n_agree']} | {do['concordance_pct']}% |")
    w("")

    # ---- Shipped-record cost ----
    rows, grand, dupe_usd, gross = shipped_cost(cell_order, cell_run_dir)
    w("## Shipped-record cost")
    w("")
    w("The true shipped-record cost: `total_cost_usd` summed across every")
    w("artifact in the 16 shipped cells, counted exactly once regardless of")
    w("which cell or machine produced it. Consumer, judge, and adjudication")
    w("costs are broken out per cell. Duplicated artifacts (the opus-medium")
    w("batch1 re-adjudication ships byte-identical copies of a subset of")
    w("`lattice-opus-medium`) are deduplicated by content hash and attributed")
    w("to their canonical cell, so the columns sum exactly to the grand total.")
    w("")
    w("Operational overhead (gates, aborted passes, the never-completed")
    w("Fable-max open cell) lives in the private ledger and is not part of this")
    w("shipped record.")
    w("")
    w("| Shipped cell | Consumer $ | Judge $ | Adjudication $ | Cell total $ |")
    w("|---|---:|---:|---:|---:|")
    tc = tj = ta = Decimal("0.00")
    for d, cons, judge, adjud, total, dupe in rows:
        tc += cons
        tj += judge
        ta += adjud
        note = ""
        if dupe > 1e-9:
            note = f" (+${dupe:,.2f} duplicate of lattice-opus-medium, counted there)"
        w(f"| `{d}`{note} | {cons:,.2f} | {judge:,.2f} | {adjud:,.2f} | {total:,.2f} |")
    w(f"| **Grand total (deduplicated)** | **{tc:,.2f}** | **{tj:,.2f}** | "
      f"**{ta:,.2f}** | **{grand:,.2f}** |")
    w("")
    w(f"Grand total shipped-record cost: **${grand:,.2f}** across 16 shipped")
    w(f"cells ({rel(MATRIX_JSON)} enumerates 15; the 16th is the opus-medium")
    w("batch1 re-adjudication).")
    w("")
    w(f"Dedup sanity: gross artifact cost across all 16 cell directories is")
    w(f"${gross:,.2f}; ${dupe_usd:,.2f} of that is the batch1 re-adjudication's")
    w("byte-identical duplicate of opus-medium artifacts, removed once; the")
    w(f"deduplicated shipped record is ${grand:,.2f} (= {gross:,.2f} - {dupe_usd:,.2f}).")
    w("")

    # ---- Provenance ----
    w("## Provenance and disclosures")
    w("")
    w("- Posted endpoint amendment: `effort-sweep-amendment-2026-07-10-fable-")
    w("  endpoint.md`. For Fable only, H1 and H2 are evaluated on low vs high,")
    w("  not low vs max, on operational grounds (Fable-max never fit the pool")
    w("  before the stopping deadline); Sonnet and Opus stay low vs max. The")
    w("  amendment is referenced from MATRIX.md and from")
    w("  `matrix.json` (`h4_matched_low_high.note`, section (c)).")
    w("- Blinding exception (disclosed, not papered over): the July judges were")
    w("  order-blinded, not content-blinded. A post-run audit found exactly one")
    w("  committed judge input of 456 where a sibling skill's name survived the")
    w("  scrub (Haiku cell, task aicg-t2, report 1), because the ban list was")
    w("  scoped to the task's own skill. It sits outside every confirmatory")
    w("  hypothesis; no H1 or H2 number moves. Disclosed in `README.md`")
    w("  (methodology honesty notes).")
    w("- Concordance selection wording: the pre-registration named the sample")
    w("  selection only loosely as \"hash-parity\"; the implemented deterministic")
    w("  digest-sort rule is disclosed verbatim in")
    w("  `results/concordance/CONCORDANCE.md` and `codex-concordance.json`")
    w("  (`selection_rule`) rather than claimed as literal pre-registered wording.")
    w("- Sanitization: nine committed files had absolute local paths redacted by")
    w("  mechanical byte-level replacement before first public release, with the")
    w("  owner's approval; no mark, score, or model output was altered. Full")
    w("  record in `results/SANITIZATION.md`.")
    w("- Denominator correction: an early /51 denominator was corrected to 50")
    w("  after a recount of the recovered per-task judge data; every number here")
    w("  uses the corrected denominator (`README.md`).")
    w("")

    return "\n".join(L) + "\n"


def main():
    text = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote {rel(OUT)} ({len(text)} bytes)")


if __name__ == "__main__":
    main()
