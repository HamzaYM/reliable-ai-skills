"""Judge input assembly and CLI invocation (blinded, stage A).

Judge inputs are assembled from an allowlist of fields: the base task
prompt, the frozen must-hits, optional frozen judge_notes, and the two
scrubbed ## Answers sections in seeded order. Nothing else can reach the
judge by construction. Judges run through the claude CLI with a JSON schema
and no tools.

Every comparison is graded by a two-judge confirmatory panel behind the
identical blinding stack: one Sonnet-class and one Opus-class judge, both
pinned by exact model ID and both pinned at --effort medium, never varying
across cells. The exact IDs below are the full model IDs the installed CLI
(2.1.206) resolves the sonnet and opus aliases to, verified live; pinning
full IDs instead of aliases means a future CLI's alias drift cannot move a
judge, and cross-model fallback is checked against an exact string.

A third pinned adjudicator resolves primary-judge disagreements: each
report-slot must-hit mark the two primaries disagree on is scored once by
the adjudicator on a minimal input (the disputed expectation, the two
blinded report slots, the judging frame) through a narrow binary schema;
the final mark is the two-of-three majority and disputed marks never
leave any denominator.
"""
import json
import re

from . import AGENTS_DIR, SCHEMAS_DIR
from .consumer import (
    effective_models,
    primary_model,
    run_claude,
)

JUDGE_PANEL = ("claude-sonnet-5", "claude-opus-4-8")
JUDGE_EFFORT = "medium"

# Pinned adjudicator: exact model ID and effort, recorded in run-meta,
# immutable after data per the pre-registration.
ADJUDICATOR_MODEL = "claude-fable-5"
ADJUDICATOR_EFFORT = "medium"


class JudgeError(Exception):
    pass


def load_judge_prompt():
    return (AGENTS_DIR / "judge-prompt.md").read_text(encoding="utf-8")


def judge_schema_path():
    return SCHEMAS_DIR / "judge.schema.json"


def _schema_for_cli(path):
    """A --json-schema payload: inline JSON without the "$schema" key.

    claude CLI 2.1.x rejects a top-level "$schema" key in --json-schema
    payloads, so it is stripped at call time only; the schema file keeps
    the key for documentation and editor tooling.
    """
    schema = json.loads(path.read_text(encoding="utf-8"))
    schema.pop("$schema", None)
    return json.dumps(schema)


def schema_for_cli():
    return _schema_for_cli(judge_schema_path())


def load_adjudicator_prompt():
    return (AGENTS_DIR / "adjudicator-prompt.md").read_text(encoding="utf-8")


def adjudicator_schema_path():
    return SCHEMAS_DIR / "adjudicator.schema.json"


def adjudicator_schema_for_cli():
    return _schema_for_cli(adjudicator_schema_path())


def assemble_input(judge_frame, task_prompt, must_hits, judge_notes, answers_1, answers_2):
    """Build the full judge prompt from allowlisted fields only."""
    lines = [judge_frame.rstrip(), "", "## Task given to both engineers", "", task_prompt.strip(), "", "## Expectations", ""]
    for mh in must_hits:
        lines.append(f"- ({mh['id']}) {mh['text']}")
    if judge_notes:
        lines += ["", "## Grading notes", "", judge_notes.strip()]
    lines += ["", "## Report 1", "", answers_1.strip(), "", "## Report 2", "", answers_2.strip(), ""]
    return "\n".join(lines)


def _parse_result(result):
    if isinstance(result, dict):
        return result
    text = result.strip()
    # Strip a markdown code fence if the model wrapped its JSON.
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    return json.loads(text)


def validate_judgment(judgment, must_hit_ids):
    """Minimal shape check mirroring judge.schema.json."""
    if not isinstance(judgment, dict):
        raise JudgeError("judgment is not an object")
    exps = judgment.get("expectations")
    if not isinstance(exps, list):
        raise JudgeError("judgment missing expectations array")
    seen = set()
    for e in exps:
        eid = e.get("expectation_id")
        if eid in seen:
            raise JudgeError(f"duplicate expectation {eid!r} in one judgment")
        seen.add(eid)
        for slot in ("report_1", "report_2"):
            mark = e.get(slot)
            if not isinstance(mark, dict) or not isinstance(mark.get("hit"), bool):
                raise JudgeError(f"expectation {eid}: bad {slot} mark")
    missing = set(must_hit_ids) - seen
    if missing:
        raise JudgeError(f"judgment missing expectations: {sorted(missing)}")
    if not isinstance(judgment.get("comparative_verdict"), str):
        raise JudgeError("judgment missing comparative_verdict")
    return judgment


