#!/usr/bin/env python3
"""Pre-registered Codex cross-vendor concordance sample (exploratory only).

Selects 50 committed judge-input comparisons deterministically, re-scores
each on Codex (a non-Claude vendor), and reports the per-mark concordance
against the panel-final (majority-resolved) marks that scores.json already
scored. This is EXPLORATORY ONLY: it never touches any verdict, retention
ratio, or published number.

Selection (frozen construction, documented exactly):
    For every committed judge-input comparison across the 15 scored
    lattice cells (results/lattice-*/judge-inputs/*.json, excluding
    lattice-fable-max, which has no scored data, and the adjudication
    artifact dir lattice-opus-medium-batch1-adjudicate, which is not a
    scored cell), compute

        digest = SHA256(SUITE_HASH + cell + filename)   # UTF-8, no sep

    where SUITE_HASH is the frozen suite hash (the run-meta freeze
    task_file_sha256), `cell` is the cell directory basename (e.g.
    "lattice-fable-medium"), and `filename` is the judge-input basename
    (e.g. "aicg-t2.json"). Sort all comparisons by digest hex ascending
    and take the first 50. The construction reuses the section-6 PRIMARY
    rule shape SHA256(suite_hash + identifier); rerunning reproduces the
    same 50 exactly.

    NOTE on frozen wording: the pre-registration calls this selection
    "hash-parity". Parity is a one-of-two split and does not by itself
    pick exactly 50; the deterministic ordering (sort by digest, take
    first 50) is the open-implementation part, filled in here as the
    simplest mechanical rule with no human choice. No even/odd parity
    pre-filter is applied; documented here for transparency. This choice
    cannot affect any verdict (the sample is exploratory).

Panel-final marks are reconstructed from the committed judge-outputs with
the harness's own scoring functions (panel_adjudicated / slot_disputes),
which reproduce scores.json's per_expectation exactly. A "mark" is one
(comparison, expectation_id, arm) with arm in {cold, loaded}.

stdlib only (plus the local eval.harness scoring module).
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL_DIR))
from harness import scoring  # noqa: E402

REPO_ROOT = EVAL_DIR.parent
RESULTS = REPO_ROOT / "results"
OUT_DIR = RESULTS / "concordance"
MARKS_DIR = OUT_DIR / "_marks"          # per-comparison Codex checkpoints
RAW_DIR = OUT_DIR / "_raw"              # per-comparison raw Codex stdout

SUITE_HASH = "b378c79644280bb93fb8ac71d0cadcfe301fd15b226dfaec852b619a2aa1c890"
SAMPLE_SIZE = 50
PRIMARIES = ["claude-opus-4-8", "claude-sonnet-5"]

CODEX_BIN = "/Applications/Codex.app/Contents/Resources/codex"
CODEX_EFFORT = "high"
CODEX_MAX_WORKERS = 5

SELECTION_RULE = (
    "digest = SHA256(SUITE_HASH + cell + filename), UTF-8 with no "
    "separator; sort all committed judge-input comparisons across the 15 "
    "scored cells by digest hex ascending; take the first "
    f"{SAMPLE_SIZE}. SUITE_HASH={SUITE_HASH}. No parity pre-filter."
)

OUTPUT_FORMAT_APPENDIX = """

## Required output format

Respond with ONLY a single JSON object and nothing else (no markdown
code fences, no commentary before or after). It must match exactly:

{"expectations": [{"expectation_id": "<id>", "report_1": {"hit": <true|false>, "evidence": "<verbatim quote or empty string>"}, "report_2": {"hit": <true|false>, "evidence": "<verbatim quote or empty string>"}}], "comparative_verdict": "<one line>"}

