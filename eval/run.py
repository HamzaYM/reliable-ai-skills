#!/usr/bin/env python3
"""Eval harness entrypoint. Stdlib only; requires Python 3.11+.

Modes (one per invocation):

  python3 eval/run.py --tasks your_tasks.jsonl --ab     full blinded A/B
  python3 eval/run.py --suite golden --ab               A/B on the golden suite
  python3 eval/run.py --tasks your_tasks.jsonl --freeze pre-register must-hits
  python3 eval/run.py --validate                        CI gate (no API calls)
  python3 eval/run.py --replay results/<run-id>         recompute + diff scores
  python3 eval/run.py --report results/<run-id>         re-emit scores + report
  python3 eval/run.py --matrix-report results/<a> ...   aggregate cells
  python3 eval/run.py --concordance-sample results/<a> ...  Codex sample

See eval/README.md for the full flag reference.
"""
import argparse
import concurrent.futures
import datetime
import json
import os
import random
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import EVAL_DIR, FIXTURES_DIR, REPO_ROOT, RESULTS_DIR, SKILLS_DIR, TASKS_DIR
from harness import concordance as concordance_mod
from harness import consumer as consumer_mod
from harness import fixtures as fixtures_mod
from harness import freeze as freeze_mod
from harness import judge as judge_mod
from harness import report as report_mod
from harness import sanitize as sanitize_mod
from harness import scoring as scoring_mod
from harness import scrub as scrub_mod
from harness import tasks as tasks_mod

SUITES = {"golden": TASKS_DIR / "golden-suite.jsonl"}