def run_judge(judge_input, model, must_hit_ids, cwd, timeout=300,
              effort=JUDGE_EFFORT):
    """Invoke one judge. Returns (validated_judgment, raw_cli_output).

    The judge effort is pinned (medium) and fail-closed exactly like the
    consumers': any CLI effort warning on stderr fails the invocation, and
    a judge answered by a model other than the requested pinned ID fails as
    cross-model fallback. A persisted judge output therefore proves both
    the requested model and the requested effort were accepted.
    """
    # claude CLI 2.1.x requires --json-schema as inline JSON, not a file
    # path, and rejects a top-level "$schema" key (see schema_for_cli).
    schema_json = schema_for_cli()
    out, attempts = run_claude(
        judge_input,
        cwd,
        model,
        timeout,
        extra_args=(
            "--json-schema", schema_json,
            "--allowedTools", "",
        ),
        effort=effort,
        check_model=True,
    )
    judgment = validate_judgment(_parse_result(out.get("result")), must_hit_ids)
    return judgment, {
        "attempts": attempts,
        "usage": out.get("usage"),
        "total_cost_usd": out.get("total_cost_usd"),
        "duration_ms": out.get("duration_ms"),
        "model_requested": model,
        "model_effective": primary_model(out),
        "models_effective": effective_models(out),
        # Fail-closed provenance: an effort warning or a cross-model
        # fallback raises before this point, so persisted values always
        # equal the requested ones.
        "effort_requested": effort or "default",
        "effort_effective": effort or "default",
    }


SLOT_NAMES = {"report_1": "Report 1", "report_2": "Report 2"}


def assemble_adjudicator_input(frame, must_hit_text, slot, answers_1, answers_2):
    """Minimal adjudicator prompt: the judging frame, the one disputed
    expectation, and the two blinded report slots. Nothing else (no other
    expectations, no judge notes, no task prompt) can reach the
    adjudicator by construction."""
    if slot not in SLOT_NAMES:
        raise JudgeError(f"unknown report slot {slot!r}")
    lines = [
        frame.rstrip(), "",
        "## Disputed expectation", "", must_hit_text.strip(), "",
        f"## Report under dispute: {SLOT_NAMES[slot]}", "",
        "## Report 1", "", answers_1.strip(), "",
        "## Report 2", "", answers_2.strip(), "",
    ]
    return "\n".join(lines)


def validate_adjudication(mark):
    """Minimal shape check mirroring adjudicator.schema.json."""
    if not isinstance(mark, dict) or not isinstance(mark.get("hit"), bool) \
            or not isinstance(mark.get("evidence"), str):
        raise JudgeError(
            "adjudicator output is not a {hit: bool, evidence: str} mark"
        )
    return mark


def run_adjudicator(adjudicator_input, cwd, timeout=300):
    """Invoke the pinned adjudicator on one disputed report-slot mark.

    Returns (validated_mark, raw_cli_meta). Pinned exactly like the
    primary judges: fail-closed on CLI effort warnings and on cross-model
    fallback, with one retry inside run_claude; a failure after that retry
    propagates to the caller, which applies the judge-failure exclusion.
    """
    schema_json = adjudicator_schema_for_cli()
    out, attempts = run_claude(
        adjudicator_input,
        cwd,
        ADJUDICATOR_MODEL,
        timeout,
        extra_args=(
            "--json-schema", schema_json,
            "--allowedTools", "",
        ),
        effort=ADJUDICATOR_EFFORT,
        check_model=True,
    )
    mark = validate_adjudication(_parse_result(out.get("result")))
    return mark, {
        "attempts": attempts,
        "usage": out.get("usage"),
        "total_cost_usd": out.get("total_cost_usd"),
        "duration_ms": out.get("duration_ms"),
        "model_requested": ADJUDICATOR_MODEL,
        "model_effective": primary_model(out),
        "models_effective": effective_models(out),
        "effort_requested": ADJUDICATOR_EFFORT,
        "effort_effective": ADJUDICATOR_EFFORT,
    }