Include exactly one entry per expectation id listed above, in order.
"""


def scored_cells():
    cells = []
    for d in sorted(os.listdir(RESULTS)):
        p = RESULTS / d
        if not d.startswith("lattice-"):
            continue
        if d == "lattice-fable-max":
            continue          # pre-registered open cell, no scored data
        if "adjudicate" in d:
            continue          # adjudication artifact, not a scored cell
        if not (p / "judge-inputs").is_dir():
            continue
        cells.append(d)
    return cells


def enumerate_comparisons():
    """Every committed judge-input comparison across the 15 scored cells."""
    out = []
    for cell in scored_cells():
        ji = RESULTS / cell / "judge-inputs"
        for f in sorted(os.listdir(ji)):
            if not f.endswith(".json"):
                continue
            digest = hashlib.sha256(
                (SUITE_HASH + cell + f).encode("utf-8")
            ).hexdigest()
            pid = f[:-5]  # strip .json -> pair id (task or task-rN)
            out.append({
                "cell": cell,
                "filename": f,
                "pid": pid,
                "digest": digest,
                "judge_input": str((ji / f).relative_to(REPO_ROOT)),
            })
    return out


def select_sample():
    comps = enumerate_comparisons()
    comps.sort(key=lambda c: c["digest"])
    return comps[:SAMPLE_SIZE]


# ---- panel-final reconstruction -------------------------------------------

def _model_column(cell):
    body = cell[len("lattice-"):]
    return body.split("-")[0]  # fable | opus | sonnet | haiku


def _task_id(pid):
    # pid is task_id, or task_id-rN for replicated cells.
    if "-r" in pid and pid.rsplit("-r", 1)[1].isdigit():
        return pid.rsplit("-r", 1)[0]
    return pid


def panel_final(cell, pid):
    """Return (resolved, disputed_arm_marks, mh_ids, order_entry).

    resolved: {mh_id: {"cold": bool, "loaded": bool}} panel-final marks.
    disputed_arm_marks: set of (mh_id, arm) the two primary judges split on.
    """
    cd = RESULTS / cell
    rm = json.load(open(cd / "run-meta.json"))
    order = json.load(open(cd / "order-key.json"))["order"]
    mh_ids = rm["tasks"][_task_id(pid)]["must_hit_ids"]
    per_judge = {}
    for jm in PRIMARIES:
        per_judge[jm] = json.load(
            open(cd / "judge-outputs" / f"{pid}.{jm}.json"))["judgments"]
    adj_path = cd / "judge-outputs" / f"{pid}.adjudication.json"
    adj = json.load(open(adj_path)) if adj_path.exists() else None
    resolved, _stats = scoring.panel_adjudicated(
        per_judge, adj, order[pid], mh_ids)
    disputes = scoring.slot_disputes(per_judge, mh_ids)  # (mh_id, slot)
    oe = order[pid]
    disputed_arm = {(mh, oe[slot]) for mh, slot in disputes}
    return resolved, disputed_arm, mh_ids, oe


# ---- Codex re-scoring ------------------------------------------------------

def build_prompt(comp):
    ji = json.load(open(REPO_ROOT / comp["judge_input"]))
    return ji["prompt"] + OUTPUT_FORMAT_APPENDIX


def _extract_json_objects(text):
    """Yield every balanced top-level {...} substring that parses as JSON."""
    depth = 0
    start = None
    in_str = False
    esc = False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    chunk = text[start:i + 1]
                    try:
                        yield json.loads(chunk)
                    except json.JSONDecodeError:
                        pass
                    start = None


def parse_marks(raw, mh_ids):
    """Parse the last valid judge JSON; return {mh_id:{report_1,report_2}}."""
    best = None
    for obj in _extract_json_objects(raw):
        if isinstance(obj, dict) and isinstance(obj.get("expectations"), list):
            best = obj
    if best is None:
        return None
    marks = {}
    for e in best["expectations"]:
        try:
            # Normalize wrapper punctuation only (e.g. "(a)" -> "a", "1." ->
            # "1"); never remaps which expectation a mark belongs to.
            eid = str(e["expectation_id"]).strip().strip("()[].: ").strip()
            marks[eid] = {
                "report_1": bool(e["report_1"]["hit"]),
                "report_2": bool(e["report_2"]["hit"]),
            }
        except (KeyError, TypeError):
            continue
    if not all(m in marks for m in mh_ids):
        return None
    return marks


def run_codex(prompt):
    proc = subprocess.run(
        [CODEX_BIN, "exec", "--sandbox", "read-only",
         "--skip-git-repo-check", "-c",
         f'model_reasoning_effort="{CODEX_EFFORT}"', "-"],
        input=prompt, capture_output=True, text=True, timeout=600,
    )
    return proc.stdout + "\n" + proc.stderr


def _score_one(comp, idx):
    ckpt = MARKS_DIR / f"{idx:02d}.json"
    if ckpt.exists():
        return json.load(open(ckpt))
    mh_ids = panel_final(comp["cell"], comp["pid"])[2]
    prompt = build_prompt(comp)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    t0 = time.time()
    marks = None
    attempts = 0
    raw = ""
    for attempt in range(2):  # one retry on parse failure
        attempts = attempt + 1
        raw = run_codex(prompt)
        (RAW_DIR / f"{idx:02d}.a{attempts}.txt").write_text(raw)
        marks = parse_marks(raw, mh_ids)
        if marks is not None:
            break
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec = {
        "idx": idx,
        "cell": comp["cell"],
        "filename": comp["filename"],
        "pid": comp["pid"],
        "digest": comp["digest"],
        "codex_model": _codex_model_from_raw(raw),
        "codex_effort": CODEX_EFFORT,
        "attempts": attempts,
        "started_utc": started,
        "finished_utc": finished,
        "wall_s": round(time.time() - t0, 1),
        "unscorable": marks is None,
        "codex_marks": marks,  # blinded report_1/report_2 hits, or None
    }
    ckpt.write_text(json.dumps(rec, indent=2))
    return rec


def _codex_model_from_raw(raw):
    for line in raw.splitlines():
        s = line.strip()
        if s.startswith("model:"):
            return s.split(":", 1)[1].strip()
    return None


def cmd_select(args):
    sample = select_sample()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "_selection.json").write_text(json.dumps({
        "selection_rule": SELECTION_RULE,
        "suite_hash": SUITE_HASH,
        "sample_size": SAMPLE_SIZE,
        "n_enumerated": len(enumerate_comparisons()),
        "cells": scored_cells(),
        "sample": sample,
    }, indent=2))
    print(f"selected {len(sample)} of {len(enumerate_comparisons())} "
          f"comparisons -> {OUT_DIR / '_selection.json'}")


def cmd_run(args):
    sample = select_sample()
    MARKS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with cf.ThreadPoolExecutor(max_workers=CODEX_MAX_WORKERS) as ex:
        futs = {ex.submit(_score_one, c, i): i
                for i, c in enumerate(sample)}
        for fut in cf.as_completed(futs):
            r = fut.result()
            print(f"[{r['idx']:02d}] {r['cell']}/{r['filename']} "
                  f"unscorable={r['unscorable']} {r['wall_s']}s")


def aggregate():
    """Compute concordance from the committed checkpoints; return report."""
    sample = select_sample()
    recs = []
    for idx, comp in enumerate(sample):
        ckpt = MARKS_DIR / f"{idx:02d}.json"
        if not ckpt.exists():
            raise SystemExit(f"missing checkpoint {ckpt}; run first")
        recs.append(json.load(open(ckpt)))

    overall = {"n": 0, "agree": 0}
    by_col = {}
    dispute = {"n": 0, "agree": 0}
    unscorable = []
    per_comparison = []
    codex_models = set()

    for rec in recs:
        col = _model_column(rec["cell"])
        by_col.setdefault(col, {"n": 0, "agree": 0})
        if rec.get("codex_model"):
            codex_models.add(rec["codex_model"])
        if rec["unscorable"] or rec["codex_marks"] is None:
            unscorable.append({"idx": rec["idx"], "cell": rec["cell"],
                               "filename": rec["filename"]})
            per_comparison.append({**_comp_meta(rec), "unscorable": True})
            continue
        resolved, disputed_arm, mh_ids, oe = panel_final(rec["cell"], rec["pid"])
        arm_to_slot = {oe["report_1"]: "report_1", oe["report_2"]: "report_2"}
        cm = rec["codex_marks"]
        c_n = c_a = 0
        marks_detail = []
        for mh in mh_ids:
            if mh not in resolved:
                continue  # panel judge-failure exclusion: not scorable
            for arm in ("cold", "loaded"):
                slot = arm_to_slot[arm]
                codex_hit = bool(cm[mh][slot])
                panel_hit = bool(resolved[mh][arm])
                agree = codex_hit == panel_hit
                overall["n"] += 1
                overall["agree"] += agree
                by_col[col]["n"] += 1
                by_col[col]["agree"] += agree
                c_n += 1
                c_a += agree
                disputed = (mh, arm) in disputed_arm
                if disputed:
                    dispute["n"] += 1
                    dispute["agree"] += agree
                marks_detail.append({
                    "expectation": mh, "arm": arm,
                    "codex_hit": codex_hit, "panel_final_hit": panel_hit,
                    "agree": agree, "panel_internally_disputed": disputed,
                })
        per_comparison.append({
            **_comp_meta(rec), "unscorable": False,
            "codex_marks_blinded": cm,  # raw report_1/report_2 hits
            "order_key": oe,            # slot -> arm unblinding used
            "n_marks": c_n, "n_agree": c_a,
            "concordance_pct": _pct(c_a, c_n), "marks": marks_detail,
        })

    report = {
        "exploratory_only": True,
        "note": ("Cross-vendor concordance spot-check. EXPLORATORY ONLY: "
                 "never touches any verdict, retention ratio, or published "
                 "number. Panel-final marks are the majority-resolved marks "
                 "scores.json scored; concordance is per (comparison, "
                 "expectation, arm) mark."),
        "selection_rule": SELECTION_RULE,
        "selection": [
            {"rank": i, "cell": c["cell"], "filename": c["filename"],
             "pid": c["pid"], "digest": c["digest"],
             "judge_input": c["judge_input"]}
            for i, c in enumerate(sample)
        ],
        "n_enumerated": len(enumerate_comparisons()),
        "suite_hash": SUITE_HASH,
        "sample_size": SAMPLE_SIZE,
        "codex_binary": CODEX_BIN,
        "codex_models_seen": sorted(codex_models),
        "codex_reasoning_effort": CODEX_EFFORT,
        "judge_instrument": ("committed judge-input 'prompt' field (the "
                             "frozen panel instrument + blinded content) "
                             "plus a strict JSON output-format appendix"),
        "n_comparisons": len(recs),
        "n_unscorable": len(unscorable),
        "unscorable": unscorable,
        "overall": {"n_marks": overall["n"], "n_agree": overall["agree"],
                    "concordance_pct": _pct(overall["agree"], overall["n"])},
        "by_model_column": {
            c: {"n_marks": v["n"], "n_agree": v["agree"],
                "concordance_pct": _pct(v["agree"], v["n"])}
            for c, v in sorted(by_col.items())},
        "dispute_overlap": {
            "definition": ("of the marks the two Claude primary judges "
                           "split on internally, how often Codex sides with "
                           "the panel-final majority"),
            "n_marks": dispute["n"], "n_agree": dispute["agree"],
            "concordance_pct": _pct(dispute["agree"], dispute["n"])},
        "per_comparison": per_comparison,
    }
    return report


def _comp_meta(rec):
    return {k: rec[k] for k in ("idx", "cell", "filename", "pid", "digest",
                                "codex_model", "codex_effort", "attempts",
                                "started_utc", "finished_utc", "wall_s")}


def _pct(a, n):
    return round(100 * a / n, 1) if n else None


def _md(report):
    r = report
    o = r["overall"]
    lines = []
    lines.append("# Codex cross-vendor concordance sample")
    lines.append("")
    lines.append("**EXPLORATORY ONLY.** This cross-vendor spot-check never "
                 "touches any verdict, retention ratio, or published number. "
                 "It is a pre-registered robustness check (section 3 of the "
                 "effort-sweep pre-registration).")
    lines.append("")
    lines.append(f"- Overall concordance: **{o['concordance_pct']}%** "
                 f"({o['n_agree']}/{o['n_marks']} marks) over n={r['n_comparisons']} "
                 f"comparisons.")
    lines.append(f"- Unscorable comparisons: **{r['n_unscorable']}** "
                 f"(Codex output unparseable after one retry; never guessed).")
    lines.append(f"- Re-scored on Codex: models {', '.join(r['codex_models_seen'])}, "
                 f"reasoning effort `{r['codex_reasoning_effort']}`.")
    lines.append("")
    lines.append("A *mark* is one (comparison, expectation, arm) binary "
                 "HIT/MISS. Concordance is the fraction of marks where Codex "
                 "agrees with the panel-final (majority-resolved) mark that "
                 "scores.json scored.")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(f"- **Selection (deterministic):** {r['selection_rule']}")
    lines.append(f"- **Judge instrument:** {r['judge_instrument']}. Codex saw "
                 "the identical blinded reports (report_1 / report_2) the "
                 "panel saw; slots were unblinded to arms with the committed "
                 "order key only for scoring.")
    lines.append("- **Panel-final marks** were reconstructed from the "
                 "committed judge-outputs with the harness's own "
                 "`panel_adjudicated` scoring (two-of-three majority, "
                 "adjudicator on disputes); this reproduces scores.json's "
                 "per-expectation marks exactly (verified, 0 mismatches on "
                 "all non-replicated cells).")
    lines.append("- **Parsing:** strict JSON extraction, one retry on parse "
                 "failure; a still-unparseable comparison is recorded "
                 "`unscorable` and excluded from denominators, never guessed.")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| Scope | Marks | Agree | Concordance |")
    lines.append("|---|---:|---:|---:|")
    lines.append(f"| Overall | {o['n_marks']} | {o['n_agree']} | {o['concordance_pct']}% |")
    for c, v in r["by_model_column"].items():
        lines.append(f"| Model column: {c} | {v['n_marks']} | {v['n_agree']} | {v['concordance_pct']}% |")
    d = r["dispute_overlap"]
    lines.append(f"| Panel-disputed marks | {d['n_marks']} | {d['n_agree']} | {d['concordance_pct']}% |")
    lines.append("")
    lines.append(f"**Dispute overlap.** {d['definition']}: "
                 f"{d['n_agree']}/{d['n_marks']} "
                 f"({d['concordance_pct']}%).")
    lines.append("")
    lines.append("Raw per-comparison marks, Codex model id + effort, and "
                 "timestamps are in `codex-concordance.json`.")
    lines.append("")
    return "\n".join(lines)


def cmd_aggregate(args):
    report = aggregate()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "codex-concordance.json").write_text(json.dumps(report, indent=2))
    (OUT_DIR / "CONCORDANCE.md").write_text(_md(report))
    o = report["overall"]
    print(f"overall {o['concordance_pct']}% ({o['n_agree']}/{o['n_marks']}), "
          f"unscorable={report['n_unscorable']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("select").set_defaults(func=cmd_select)
    sub.add_parser("run").set_defaults(func=cmd_run)
    sub.add_parser("aggregate").set_defaults(func=cmd_aggregate)
    args = ap.parse_args()
    args.func(args)