# Dry-run cost model, recalibrated from the 2026-07-10 two-task smoke
# (run 20260710T003211Z-example-sonnet-medium). Token counts include cache
# reads (which dominate: measured consumer mean ~403k, judge mean ~44k);
# the $/Mtok band is the measured effective blended rate over those
# cache-heavy totals, not the list price.
EST_CONSUMER_TOKENS = 400_000
EST_JUDGE_TOKENS = 44_000
EST_USD_PER_MTOK = (1.0, 1.4)


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def write_atomic(path, text):
    """Write via same-directory temp file + os.replace: no torn artifacts."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def utc_now():
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def resolve_tasks_path(args):
    if args.tasks and args.suite:
        fail("--tasks and --suite are mutually exclusive")
    if args.suite:
        path = SUITES.get(args.suite)
        if path is None:
            fail(f"unknown suite {args.suite!r}; known: {', '.join(SUITES) or 'none yet'}")
        if not path.is_file():
            fail(f"suite file not found: {path}")
        return path
    if args.tasks:
        path = Path(args.tasks)
        if not path.is_file():
            fail(f"task file not found: {path}")
        return path
    fail("this mode needs --tasks FILE or --suite NAME")


def load_and_check(path):
    try:
        tasks = tasks_mod.load_tasks(path)
    except tasks_mod.TaskError as exc:
        fail(f"task file invalid:\n{exc}")
    ref_errs = tasks_mod.validate_refs(tasks)
    if ref_errs:
        fail("task references invalid:\n" + "\n".join(ref_errs))
    return tasks


# ---------------------------------------------------------------- freeze


def cmd_freeze(args):
    path = resolve_tasks_path(args)
    tasks = load_and_check(path)
    for fx in sorted({t["fixture"] for t in tasks}):
        fixtures_mod.load_manifest(fx)  # fails loudly if missing
    freeze_path, data = freeze_mod.write_freeze(path, tasks)
    print(f"froze {data['counts']['tasks']} tasks / "
          f"{data['counts']['must_hits']} must-hits -> {freeze_path}")
    print(f"task file sha256: {data['task_file_sha256']}")
    print("commit the freeze file before running --ab so the ordering proof "
          "is git history.")


# ---------------------------------------------------------------- validate


def cmd_validate(_args):
    errors, warnings = [], []
    denylist = sanitize_mod.load_denylist()
    print(f"denylist: {len(denylist)} private terms loaded"
          if denylist else "denylist: none present (eval/denylist.local.txt)")

    # 1. Skill frontmatter, at any depth, plus skill folders with no
    # SKILL.md at all.
    skill_mds = sorted(SKILLS_DIR.rglob("SKILL.md")) if SKILLS_DIR.is_dir() else []
    for skill_md in skill_mds:
        rel = skill_md.parent.relative_to(SKILLS_DIR)
        text = skill_md.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not m:
            errors.append(f"skills/{rel}/SKILL.md: missing frontmatter")
            continue
        fm = m.group(1)
        name = re.search(r"^name:\s*(\S+)\s*$", fm, re.MULTILINE)
        if not name or name.group(1) != skill_md.parent.name:
            errors.append(
                f"skills/{rel}/SKILL.md: frontmatter name must match folder "
                f"name {skill_md.parent.name!r}"
            )
        if not re.search(r"^description:\s*\S", fm, re.MULTILINE):
            errors.append(f"skills/{rel}/SKILL.md: missing description")
    if SKILLS_DIR.is_dir():
        for category in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
            for skill_dir in sorted(q for q in category.iterdir() if q.is_dir()):
                if not any(skill_dir.rglob("SKILL.md")):
                    errors.append(
                        f"skills/{skill_dir.relative_to(SKILLS_DIR)}: "
                        f"no SKILL.md anywhere under this skill folder"
                    )
    print(f"skills: checked frontmatter of {len(skill_mds)} skills")

    # 2. Task files: schema, refs, sanitization, freeze consistency.
    task_files = sorted(TASKS_DIR.glob("*.jsonl"))
    if not task_files:
        warnings.append("no task files under eval/tasks/")
    for path in task_files:
        try:
            tasks = tasks_mod.load_tasks(path)
        except tasks_mod.TaskError as exc:
            errors.append(str(exc))
            continue
        errors.extend(tasks_mod.validate_refs(tasks))
        errors.extend(tasks_mod.skill_frontmatter_preflight(tasks))
        prefixes = set()
        for fx in {t["fixture"] for t in tasks}:
            try:
                prefixes.update(
                    fixtures_mod.load_manifest(fx).get("fake_ticket_prefixes", [])
                )
            except fixtures_mod.FixtureError as exc:
                errors.append(str(exc))
        for task in tasks:
            e, w = sanitize_mod.lint_task(task, tuple(prefixes), denylist)
            errors.extend(e)
            warnings.extend(w)
        freeze_errs = freeze_mod.verify_freeze(path, tasks)
        if freeze_errs and freeze_mod.load_freeze(path) is None:
            warnings.append(f"{path.name}: not frozen yet ({freeze_errs[0]})")
        else:
            errors.extend(f"{path.name}: {e}" for e in freeze_errs)
        print(f"tasks: {path.name}: {len(tasks)} tasks checked")

    # 3. Fixtures: sanitization + deterministic rebuild against manifest.
    for fixture_dir in sorted(FIXTURES_DIR.iterdir()) if FIXTURES_DIR.is_dir() else []:
        if not fixture_dir.is_dir():
            continue
        name = fixture_dir.name
        try:
            manifest = fixtures_mod.load_manifest(name)
        except fixtures_mod.FixtureError as exc:
            errors.append(str(exc))
            continue
        prefixes = tuple(manifest.get("fake_ticket_prefixes", []))
        e, w = sanitize_mod.lint_fixture_files(fixture_dir, prefixes, denylist)
        errors.extend(e)
        warnings.extend(w)
        rebuild_errs = fixtures_mod.verify_fixture(name)
        errors.extend(rebuild_errs)
        print(f"fixture: {name}: rebuild "
              f"{'deterministic, matches manifest' if not rebuild_errs else 'MISMATCH'}")

    # 4. Replay-scoring of every committed run.
    run_dirs = sorted(p for p in RESULTS_DIR.glob("*") if p.is_dir()) \
        if RESULTS_DIR.is_dir() else []
    for run_dir in run_dirs:
        if not (run_dir / "run-meta.json").is_file():
            warnings.append(f"results/{run_dir.name}: no run-meta.json, skipped")
            continue
        try:
            errs = report_mod.replay_diff(run_dir)
        except Exception as exc:
            errs = [f"results/{run_dir.name}: replay failed: {exc}"]
        errors.extend(errs)
        print(f"replay: results/{run_dir.name}: "
              f"{'reproduces byte-for-byte' if not errs else 'MISMATCH'}")
    if not run_dirs:
        print("replay: no committed runs under results/ (nothing to replay)")

    for w in warnings:
        print(f"warning: {w}")
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        print(f"\nvalidate: FAIL ({len(errors)} errors, {len(warnings)} warnings)")
        sys.exit(1)
    print(f"\nvalidate: OK ({len(warnings)} warnings)")


# ---------------------------------------------------------------- replay/report


def cmd_replay(run_dir):
    run_dir = Path(run_dir)
    if not run_dir.is_dir():
        fail(f"not a run directory: {run_dir}")
    errs = report_mod.replay_diff(run_dir)
    if errs:
        for e in errs:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"replay: {run_dir} reproduces byte-for-byte from raw judge outputs")


def cmd_report(run_dir):
    run_dir = Path(run_dir)
    if not run_dir.is_dir():
        fail(f"not a run directory: {run_dir}")
    scores_text, report_text = report_mod.recompute(run_dir)
    write_atomic(run_dir / "scores.json", scores_text)
    write_atomic(run_dir / "REPORT.md", report_text)
    print(f"re-emitted {run_dir}/scores.json and {run_dir}/REPORT.md")


def cmd_matrix_report(args):
    run_dirs = [Path(p) for p in args.matrix_report]
    for d in run_dirs:
        if not d.is_dir():
            fail(f"not a run directory: {d}")
    try:
        matrix = report_mod.matrix_scores(run_dirs)
    except (report_mod.MatrixError, scoring_mod.ScoringError, OSError,
            json.JSONDecodeError, KeyError) as exc:
        fail(f"matrix aggregation failed: {exc}")
    out_dir = Path(args.out) if args.out else RESULTS_DIR / "matrix"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_atomic(out_dir / "matrix.json", report_mod.matrix_text(matrix))
    write_atomic(out_dir / "MATRIX.md", report_mod.render_matrix(matrix))
    print(f"matrix: {len(matrix['cells'])} cell(s) x "
          f"{len(matrix['skills'])} skill(s): {', '.join(matrix['cell_order'])}")
    print(f"wrote {out_dir}/matrix.json and {out_dir}/MATRIX.md")


def cmd_concordance_sample(args):
    run_dirs = [Path(p) for p in args.concordance_sample]
    for d in run_dirs:
        if not d.is_dir():
            fail(f"not a run directory: {d}")
    try:
        manifest = concordance_mod.build_manifest(run_dirs)
    except (concordance_mod.ConcordanceError, OSError,
            json.JSONDecodeError) as exc:
        fail(f"concordance sample failed: {exc}")
    out_dir = Path(args.out) if args.out else RESULTS_DIR / "concordance-sample"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_atomic(
        out_dir / "manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    print(f"concordance sample: selected {manifest['selected_n']} of target "
          f"{manifest['sample_size_target']} comparisons "
          f"(pool {manifest['pool_comparisons']}, even-parity "
          f"{manifest['parity_kept']})")
    if manifest["shortfall_note"]:
        print(f"note: {manifest['shortfall_note']}")
    print(f"wrote {out_dir}/manifest.json")


# ---------------------------------------------------------------- ab


def ab_pairs(tasks, repeats):
    for task in tasks:
        for r in range(1, repeats + 1):
            yield task, r, scoring_mod.pair_id(task["id"], r, repeats)


def effort_label(model, effort):
    """The recorded effort coordinate of a cell.

    An explicit --effort level records as itself; without the flag, an
    effort-invariant model (haiku-class, no effort knob) records as
    "none" and every other model as "default".
    """
    if effort:
        return effort
    if consumer_mod.effort_invariant_model(model):
        return "none"
    return "default"


def cell_slug(model, effort):
    """Filesystem-safe cell label for run ids: <model>-<effort label>.

    A run is one cell of the model x effort matrix, so both coordinates go
    into the default run id and cells never collide in results/. The
    effort coordinate is the recorded label: the explicit level, "default"
    without --effort, or "none" for effort-invariant models.
    """
    safe_model = re.sub(r"[^A-Za-z0-9._-]+", "-", model)
    return f"{safe_model}-{effort_label(model, effort)}"


def unavailable_by_design(model, effort):
    """Reason string when a model-effort combination cannot exist, else None.

    Effort-invariant models (haiku-class) have no effort knob, and the
    claude CLI accepts --effort for them with no stderr warning (verified
    live on 2.1.206), so the fail-closed stderr probe cannot prove the
    level was applied. Running such a cell would be a silent fallback
    stamped with an unverifiable effort, so it is refused and recorded.
    """
    if effort and consumer_mod.effort_invariant_model(model):
        return (
            f"{model} is an effort-invariant model with no effort knob; "
            f"the claude CLI accepts --effort for it without any warning, "
            f"so --effort {effort} cannot be verified as applied and the "
            f"cell is unavailable by design (run this model without "
            f"--effort; it is recorded as effort none)"
        )
    return None


def record_unavailable_cell(model, effort, reason):
    """Persist an unavailable-by-design cell record under results/.

    The record is the audit trail that the combination was refused rather
    than silently run at some other effort.
    """
    out_dir = RESULTS_DIR / "unavailable"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{cell_slug(model, effort)}.json"
    try:
        cli_version = consumer_mod.claude_version()
    except consumer_mod.ConsumerError:
        cli_version = None
    write_atomic(path, json.dumps({
        "status": "unavailable-by-design",
        "model": model,
        "effort": effort,
        "reason": reason,
        "claude_cli_version": cli_version,
        "recorded_at": utc_now(),
    }, indent=2, sort_keys=True) + "\n")
    return path


def judge_slug(model):
    """Filesystem-safe judge label for per-judge output file names."""
    return re.sub(r"[^A-Za-z0-9._-]+", "-", model)


def judge_file(out_dir, pid, judge_model):
    return out_dir / "judge-outputs" / f"{pid}.{judge_slug(judge_model)}.json"


def adjudication_file(out_dir, pid):
    """Adjudication record for one comparison: both primary marks with
    evidence quotes, the adjudicator's mark, and the final two-of-three
    majority result, persisted next to the judge outputs."""
    return out_dir / "judge-outputs" / f"{pid}.adjudication.json"


def load_adjudication(path):
    """Parse a persisted adjudication record. None when missing/invalid."""
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("disputes"), list):
        return None
    return data


def judge_slot_marks(judgments, mh_id, slot):
    """One primary judge's original votes for a report-slot mark: every
    vote's hit and evidence quote, plus the within-judge majority."""
    votes = []
    for j in judgments:
        for e in j["expectations"]:
            if e["expectation_id"] == mh_id:
                votes.append({"hit": bool(e[slot]["hit"]),
                              "evidence": e[slot].get("evidence", "")})
    return {
        "hit": scoring_mod.majority([v["hit"] for v in votes]),
        "votes": votes,
    }


def make_order_key(tasks, repeats, seed):
    rng = random.Random(seed)
    order = {}
    for task in sorted(tasks, key=lambda t: t["id"]):
        for r in range(1, repeats + 1):
            pid = scoring_mod.pair_id(task["id"], r, repeats)
            cold_first = rng.random() < 0.5
            order[pid] = (
                {"report_1": "cold", "report_2": "loaded"}
                if cold_first
                else {"report_1": "loaded", "report_2": "cold"}
            )
    return {"seed": seed, "order": order}


