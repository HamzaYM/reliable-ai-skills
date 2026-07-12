"""Pre-registration freeze: write and verify hash manifests for task files.

python eval/run.py --tasks X.jsonl --freeze  writes X.freeze.json.
--ab refuses to start unless the freeze exists and every recomputed hash
matches (task file, per-task canonical JSON, fixture build scripts and tree
hashes, and the grading instrument: agents/*.md and schemas/*.json).
--allow-unfrozen bypasses the gate and stamps the run
"preregistered": false. skills_snapshot is provenance only, never a gate.
"""
import datetime
import json
import subprocess

from . import AGENTS_DIR, EVAL_DIR, FIXTURES_DIR, REPO_ROOT, SCHEMAS_DIR, SKILLS_DIR
from .fixtures import load_manifest, tree_hash
from .tasks import file_sha256, task_hash


class FreezeError(Exception):
    pass


def freeze_path_for(tasks_path):
    return tasks_path.with_suffix(".freeze.json")


def _skill_dir_hash(skill_rel):
    return tree_hash(SKILLS_DIR / skill_rel)


def _git_head():
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def instrument_hashes():
    """Hashes of the grading instrument: judge/consumer prompts and schemas.

    Frozen and gated so the criteria a run is graded with cannot silently
    change between freeze and run.
    """
    files = sorted(AGENTS_DIR.glob("*.md")) + sorted(SCHEMAS_DIR.glob("*.json"))
    return {str(p.relative_to(EVAL_DIR)): file_sha256(p) for p in files}


def build_freeze(tasks_path, tasks):
    fixtures = {}
    skills = {}
    for task in tasks:
        fx = task["fixture"]
        if fx not in fixtures:
            manifest = load_manifest(fx)
            fixtures[fx] = {
                "build_sha256": file_sha256(FIXTURES_DIR / fx / "build.sh"),
                "tree_sha256": manifest["tree_sha256"],
            }
        sk = task["skill"]
        if sk not in skills:
            skills[sk] = _skill_dir_hash(sk)
    return {
        "frozen_at": datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "task_file_sha256": file_sha256(tasks_path),
        "tasks": {t["id"]: task_hash(t) for t in tasks},
        "fixtures": fixtures,
        "instruments": instrument_hashes(),
        "skills_snapshot": skills,
        "git_commit": _git_head(),
        "counts": {
            "tasks": len(tasks),
            "must_hits": sum(len(t["must_hits"]) for t in tasks),
        },
    }


def write_freeze(tasks_path, tasks):
    data = build_freeze(tasks_path, tasks)
    path = freeze_path_for(tasks_path)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path, data


def load_freeze(tasks_path):
    path = freeze_path_for(tasks_path)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def verify_freeze(tasks_path, tasks):
    """Recompute every gated hash and diff against the freeze file.

    Returns a list of mismatch descriptions; empty means the freeze holds.
    A missing freeze file is reported as a mismatch.
    """
    frozen = load_freeze(tasks_path)
    if frozen is None:
        return [f"no freeze file: {freeze_path_for(tasks_path)} (run --freeze first)"]
    errs = []
    actual_file = file_sha256(tasks_path)
    if actual_file != frozen.get("task_file_sha256"):
        errs.append(
            f"task file hash changed since freeze: {actual_file} != "
            f"{frozen.get('task_file_sha256')}"
        )
    frozen_tasks = frozen.get("tasks", {})
    for t in tasks:
        expected = frozen_tasks.get(t["id"])
        actual = task_hash(t)
        if expected is None:
            errs.append(f"task {t['id']} not present in freeze")
        elif expected != actual:
            errs.append(f"task {t['id']} edited since freeze")
    for tid in frozen_tasks:
        if tid not in {t["id"] for t in tasks}:
            errs.append(f"task {tid} was frozen but is missing from the task file")
    for fx, entry in frozen.get("fixtures", {}).items():
        build_path = FIXTURES_DIR / fx / "build.sh"
        if not build_path.is_file():
            errs.append(f"fixture {fx}: build.sh missing")
            continue
        if file_sha256(build_path) != entry.get("build_sha256"):
            errs.append(f"fixture {fx}: build.sh changed since freeze")
        try:
            manifest = load_manifest(fx)
        except Exception as exc:  # missing/corrupt manifest
            errs.append(f"fixture {fx}: {exc}")
            continue
        if manifest.get("tree_sha256") != entry.get("tree_sha256"):
            errs.append(f"fixture {fx}: manifest tree hash changed since freeze")
    frozen_instruments = frozen.get("instruments")
    if frozen_instruments is None:
        errs.append(
            "freeze has no instrument hashes (agents/, schemas/); re-run --freeze"
        )
    else:
        actual_instruments = instrument_hashes()
        for rel in sorted(set(frozen_instruments) | set(actual_instruments)):
            if frozen_instruments.get(rel) != actual_instruments.get(rel):
                errs.append(f"instrument {rel} changed since freeze")
    return errs


def current_skill_hashes(tasks):
    """Skill dir hashes at run time, recorded so freeze-to-run drift is visible."""
    return {sk: _skill_dir_hash(sk) for sk in sorted({t["skill"] for t in tasks})}
