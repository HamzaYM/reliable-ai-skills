"""Task JSONL loading, schema validation, and canonical hashing.

The schema is documented in eval/schemas/task.schema.json; this module
enforces the same rules by hand (no jsonschema dependency).
"""
import hashlib
import json
import re

from . import FIXTURES_DIR, SKILLS_DIR

ID_RE = re.compile(r"^[a-z0-9-]+$")
SEGMENT_RE = re.compile(r"^[a-z0-9_.-]+$")
REQUIRED_FIELDS = ("id", "skill", "fixture", "prompt", "must_hits")
ALLOWED_FIELDS = set(REQUIRED_FIELDS) | {"judge_notes", "tags"}


def _safe_rel_path(value, nested):
    """True when value is traversal-free: [a-z0-9_.-] segments, no '..'."""
    segments = value.split("/") if nested else [value]
    return all(SEGMENT_RE.match(s) and s.strip(".") for s in segments)


class TaskError(Exception):
    """Raised when a task file fails to parse or validate."""


def load_tasks(path):
    """Parse a JSONL task file. Returns a list of task dicts.

    Raises TaskError with every problem found (not just the first).
    """
    errors = []
    tasks = []
    seen_ids = set()
    text = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{lineno}: invalid JSON: {exc}")
            continue
        errors.extend(
            f"{path.name}:{lineno}: {msg}" for msg in validate_task(obj)
        )
        if isinstance(obj, dict):
            tid = obj.get("id")
            if tid in seen_ids:
                errors.append(f"{path.name}:{lineno}: duplicate task id {tid!r}")
            seen_ids.add(tid)
            tasks.append(obj)
    if not tasks and not errors:
        errors.append(f"{path.name}: no tasks found")
    if errors:
        raise TaskError("\n".join(errors))
    return tasks


def validate_task(obj):
    """Structural validation of a single task object. Returns error strings."""
    errs = []
    if not isinstance(obj, dict):
        return ["task line is not a JSON object"]
    for field in REQUIRED_FIELDS:
        if field not in obj:
            errs.append(f"missing required field {field!r}")
    for field in obj:
        if field not in ALLOWED_FIELDS:
            errs.append(f"unknown field {field!r}")
    tid = obj.get("id")
    if tid is not None and (not isinstance(tid, str) or not ID_RE.match(tid)):
        errs.append(f"id must match [a-z0-9-]+, got {tid!r}")
    for field in ("skill", "fixture", "prompt"):
        val = obj.get(field)
        if field in obj and (not isinstance(val, str) or not val.strip()):
            errs.append(f"{field} must be a non-empty string")
    for field, nested in (("skill", True), ("fixture", False)):
        val = obj.get(field)
        if isinstance(val, str) and val.strip() and not _safe_rel_path(val, nested):
            errs.append(
                f"{field} must be {'slash-separated segments' if nested else 'one segment'}"
                f" of [a-z0-9_.-] with no '..', got {val!r}"
            )
    mh = obj.get("must_hits")
    if mh is not None:
        if not isinstance(mh, list) or not (2 <= len(mh) <= 6):
            errs.append("must_hits must be an array of 2 to 6 items")
        else:
            seen = set()
            for i, item in enumerate(mh):
                if (
                    not isinstance(item, dict)
                    or set(item) != {"id", "text"}
                    or not isinstance(item.get("id"), str)
                    or not isinstance(item.get("text"), str)
                    or not item["id"]
                    or not item["text"].strip()
                ):
                    errs.append(
                        f"must_hits[{i}] must be {{\"id\": str, \"text\": str}}"
                    )
                    continue
                if item["id"] in seen:
                    errs.append(f"must_hits[{i}] duplicate id {item['id']!r}")
                seen.add(item["id"])
    if "judge_notes" in obj and not isinstance(obj["judge_notes"], str):
        errs.append("judge_notes must be a string")
    if "tags" in obj and (
        not isinstance(obj["tags"], list)
        or not all(isinstance(t, str) for t in obj["tags"])
    ):
        errs.append("tags must be an array of strings")
    return errs


# Frontmatter keys a staged skill must never declare: each one would alter
# the consumer's runtime configuration (deliberation depth, serving model,
# context handling, or a delegated agent) in the loaded arm only, which
# would unblind the cold-vs-loaded comparison and contaminate every
# effort-sweep cell the skill appears in.
FORBIDDEN_SKILL_FRONTMATTER_KEYS = ("effort", "model", "context", "agent")


def skill_frontmatter_preflight(tasks, skills_dir=None):
    """Errors for staged skills whose SKILL.md frontmatter declares any
    runtime-configuration key (effort, model, context, agent).

    Run before any API call: a hit aborts the run outright. skills_dir is
    injectable for tests; live callers use the repo skills directory.
    """
    root = skills_dir if skills_dir is not None else SKILLS_DIR
    errs = []
    for skill in sorted({t["skill"] for t in tasks}):
        path = root / skill / "SKILL.md"
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue  # validate_refs reports missing skills
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not m:
            continue  # frontmatter presence is checked by --validate
        for key in FORBIDDEN_SKILL_FRONTMATTER_KEYS:
            if re.search(rf"^{key}\s*:", m.group(1), re.MULTILINE):
                errs.append(
                    f"skills/{skill}/SKILL.md: frontmatter declares {key!r}; "
                    f"a staged skill must not set runtime configuration "
                    f"(it would apply to the loaded arm only and unblind "
                    f"the comparison)"
                )
    return errs


def validate_refs(tasks):
    """Check that each task's skill and fixture exist on disk."""
    errs = []
    for task in tasks:
        skill_dir = SKILLS_DIR / task["skill"]
        if not (skill_dir / "SKILL.md").is_file():
            errs.append(
                f"task {task['id']}: skill not found: skills/{task['skill']}/SKILL.md"
            )
        fixture_dir = FIXTURES_DIR / task["fixture"]
        if not (fixture_dir / "build.sh").is_file():
            errs.append(
                f"task {task['id']}: fixture not found: eval/fixtures/{task['fixture']}/build.sh"
            )
    return errs


def canonical_task_json(task):
    """Canonical JSON text for hashing a single task."""
    return json.dumps(task, sort_keys=True, separators=(",", ":"))


def task_hash(task):
    return hashlib.sha256(canonical_task_json(task).encode("utf-8")).hexdigest()


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_name_for(task):
    """The skill's folder name (also its frontmatter name by repo convention)."""
    return task["skill"].rstrip("/").split("/")[-1]


def all_skill_names(skills_dir=None):
    """Leaf folder names of every staged skill (one per SKILL.md).

    The scrubber uses this to ban cross-skill name echoes: a staged skill's
    SKILL.md may cite a sibling skill by its exact name, and that sibling
    name unblinds a report just as much as the task's own skill name.
    Enumerated from disk so the ban list is the full frozen roster
    regardless of --skill task filtering. skills_dir is injectable for tests.
    """
    root = skills_dir if skills_dir is not None else SKILLS_DIR
    return sorted(p.parent.name for p in root.glob("*/*/SKILL.md"))