def stage_arm_workspace(built_dir, run_root, pid, arm, task):
    ws = fixtures_mod.stage_workspace(built_dir, run_root / f"{pid}-{arm}")
    if arm == "loaded":
        fixtures_mod.install_skill(
            ws, SKILLS_DIR / task["skill"], tasks_mod.skill_name_for(task)
        )
    else:
        # Cold-arm isolation is asserted, not assumed: the cold workspace
        # must contain no .claude directory at all (no skills, no settings,
        # no project config). User-level skills cannot reach the consumer
        # either: the allowlist (Read,Grep,Glob,Bash) exposes no Skill
        # tool, and run-meta records ambient_user_skills for audit.
        leftover = ws / ".claude"
        if leftover.exists():
            raise fixtures_mod.FixtureError(
                f"cold workspace {ws.name} contains a .claude directory; "
                f"the cold arm must be isolated from every skill and "
                f"config source"
            )
    return ws


def consumer_file(out_dir, pid, arm):
    return out_dir / "consumer" / f"{pid}-{arm}.json"


def load_consumer_result(path):
    """Parse a persisted consumer result. None when missing or invalid, so
    a torn or hand-damaged file re-runs instead of wedging every resume."""
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("answers"), str):
        return None
    return data


def run_one_consumer(job):
    """Executed in the worker pool. Returns (pid, arm, result_or_error)."""
    (task, pid, repeat, arm, built_dir, expected_snap, work_root, persona,
     model, effort) = job
    ws = None
    try:
        # Consumers have Bash, so a hostile or confused sibling run could
        # write into the shared built template; re-verify it (tree hash and
        # git refs) immediately before every staging.
        if fixtures_mod.snapshot(built_dir) != expected_snap:
            raise consumer_mod.ConsumerError(
                f"built fixture template {built_dir.name} was modified "
                f"during the run; aborting this staging"
            )
        ws = stage_arm_workspace(built_dir, work_root, pid, arm, task)
        skill_name = tasks_mod.skill_name_for(task) if arm == "loaded" else None
        prompt = consumer_mod.build_prompt(persona, task["prompt"], skill_name)
        pre_snap = fixtures_mod.snapshot(ws)
        result = consumer_mod.run_consumer(prompt, ws, model, effort=effort)
        post_snap = fixtures_mod.snapshot(ws)
        try:
            answers = consumer_mod.extract_answers(result["report"])
        except consumer_mod.ReportParseError as exc:
            return pid, arm, exc
        result.update(
            {
                "task": task["id"],
                "pair": pid,
                # Repeat index in every artifact: each repeat is its own
                # fresh workspace and fresh CLI invocation; no session
                # state is shared across repeats.
                "repeat": repeat,
                "arm": arm,
                "model_requested": model,
                "effort_requested": effort or "default",
                "answer_chars": len(answers),
                "sections": consumer_mod.parse_sections(result["report"]),
                "answers": answers,
                # Snapshot diff covers working files AND git refs, so
                # commits/fetches/branch deletions count as mutations too.
                "workspace_mutated": pre_snap != post_snap,
            }
        )
        if consumer_mod.effort_invariant_model(model):
            # No effort knob exists on this model, so the cell's effort
            # coordinate is "none" rather than "default".
            result["effort_requested"] = "none"
            result["effort_effective"] = "none"
        return pid, arm, result
    except (consumer_mod.ConsumerError, fixtures_mod.FixtureError,
            subprocess.SubprocessError, OSError) as exc:
        return pid, arm, exc
    finally:
        if ws is not None:
            shutil.rmtree(ws, ignore_errors=True)


def cmd_ab(args):
    tasks_path = resolve_tasks_path(args)
    tasks = load_and_check(tasks_path)

    # Freeze gate, verified against the FULL task file before any --skill
    # or --task-ids filter, so filtering never reads as frozen-task removal.
    freeze_errs = freeze_mod.verify_freeze(tasks_path, tasks)
    frozen = freeze_mod.load_freeze(tasks_path)
    preregistered = not freeze_errs
    if freeze_errs and not args.allow_unfrozen:
        fail(
            "freeze check failed; fix, re-freeze, or pass --allow-unfrozen "
            "(stamps the result preregistered: false):\n  "
            + "\n  ".join(freeze_errs)
        )
    if args.skill:
        tasks = [t for t in tasks if t["skill"] == args.skill
                 or tasks_mod.skill_name_for(t) == args.skill]
        if not tasks:
            fail(f"no tasks match --skill {args.skill!r}")
    if args.task_ids:
        wanted = [tid.strip() for tid in args.task_ids.split(",") if tid.strip()]
        known = {t["id"] for t in tasks}
        unknown = [tid for tid in wanted if tid not in known]
        if unknown:
            fail("--task-ids not in the task file: " + ", ".join(unknown))
        wanted_set = set(wanted)
        tasks = [t for t in tasks if t["id"] in wanted_set]

    judge_committed_out_dir = None
    if args.judge_committed:
        # Judging is decoupled by pre-registration and runs on committed
        # inputs at any time (prereg section 7). This mode never calls a
        # consumer model: it judges exactly the tasks whose consumer arms
        # for EVERY repeat are already persisted on disk from an earlier,
        # possibly still-incomplete or paused attempt, and leaves every
        # other task for that attempt to finish later. Requires --out
        # pointed at that attempt's directory (never a fresh one, since
        # there would be nothing committed to judge).
        if not args.out:
            fail("--judge-committed requires --out pointed at an existing "
                 "run directory with committed consumer artifacts")
        judge_committed_out_dir = Path(args.out)
        complete_ids = set()
        for t in tasks:
            pids = [scoring_mod.pair_id(t["id"], r, args.repeats)
                    for r in range(1, args.repeats + 1)]
            if all(
                consumer_file(judge_committed_out_dir, pid, arm).is_file()
                for pid in pids for arm in ("cold", "loaded")
            ):
                complete_ids.add(t["id"])
        skipped = sorted(t["id"] for t in tasks if t["id"] not in complete_ids)
        tasks = [t for t in tasks if t["id"] in complete_ids]
        if not tasks:
            fail("--judge-committed: no task has every repeat's consumer "
                 "arms committed yet in " + str(judge_committed_out_dir))
        print(f"judge-committed: {len(tasks)} task(s) fully committed, "
              f"judging now; {len(skipped)} left for later "
              f"({', '.join(skipped) if skipped else 'none'})")

    # Staged-skill frontmatter preflight, before any API call: a skill that
    # declares effort/model/context/agent would reconfigure the loaded
    # arm's runtime and unblind the comparison.
    fm_errs = tasks_mod.skill_frontmatter_preflight(tasks)
    if fm_errs:
        fail(
            "staged-skill frontmatter preflight failed (no API calls "
            "made):\n  " + "\n  ".join(fm_errs)
        )
    if args.seed is not None:
        seed = args.seed
    else:
        # Fresh run-time entropy: deriving the seed from author-controlled
        # bytes would let a task author grind free-form fields until the
        # ordering favors one arm. The seed is persisted to run-state.json,
        # order-key.json, and run-meta.json, and reused verbatim on resume.
        seed = secrets.randbits(64)

    # Per-model effort preflight, before any API call. An unsupported
    # model-effort combination is unavailable by design: recorded, then
    # refused, never a silent fallback to some other effort.
    reason = unavailable_by_design(args.model, args.effort)
    if reason:
        record_path = record_unavailable_cell(args.model, args.effort, reason)
        fail(f"model-effort combination unavailable by design (recorded at "
             f"{record_path}): {reason}")

    # --effort is fail-closed: the installed CLI must advertise the flag
    # AND the requested level before any API call, because the CLI itself
    # ignores unknown effort values and silently runs at the default
    # effort, which would mislabel this cell.
    effort_evidence = None
    if args.effort:
        try:
            effort_evidence = consumer_mod.verify_effort_support(args.effort)
        except consumer_mod.ConsumerError as exc:
            fail(str(exc))

    # Per-model enumeration of supported effort levels and detected
    # defaults, recorded verbatim in run-meta.
    try:
        effort_support = consumer_mod.enumerate_effort_support(args.model)
    except consumer_mod.ConsumerError as exc:
        fail(str(exc))

    # Judge panel preflight: both judges run pinned at --effort medium, so
    # the installed CLI must advertise that level before any spend.
    try:
        judge_effort_evidence = consumer_mod.verify_effort_support(
            judge_mod.JUDGE_EFFORT
        )
    except consumer_mod.ConsumerError as exc:
        fail(f"judge panel effort preflight failed: {exc}")

    # Adjudicator preflight: the pinned adjudicator effort must also be
    # advertised by the installed CLI before any spend.
    try:
        adjudicator_effort_evidence = consumer_mod.verify_effort_support(
            judge_mod.ADJUDICATOR_EFFORT
        )
    except consumer_mod.ConsumerError as exc:
        fail(f"adjudicator effort preflight failed: {exc}")

    n_consumers = len(tasks) * 2 * args.repeats
    n_judges = (len(tasks) * args.repeats * args.judge_repeats
                * len(judge_mod.JUDGE_PANEL))

    if args.dry_run:
        return dry_run(args, tasks_path, tasks, seed, preregistered,
                       n_consumers, n_judges, effort_evidence,
                       effort_support)

    # Output dir + resume state. The run id carries the cell coordinates
    # (model x effort) so matrix cells land in separate directories.
    suite_label = args.suite or tasks_path.stem
    out_dir = Path(args.out) if args.out else RESULTS_DIR / (
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + f"-{suite_label}-{cell_slug(args.model, args.effort)}"
    )
    state = {
        "task_file": str(tasks_path.relative_to(REPO_ROOT))
        if tasks_path.is_relative_to(REPO_ROOT) else str(tasks_path),
        "task_file_sha256": tasks_mod.file_sha256(tasks_path),
        "seed": seed,
        "model": args.model,
        "effort": args.effort,
        "judge_panel": list(judge_mod.JUDGE_PANEL),
        "judge_effort": judge_mod.JUDGE_EFFORT,
        "adjudicator_model": judge_mod.ADJUDICATOR_MODEL,
        "adjudicator_effort": judge_mod.ADJUDICATOR_EFFORT,
        "repeats": args.repeats,
        "judge_repeats": args.judge_repeats,
        "skill_filter": args.skill,
        "task_id_filter": args.task_ids,
        "preregistered": preregistered,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    # One active process per run directory: two concurrent runs would
    # interleave writes to the same artifact files. The flock is released
    # automatically when the process exits, so a crashed run never blocks
    # its own resume.
    import fcntl  # POSIX-only, like the bash-based fixture builds
    lock_handle = (out_dir / ".lock").open("a")
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fail(f"{out_dir} is in use by another active run")

    state_path = out_dir / "run-state.json"
    resuming = False
    if state_path.is_file():
        prev = json.loads(state_path.read_text(encoding="utf-8"))
        prev_started = prev.pop("started_at", None)
        # Legacy/cross-machine runs may have persisted task_file as an
        # absolute path rooted in a different machine's home directory.
        # relative_to(REPO_ROOT) only strips THIS machine's own root, so a
        # foreign absolute path is never a subpath of it. Normalize by
        # matching the trailing path segments instead (anchored to the repo
        # layout, not any machine's home dir); task_file_sha256 remains the
        # authoritative content check regardless.
        prev_task_file = prev.get("task_file")
        if (isinstance(prev_task_file, str) and prev_task_file
                and prev_task_file.replace("\\", "/").endswith(state["task_file"])):
            prev["task_file"] = state["task_file"]
        if args.seed is None and isinstance(prev.get("seed"), int):
            seed = prev["seed"]  # adopt the interrupted run's entropy
            state["seed"] = seed
        if prev != state:
            fail(
                f"{out_dir} holds an interrupted run with a different "
                f"configuration; use a fresh --out or match the original flags"
            )
        resuming = True
        print(f"resuming interrupted run in {out_dir} (started {prev_started})")
    for sub in ("consumer", "judge-inputs", "judge-outputs"):
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    if not resuming:
        write_atomic(
            state_path,
            json.dumps({**state, "started_at": utc_now()}, indent=2, sort_keys=True)
            + "\n",
        )

    # Order key: generated once per run, reused verbatim on resume.
    order_path = out_dir / "order-key.json"
    if order_path.is_file():
        order_key = json.loads(order_path.read_text(encoding="utf-8"))
    else:
        order_key = make_order_key(tasks, args.repeats, seed)
        write_atomic(
            order_path, json.dumps(order_key, indent=2, sort_keys=True) + "\n"
        )

    started = time.monotonic()
    persona = consumer_mod.load_persona()
    try:
        cli_version = consumer_mod.claude_version()
    except consumer_mod.ConsumerError as exc:
        fail(str(exc))

    with tempfile.TemporaryDirectory(prefix="skills-eval-") as tmp:
        tmp = Path(tmp)
        # Build each fixture once, verify against its manifest, then copy
        # per consumer run.
        built = {}
        template_snaps = {}
        for fx in sorted({t["fixture"] for t in tasks}):
            dest = tmp / "fixtures" / fx
            fixtures_mod.build_fixture(fx, dest)
            snap = fixtures_mod.snapshot(dest)
            manifest = fixtures_mod.load_manifest(fx)
            if snap["tree_sha256"] != manifest["tree_sha256"] or \
                    snap["git_heads"] != manifest.get("git_heads"):
                fail(f"fixture {fx}: build does not match manifest.json; "
                     f"run --validate for details")
            built[fx] = dest
            template_snaps[fx] = snap
            print(f"fixture {fx}: built and verified against manifest")

        # Consumer jobs (skipping any completed on a previous attempt; a
        # persisted result only counts when it parses and validates).
        jobs = []
        for task, r, pid in ab_pairs(tasks, args.repeats):
            for arm in ("cold", "loaded"):
                if load_consumer_result(consumer_file(out_dir, pid, arm)) is not None:
                    continue
                jobs.append((task, pid, r, arm, built[task["fixture"]],
                             template_snaps[task["fixture"]],
                             tmp / "work", persona, args.model, args.effort))
        (tmp / "work").mkdir(exist_ok=True)
        print(f"consumers: {n_consumers} total, {n_consumers - len(jobs)} "
              f"already complete, {len(jobs)} to run "
              f"(concurrency {args.concurrency})")
        failures = {}
        with concurrent.futures.ThreadPoolExecutor(args.concurrency) as pool:
            for pid, arm, result in pool.map(run_one_consumer, jobs):
                if isinstance(result, Exception):
                    task_id = pid.rsplit("-r", 1)[0] if args.repeats > 1 else pid
                    entry = failures.setdefault(task_id, {"arms": set(), "msgs": []})
                    entry["arms"].add(arm)
                    entry["msgs"].append(f"{pid}-{arm}: {result}")
                    print(f"consumer {pid}-{arm}: FAILED ({result})")
                    continue
                write_atomic(
                    consumer_file(out_dir, pid, arm),
                    json.dumps(result, indent=2, sort_keys=True) + "\n",
                )
                print(f"consumer {pid}-{arm}: ok "
                      f"({result.get('duration_ms', '?')} ms)")

        # A task with any failed consumer run is excluded entirely and the
        # exclusion is reported (with the failing arms, so a skill cannot
        # quietly shed its own worst tasks); the denominator shrinks
        # accordingly.
        excluded = [
            {"task": task_id, "failed_arms": sorted(f["arms"]),
             "reason": "; ".join(f["msgs"])}
            for task_id, f in sorted(failures.items())
        ]
        included_tasks = [t for t in tasks if t["id"] not in failures]

        # Stage B comprehension check + scrub + judge input assembly.
        comprehension = {}
        scrub_subs = []
        judge_inputs = {}
        slot_texts = {}
        must_hit_texts = {}
        judge_frame = judge_mod.load_judge_prompt()
        mutation_warnings = []
        leak_hits = []
        models_effective = set()
        # Full frozen skill roster: banned in every task's scrub pass so a
        # cross-skill name echo cannot survive (see scrub.banned_patterns).
        skill_roster = tasks_mod.all_skill_names()
        for task, r, pid in ab_pairs(included_tasks, args.repeats):
            answers = {}
            for arm in ("cold", "loaded"):
                data = json.loads(
                    consumer_file(out_dir, pid, arm).read_text(encoding="utf-8")
                )
                if data.get("workspace_mutated"):
                    mutation_warnings.append(f"{pid}-{arm}")
                models_effective.update(data.get("models_effective") or [])
                answers[arm] = data["answers"]
                if arm == "loaded":
                    comprehension.setdefault(task["id"], []).append(
                        consumer_mod.comprehension_check(
                            data["report"], tasks_mod.skill_name_for(task)
                        )
                    )
            patterns = scrub_mod.banned_patterns(
                task["skill"], tasks_mod.skill_name_for(task), skill_roster
            )
            scrubbed = {}
            for arm in ("cold", "loaded"):
                scrubbed[arm], subs = scrub_mod.scrub_text(answers[arm], patterns)
                for s in subs:
                    s.update({"pair": pid, "arm_file": f"{pid}-{arm}"})
                scrub_subs.extend(subs)
            order = order_key["order"][pid]
            report_1 = scrubbed[order["report_1"]]
            report_2 = scrubbed[order["report_2"]]
            # Retained for adjudication: the identical blinded slots the
            # primary judges see, plus the frozen must-hit texts.
            slot_texts[pid] = {"report_1": report_1, "report_2": report_2}
            must_hit_texts[pid] = {m["id"]: m["text"] for m in task["must_hits"]}
            judge_input = judge_mod.assemble_input(
                judge_frame, task["prompt"], task["must_hits"],
                task.get("judge_notes"), report_1, report_2,
            )
            hits = scrub_mod.verify_no_leak(judge_input, patterns)
            for h in hits:
                leak_hits.append({**h, "file": f"judge-inputs/{pid}.json"})
            judge_inputs[pid] = judge_input
            write_atomic(
                out_dir / "judge-inputs" / f"{pid}.json",
                json.dumps(
                    {"pair": pid, "task": task["id"], "prompt": judge_input,
                     "schema": "eval/schemas/judge.schema.json"},
                    indent=2, sort_keys=True,
                ) + "\n",
            )

        write_atomic(
            out_dir / "scrub-manifest.json",
            json.dumps({"substitutions": scrub_subs}, indent=2, sort_keys=True) + "\n",
        )
        write_atomic(
            out_dir / "comprehension.json",
            json.dumps(comprehension, indent=2, sort_keys=True) + "\n",
        )

        if leak_hits:
            for h in leak_hits:
                print(
                    f"LEAK {h['file']} offset {h['offset']} pattern "
                    f"{h['pattern']}: ...{h['snippet']}...",
                    file=sys.stderr,
                )
            fail(
                f"blinding verifier found {len(leak_hits)} banned-token hits "
                f"in assembled judge inputs; run aborted before judging"
            )
        print(f"blinding: verifier clean over {len(judge_inputs)} judge inputs; "
              f"{len(scrub_subs)} scrub substitutions")

        # Judges: the pinned two-judge panel, one job per (pair, judge)
        # with all that judge's votes, errors returned as values and each
        # judge's output written the moment it completes, so judging stays
        # resumable per judge and one bad judge run never discards the
        # other judge's spend on the same pair.
        judge_pairs = list(ab_pairs(included_tasks, args.repeats))
        judges_effective = {jm: set() for jm in judge_mod.JUDGE_PANEL}

        def run_one_judge(job):
            """Returns (pid, task_id, judge_model, output_dict_or_error)."""
            task, r, pid, jm = job
            mh_ids = [m["id"] for m in task["must_hits"]]
            judgments, metas = [], []
            try:
                for _ in range(args.judge_repeats):
                    judgment, meta = judge_mod.run_judge(
                        judge_inputs[pid], jm, mh_ids, tmp
                    )
                    judgments.append(judgment)
                    metas.append(meta)
            except (consumer_mod.ConsumerError, judge_mod.JudgeError,
                    subprocess.SubprocessError, OSError) as exc:
                return pid, task["id"], jm, exc
            return pid, task["id"], jm, {
                "pair": pid, "task": task["id"], "repeat": r,
                "judge_model": jm,
                "judge_effort": judge_mod.JUDGE_EFFORT,
                "judgments": judgments, "cli_meta": metas,
            }

        pending = []
        for task, r, pid in judge_pairs:
            for jm in judge_mod.JUDGE_PANEL:
                target = judge_file(out_dir, pid, jm)
                if target.is_file():
                    try:
                        existing = json.loads(target.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        existing = {}
                    if (existing.get("judge_model") == jm
                            and len(existing.get("judgments", []))
                            >= args.judge_repeats):
                        for meta in existing.get("cli_meta") or []:
                            judges_effective[jm].update(
                                meta.get("models_effective") or []
                            )
                        continue
                pending.append((task, r, pid, jm))
        n_judge_jobs = len(judge_pairs) * len(judge_mod.JUDGE_PANEL)
        print(f"judges: panel {' + '.join(judge_mod.JUDGE_PANEL)} at "
              f"--effort {judge_mod.JUDGE_EFFORT}: {n_judge_jobs} "
              f"pair-judge runs ({args.judge_repeats} vote(s) each), "
              f"{n_judge_jobs - len(pending)} already complete, "
              f"{len(pending)} to run")
        judge_failures = {}
        with concurrent.futures.ThreadPoolExecutor(args.concurrency) as pool:
            for pid, task_id, jm, output in pool.map(run_one_judge, pending):
                if isinstance(output, Exception):
                    judge_failures.setdefault(task_id, []).append(
                        f"{pid} [{jm}]: {output}"
                    )
                    print(f"judge {pid} [{jm}]: FAILED ({output})")
                    continue
                for meta in output["cli_meta"]:
                    judges_effective[jm].update(
                        meta.get("models_effective") or []
                    )
                write_atomic(
                    judge_file(out_dir, pid, jm),
                    json.dumps(output, indent=2, sort_keys=True) + "\n",
                )
                print(f"judge {pid} [{jm}]: ok "
                      f"({len(output['judgments'])} vote(s))")
        # A task whose judging failed is excluded like a consumer failure;
        # resuming the run re-attempts only the missing judge outputs.
        excluded.extend(
            {"task": task_id, "reason": "judging failed: " + "; ".join(msgs)}
            for task_id, msgs in sorted(judge_failures.items())
        )

        # Adjudication: for every comparison both judges completed, each
        # report-slot must-hit mark the two primaries disagree on goes to
        # the pinned adjudicator exactly once (one retry inside
        # run_claude). The adjudicator sees a minimal input: the disputed
        # expectation, the two blinded report slots, and the judging
        # frame. The final mark is the two-of-three majority; disputed
        # marks never leave any denominator. Resumable: marks already
        # adjudicated in a persisted record are reused verbatim.
        adjudicator_frame = judge_mod.load_adjudicator_prompt()
        adjudicator_effective = set()
        adjudication_failures = {}
        adj_jobs = []
        pair_disputes = {}
        for task, r, pid in judge_pairs:
            if task["id"] in judge_failures:
                continue
            per_judge = {}
            complete = True
            for jm in judge_mod.JUDGE_PANEL:
                target = judge_file(out_dir, pid, jm)
                if not target.is_file():
                    complete = False
                    break
                per_judge[jm] = json.loads(
                    target.read_text(encoding="utf-8"))["judgments"]
            if not complete:
                continue
            mh_ids = [m["id"] for m in task["must_hits"]]
            try:
                disputes = scoring_mod.slot_disputes(per_judge, mh_ids)
            except scoring_mod.ScoringError as exc:
                adjudication_failures.setdefault(task["id"], []).append(
                    f"{pid}: {exc}")
                continue
            if not disputes:
                continue
            existing = load_adjudication(adjudication_file(out_dir, pid))
            have = {}
            for d in (existing or {}).get("disputes", []):
                if isinstance(d.get("adjudicator_mark"), dict):
                    have[(d["must_hit"], d["slot"])] = d
            pair_disputes[pid] = (task, r, per_judge, disputes, have)
            for mh_id, slot in disputes:
                if (mh_id, slot) not in have:
                    adj_jobs.append((task, pid, mh_id, slot))

        # Run metadata (everything scoring and replay need). A function, not
        # a one-shot dict: the deferred-adjudication branch below needs to
        # persist a run-meta.json checkpoint BEFORE it returns (using
        # excluded_tasks as they stand pre-adjudication), and the normal
        # end-of-run write below needs the same construction again once any
        # adjudication-failure exclusions have been folded into `excluded`.
        # Every free variable this reads is already bound by this point in
        # the function (before any adjudication has run); adjudicator
        # models_effective is legitimately empty in the deferred snapshot
        # since no adjudicator call has happened yet.
        def build_run_meta():
            return {
                "run_id": out_dir.name,
                "created_at": utc_now(),
                "task_file": str(tasks_path.relative_to(REPO_ROOT))
                if tasks_path.is_relative_to(REPO_ROOT) else str(tasks_path),
                "task_file_sha256": tasks_mod.file_sha256(tasks_path),
                "model": args.model,
                "effort": effort_label(args.model, args.effort),
                "effort_mechanism": {
                    "cli_flag": f"--effort {args.effort}" if args.effort else None,
                    **(effort_evidence or {}),
                    "consumer_stderr_checked": bool(args.effort),
                    "note": (
                        "every consumer invocation carried --effort and failed "
                        "closed on any CLI effort warning; judges ran at their "
                        "own pinned effort (see judge_panel)"
                        if args.effort else
                        ("effort-invariant model: no effort knob exists, no "
                         "--effort flag was passed, and the cell is recorded as "
                         "effort none"
                         if consumer_mod.effort_invariant_model(args.model) else
                         "no --effort flag passed; consumers ran at the CLI default "
                         "effort (see effort_sources for ambient overrides)")
                    ),
                },
                # Per-model enumeration of supported effort levels and detected
                # defaults (preflight evidence; unsupported combinations are
                # refused before this point and recorded under
                # results/unavailable/).
                "effort_support": effort_support,
                "effort_sources": consumer_mod.ambient_effort_sources(),
                # Requested vs effective: "model" and "effort" above are the
                # requested coordinates; every persisted consumer result carries
                # model_effective/models_effective/effort_effective, and this is
                # the union of answering models observed across included runs.
                "consumer_models_effective": sorted(models_effective),
                "max_output_tokens": {
                    "value": consumer_mod.CONSUMER_MAX_OUTPUT_TOKENS,
                    "mechanism": (
                        "CLAUDE_CODE_MAX_OUTPUT_TOKENS environment variable on "
                        "every consumer invocation, identical in both arms and at "
                        "every effort level"
                    ),
                },
                "validity_rules": {
                    "truncated_by_limit": (
                        "a consumer run whose output hit the pinned ceiling is "
                        "invalid: one retry, then the task is excluded-as-invalid"
                    ),
                    "cross_model_fallback": (
                        "a consumer run answered by a model other than the "
                        "requested one is invalid: one retry, then the task is "
                        "excluded-as-invalid"
                    ),
                    "cli_effort_warning": (
                        "a consumer run whose stderr carried a CLI effort warning "
                        "is invalid: the requested effort was not applied"
                    ),
                },
                "cold_arm_isolation": {
                    "workspace": (
                        "cold workspaces are staged into a fresh temp directory "
                        "and asserted to contain no .claude directory before "
                        "every consumer run"
                    ),
                    "skill_tool": (
                        "consumers run with --allowedTools "
                        f"{consumer_mod.ALLOWED_TOOLS}, which exposes no Skill "
                        "tool, so user-level and project-level skills cannot be "
                        "invoked in either arm"
                    ),
                    "ambient_user_skills": consumer_mod.ambient_user_skills(),
                },
                "judge_panel": {
                    "models": list(judge_mod.JUDGE_PANEL),
                    "effort": judge_mod.JUDGE_EFFORT,
                    "effort_mechanism": {
                        "cli_flag": f"--effort {judge_mod.JUDGE_EFFORT}",
                        **judge_effort_evidence,
                        "note": (
                            "pinned identically for both judges on every judge "
                            "invocation, never varying across cells; any CLI "
                            "effort warning on a judge's stderr fails that judge "
                            "run closed"
                        ),
                    },
                    "blinding": (
                        "identical blinding stack for both judges: the same "
                        "scrubbed and verifier-checked judge inputs, the same "
                        "seeded order key, and the same leak verifier gate"
                    ),
                    "combination_rule": scoring_mod.ADJUDICATED_UNIT,
                    # Requested vs effective per judge. A judge run answered by a
                    # different model (cross-model fallback) or carrying a CLI
                    # effort warning fails closed before persisting, so effective
                    # always equals requested in persisted judge outputs; the
                    # models_effective union below is the observed evidence.
                    "judges": {
                        jm: {
                            "model_requested": jm,
                            "models_effective": sorted(judges_effective[jm]),
                            "effort_requested": judge_mod.JUDGE_EFFORT,
                            "effort_effective": judge_mod.JUDGE_EFFORT,
                        }
                        for jm in judge_mod.JUDGE_PANEL
                    },
                },
                "judge_model": "two-judge panel (see judge_panel)",
                # Pinned third adjudicator: exact model ID and effort recorded
                # here before any verdict exists, immutable after data. Its
                # presence switches scoring to the adjudicated combination rule.
                "adjudicator": {
                    "model": judge_mod.ADJUDICATOR_MODEL,
                    "effort": judge_mod.ADJUDICATOR_EFFORT,
                    "effort_mechanism": {
                        "cli_flag": f"--effort {judge_mod.ADJUDICATOR_EFFORT}",
                        **adjudicator_effort_evidence,
                        "note": (
                            "pinned on every adjudicator invocation; any CLI "
                            "effort warning or cross-model fallback fails that "
                            "invocation closed"
                        ),
                    },
                    "models_effective": sorted(adjudicator_effective),
                    "schema": "eval/schemas/adjudicator.schema.json",
                    "input": (
                        "minimal by construction: the disputed expectation text, "
                        "the two blinded report slots exactly as the primary "
                        "judges saw them, and the judging frame; invoked once per "
                        "disputed report-slot mark"
                    ),
                    "rule": scoring_mod.ADJUDICATED_UNIT,
                    "failure_rule": (
                        "adjudicator failure after one retry excludes the task "
                        "like a judge failure; the more-than-one-third floor "
                        "triggers only on judge-failure exclusions, never on "
                        "adjudicated disagreements"
                    ),
                    "floor_rule": scoring_mod.FAILURE_FLOOR_RULE,
                },
                "claude_cli_version": cli_version,
                "seed": seed,
                "concurrency": args.concurrency,
                "repeats": args.repeats,
                "judge_repeats": args.judge_repeats,
                "preregistered": preregistered,
                "freeze": {
                    "frozen_at": (frozen or {}).get("frozen_at"),
                    "task_file_sha256": (frozen or {}).get("task_file_sha256"),
                },
                "auth_mode": "api-key" if os.environ.get("ANTHROPIC_API_KEY")
                else "subscription-login",
                "skill_hashes_at_run": freeze_mod.current_skill_hashes(tasks),
                "instrument_hashes_at_run": freeze_mod.instrument_hashes(),
                "tasks": {
                    t["id"]: {
                        "skill": t["skill"],
                        "fixture": t["fixture"],
                        "must_hit_ids": [m["id"] for m in t["must_hits"]],
                    }
                    for t in tasks
                },
                "excluded_tasks": excluded,
                "workspace_mutation_warnings": sorted(mutation_warnings),
                # On a resumed run this covers only the final attempt, not the
                # interrupted ones; "resumed" flags that under-report.
                "resumed": resuming,
                "wall_clock_seconds": round(time.monotonic() - started, 1),
            }

        if args.defer_adjudication and adj_jobs:
            # Judging is decoupled by pre-registration and runs on committed
            # inputs at any time. Stop before the adjudicator so that an
            # adjudicator-pool outage (a quota pause, not task-level flake)
            # cannot be written into the record as judge-failure exclusions.
            # Both panel judges' marks are already persisted; rerunning the
            # same command without this flag adjudicates and scores.
            # CRITICAL: still write run-meta.json here, with excluded_tasks
            # as they stand right now, BEFORE returning. Without this, a
            # stale run-meta.json from an earlier failed attempt at this
            # same --out (one whose excluded_tasks reflected THAT attempt's
            # mass consumer failures) would survive untouched, and a later
            # `--report` recompute would silently score against that stale,
            # over-excluded task list instead of this attempt's real,
            # complete data. (Found live 2026-07-10: lattice-haiku and
            # lattice-sonnet-low both showed 0/0 on --report/--validate
            # despite full underlying data, traced to exactly this gap.)
            write_atomic(
                out_dir / "run-meta.json",
                json.dumps(build_run_meta(), indent=2, sort_keys=True) + "\n",
            )
            print(f"defer-adjudication: {len(adj_jobs)} disputed report-slot "
                  f"mark(s) across {len(pair_disputes)} comparison(s) left "
                  f"unadjudicated; panel marks committed, run NOT scored. "
                  f"Rerun without --defer-adjudication to adjudicate and score.")
            return

        def run_one_adjudication(job):
            """Returns (pid, task_id, mh_id, slot, (mark, meta)_or_error)."""
            task, pid, mh_id, slot = job
            adj_input = judge_mod.assemble_adjudicator_input(
                adjudicator_frame, must_hit_texts[pid][mh_id], slot,
                slot_texts[pid]["report_1"], slot_texts[pid]["report_2"],
            )
            try:
                mark, meta = judge_mod.run_adjudicator(adj_input, tmp)
            except (consumer_mod.ConsumerError, judge_mod.JudgeError,
                    subprocess.SubprocessError, OSError) as exc:
                return pid, task["id"], mh_id, slot, exc
            return pid, task["id"], mh_id, slot, (mark, meta)

        n_disputed = sum(len(p[3]) for p in pair_disputes.values())
        print(f"adjudicator: {judge_mod.ADJUDICATOR_MODEL} at --effort "
              f"{judge_mod.ADJUDICATOR_EFFORT}: {n_disputed} disputed "
              f"report-slot mark(s) across {len(pair_disputes)} "
              f"comparison(s), {n_disputed - len(adj_jobs)} already "
              f"adjudicated, {len(adj_jobs)} to run")
        adj_results = {}
        if adj_jobs:
            with concurrent.futures.ThreadPoolExecutor(args.concurrency) as pool:
                for pid, task_id, mh_id, slot, outcome in pool.map(
                        run_one_adjudication, adj_jobs):
                    adj_results[(pid, mh_id, slot)] = outcome
                    if isinstance(outcome, Exception):
                        adjudication_failures.setdefault(task_id, []).append(
                            f"{pid} {mh_id}/{slot}: {outcome}")
                        print(f"adjudicator {pid} {mh_id}/{slot}: FAILED "
                              f"({outcome})")
                    else:
                        adjudicator_effective.update(
                            outcome[1].get("models_effective") or [])
                        print(f"adjudicator {pid} {mh_id}/{slot}: ok")
        for pid in sorted(pair_disputes):
            task, r, per_judge, disputes, have = pair_disputes[pid]
            entries = []
            for mh_id, slot in disputes:
                if (mh_id, slot) in have:
                    entries.append(have[(mh_id, slot)])
                    continue
                outcome = adj_results.get((pid, mh_id, slot))
                entry = {
                    "must_hit": mh_id,
                    "slot": slot,
                    "judge_marks": {
                        jm: judge_slot_marks(per_judge[jm], mh_id, slot)
                        for jm in judge_mod.JUDGE_PANEL
                    },
                    "rule": scoring_mod.ADJUDICATION_RULE,
                }
                if isinstance(outcome, tuple):
                    mark, meta = outcome
                    entry.update({
                        "adjudicator_mark": mark,
                        "final_mark": mark["hit"],
                        "cli_meta": meta,
                    })
                else:
                    entry.update({
                        "adjudicator_mark": None,
                        "final_mark": None,
                        "adjudicator_error": str(outcome),
                    })
                entries.append(entry)
            write_atomic(
                adjudication_file(out_dir, pid),
                json.dumps({
                    "pair": pid,
                    "task": task["id"],
                    "repeat": r,
                    "adjudicator_model": judge_mod.ADJUDICATOR_MODEL,
                    "adjudicator_effort": judge_mod.ADJUDICATOR_EFFORT,
                    "schema": "eval/schemas/adjudicator.schema.json",
                    "disputes": entries,
                }, indent=2, sort_keys=True) + "\n",
            )
        # Adjudicator failure after the retry is the existing judge-failure
        # cell exclusion: the whole paired comparison's task leaves the
        # denominator and the exclusion is reported. The >1/3 floor in
        # scoring triggers only on such judge-failure exclusions, never on
        # adjudicated disagreements.
        excluded.extend(
            {"task": task_id,
             "reason": "adjudication failed: " + "; ".join(msgs)}
            for task_id, msgs in sorted(adjudication_failures.items())
        )

    # Full, final run-meta.json: same construction as the deferred-branch
    # checkpoint above, called again now that `excluded` may additionally
    # carry adjudication-failure exclusions from the loop just above.
    write_atomic(
        out_dir / "run-meta.json",
        json.dumps(build_run_meta(), indent=2, sort_keys=True) + "\n",
    )

    # Score and emit.
    scores_text, report_text = report_mod.recompute(out_dir)
    write_atomic(out_dir / "scores.json", scores_text)
    write_atomic(out_dir / "REPORT.md", report_text)
    scores = json.loads(scores_text)
    agg = scores["aggregate"]
    print(
        f"\ndone: cold {agg['cold_hits']}/{agg['n_expectations']} | "
        f"loaded {agg['loaded_hits']}/{agg['n_expectations']} | "
        f"skills passing "
        f"{sum(1 for s in scores['skills'].values() if s['pass'])}/"
        f"{len(scores['skills'])}"
    )
    print(f"results: {out_dir}")


def dry_run(args, tasks_path, tasks, seed, preregistered, n_consumers,
            n_judges, effort_evidence=None, effort_support=None):
    print(f"DRY RUN: no API calls will be made\n")
    print(f"task file: {tasks_path} ({len(tasks)} tasks)")
    print(f"preregistered: {preregistered}")
    print(f"seed: {seed} (order key is generated from this at run time and "
          f"persisted to order-key.json)")
    print(f"consumer model: {args.model}; judge panel: "
          f"{' + '.join(judge_mod.JUDGE_PANEL)} (both pinned at --effort "
          f"{judge_mod.JUDGE_EFFORT})")
    print(f"adjudicator: {judge_mod.ADJUDICATOR_MODEL} (pinned at --effort "
          f"{judge_mod.ADJUDICATOR_EFFORT}), invoked once per disputed "
          f"report-slot mark; dispute count is unknowable before judging")
    print(f"consumer effort: {effort_label(args.model, args.effort)}"
          f"{'' if args.effort else ' (no --effort flag)'}")
    if effort_support:
        print(f"model effort support: "
              f"{', '.join(effort_support['supported_levels']) or 'none'} "
              f"(effort-invariant: {effort_support['effort_invariant']})")
    print(f"consumer max output tokens (pinned, both arms): "
          f"{consumer_mod.CONSUMER_MAX_OUTPUT_TOKENS}")
    if effort_evidence:
        print(f"effort mechanism verified against the installed CLI: "
              f"{effort_evidence['cli_help_evidence']}")
    try:
        print(f"claude CLI: {consumer_mod.claude_version()}")
    except consumer_mod.ConsumerError as exc:
        fail(str(exc))
    print(f"auth: {'ANTHROPIC_API_KEY' if os.environ.get('ANTHROPIC_API_KEY') else 'subscription login'}")
    with tempfile.TemporaryDirectory(prefix="skills-eval-dry-") as tmp:
        tmp = Path(tmp)
        for fx in sorted({t["fixture"] for t in tasks}):
            dest = tmp / fx
            fixtures_mod.build_fixture(fx, dest)
            snap = fixtures_mod.snapshot(dest)
            manifest = fixtures_mod.load_manifest(fx)
            ok = (snap["tree_sha256"] == manifest["tree_sha256"]
                  and snap["git_heads"] == manifest.get("git_heads"))
            print(f"\nfixture {fx}: built at {dest}: "
                  f"{'matches manifest' if ok else 'MISMATCH vs manifest'}")
            if not ok:
                fail(f"fixture {fx} is not deterministic or manifest is stale")
        print("\nplan:")
        for task, r, pid in ab_pairs(tasks, args.repeats):
            for arm in ("cold", "loaded"):
                extra = ""
                if arm == "loaded":
                    name = tasks_mod.skill_name_for(task)
                    ws = tmp / "sample" / f"{pid}-loaded"
                    if not ws.exists():
                        stage_arm_workspace(
                            tmp / task["fixture"], tmp / "sample", pid, arm, task
                        )
                    extra = f" + .claude/skills/{name}/"
                print(f"  {pid:<28} {arm:<7} fixture={task['fixture']}{extra}")
        print(f"\nstaged sample workspaces verified (skill copy works); "
              f"temp dir removed on exit")
    tok = n_consumers * EST_CONSUMER_TOKENS + n_judges * EST_JUDGE_TOKENS
    lo = tok * EST_USD_PER_MTOK[0] / 1e6
    hi = tok * EST_USD_PER_MTOK[1] / 1e6
    print(f"\nestimate: {n_consumers} consumer runs + {n_judges} judge runs")
    print(f"estimate: ~{tok / 1e6:.1f}M tokens including cache reads, "
          f"roughly ${lo:.2f} to ${hi:.2f} (measured effective Sonnet-tier "
          f"rate; higher-effort or larger-model cells run above this band)")
    waves = -(-n_consumers // args.concurrency)
    print(f"estimate: about {waves * 2} to {waves * 4} minutes of consumer "
          f"wall clock at concurrency {args.concurrency}, plus judging")


# ---------------------------------------------------------------- main


def main():
    p = argparse.ArgumentParser(
        prog="eval/run.py",
        description="Blinded A/B eval harness for the skills library "
                    "(stdlib only; needs the claude CLI for live runs).",
    )
    p.add_argument("--tasks", help="path to a task JSONL file")
    p.add_argument("--suite", help="named suite under eval/tasks/ (golden)")
    p.add_argument("--ab", action="store_true", help="run the blinded A/B")
    p.add_argument("--freeze", action="store_true",
                   help="write the pre-registration freeze for --tasks/--suite")
    p.add_argument("--validate", action="store_true",
                   help="schema/lint/fixture/freeze/replay validation (no API)")
    p.add_argument("--replay", metavar="RUN_DIR",
                   help="recompute scores from a run's raw judge outputs and "
                        "byte-diff against its committed scores")
    p.add_argument("--report", metavar="RUN_DIR",
                   help="re-emit REPORT.md and scores.json for a run")
    p.add_argument("--matrix-report", metavar="RUN_DIR", nargs="+",
                   help="aggregate multiple completed cell runs (one per "
                        "model x effort cell) into matrix.json + MATRIX.md, "
                        "including matched-effort, defaults-as-shipped, and "
                        "H4 shrinkage views")
    p.add_argument("--concordance-sample", metavar="RUN_DIR", nargs="+",
                   help="select the 50-comparison Codex concordance sample "
                        "deterministically by hash-parity over the given "
                        "runs' committed judge inputs and write "
                        "manifest.json (no API calls, no Codex "
                        "integration)")
    p.add_argument("--dry-run", action="store_true",
                   help="with --ab: print plan, stage workspaces, estimate "
                        "cost; no API calls")
    p.add_argument("--seed", type=int, default=None,
                   help="order-randomization seed (default: fresh run-time "
                        "entropy, persisted with the run)")
    p.add_argument("--concurrency", type=int, default=4,
                   help="parallel consumer/judge subprocesses (default 4)")
    p.add_argument("--repeats", type=int, default=1,
                   help="consumer runs per arm per task (default 1); each "
                        "repeat is isolated (own workspace, own CLI "
                        "invocation, no shared session state), carries its "
                        "repeat index in every artifact, and endpoint "
                        "cells aggregate to mean rates across repeats")
    p.add_argument("--judge-repeats", type=int, default=1,
                   help="judges per task; majority vote when >1 (default 1)")
    p.add_argument("--model", default="sonnet", help="consumer model")
    p.add_argument("--effort", default=None, metavar="LEVEL",
                   help="consumer effort level passed to the claude CLI as "
                        "--effort (low, medium, high, xhigh, max on "
                        "2.1.206); verified against the installed CLI "
                        "before any API call and recorded in run-meta; "
                        "absent = model default")
    p.add_argument("--skill", default=None, help="filter to one skill's tasks")
    p.add_argument("--defer-adjudication", action="store_true",
                   help="run consumers and both panel judges, persist their "
                        "marks, then stop before adjudicating disputed marks "
                        "and before scoring; use when the pinned "
                        "adjudicator's pool is exhausted. Rerun the same "
                        "command without this flag (same --out) to adjudicate "
                        "the committed disputes and score.")
    p.add_argument("--judge-committed", action="store_true",
                   help="never call a consumer model; judge only the tasks "
                        "whose consumer arms are ALREADY complete for every "
                        "repeat in the --out run directory (a still-paused "
                        "or still-running attempt), leaving every other "
                        "task for that attempt to finish later. Requires "
                        "--out. Judging is decoupled by pre-registration "
                        "and may run on committed inputs at any time.")
    p.add_argument("--task-ids", default=None, metavar="ID[,ID...]",
                   help="filter to specific task ids (comma-separated), "
                        "applied after the freeze is verified against the "
                        "full task file, exactly like --skill; unknown ids "
                        "fail before any API call")
    p.add_argument("--out", default=None,
                   help="output directory (default results/<UTC-timestamp>-"
                        "<suite>); reuse a partial run's dir to resume it")
    p.add_argument("--allow-unfrozen", action="store_true",
                   help="run --ab despite a missing/mismatched freeze; stamps "
                        "the result preregistered: false")
    args = p.parse_args()

    modes = [bool(args.ab), bool(args.freeze), bool(args.validate),
             bool(args.replay), bool(args.report), bool(args.matrix_report),
             bool(args.concordance_sample)]
    if sum(modes) != 1:
        p.error("pick exactly one mode: --ab, --freeze, --validate, "
                "--replay DIR, --report DIR, --matrix-report DIR..., or "
                "--concordance-sample DIR...")
    if args.repeats < 1 or args.judge_repeats < 1 or args.concurrency < 1:
        p.error("--repeats, --judge-repeats, and --concurrency must be >= 1")
    if args.effort and not args.ab:
        p.error("--effort only applies to --ab runs")

    if args.freeze:
        cmd_freeze(args)
    elif args.validate:
        cmd_validate(args)
    elif args.replay:
        cmd_replay(args.replay)
    elif args.report:
        cmd_report(args.report)
    elif args.matrix_report:
        cmd_matrix_report(args)
    elif args.concordance_sample:
        cmd_concordance_sample(args)
    elif args.ab:
        cmd_ab(args)


if __name__ == "__main__":
    main()
