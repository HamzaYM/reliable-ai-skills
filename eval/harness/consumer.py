"""Consumer runner: headless claude CLI invocation and report parsing.

Consumers run as `claude -p --output-format json` subprocesses with
read-oriented tools, cwd set to a disposable fixture workspace. The loaded
arm's workspace contains the skill at .claude/skills/<name>/ and its prompt
is prefixed with an explicit instruction to read it. The cold workspace
contains no skill files at all.

Auth: the subprocess inherits the environment, so a subscription login is
the default path and ANTHROPIC_API_KEY works as a fallback when exported.
"""
import json
import os
import re
import subprocess
import time
from pathlib import Path

from . import AGENTS_DIR

ALLOWED_TOOLS = "Read,Grep,Glob,Bash"
CONSUMER_TIMEOUT = 600  # seconds; one retry on timeout or failure
SECTION_ORDER = ("plan", "actions", "answers", "next steps", "confidence and gaps")

# Identical per-message output ceiling for every consumer invocation, in
# both arms, at every effort level, pinned via the CLI's
# CLAUDE_CODE_MAX_OUTPUT_TOKENS environment variable on the subprocess.
# 64000 is the maxOutputTokens the CLI itself reported (modelUsage) for the
# committed smoke run 20260710T003211Z-example-sonnet-medium, so pinning it
# changes nothing for existing cells; it only guarantees the ceiling cannot
# drift across models, effort levels, or CLI upgrades. A consumer run whose
# output hits this ceiling is truncated-by-limit and therefore invalid:
# one retry, then the task is excluded-as-invalid.
CONSUMER_MAX_OUTPUT_TOKENS = 64000

# The claude CLI does NOT fail on a bad effort value: it prints a warning
# to stderr and silently runs at the default effort (verified live on
# 2.1.206). Any of these markers on stderr therefore means the requested
# effort was not applied, and the run must fail closed.
EFFORT_WARNING_MARKERS = (
    "unknown --effort value",
    "effort not supported",
    "invalid effort",
    "ignoring it and using the default effort",
    "not applied: claude_code_effort_level",
)

# Effort-invariant models: the API serves haiku-class models at a single
# fixed deliberation level (no effort knob), and the claude CLI accepts
# --effort for them SILENTLY (verified live on 2.1.206: `claude -p ...
# --model haiku --effort medium` emits no stderr warning at all). Because
# there is no warning, the stderr fail-closed probe cannot prove a level
# was or was not applied, so a haiku cell run with --effort would be an
# unverifiable label. The harness therefore classifies these models as
# effort-invariant, records their cells as effort "none", and refuses
# --effort for them as unavailable by design rather than falling back
# silently.
EFFORT_INVARIANT_MODEL_MARKERS = ("haiku",)

LOADED_PREFIX_TEMPLATE = (
    "Before starting, read `.claude/skills/{name}/SKILL.md` in full and let "
    "it guide your approach.\n\n"
)


class ConsumerError(Exception):
    pass


class ReportParseError(Exception):
    pass


def load_persona():
    return (AGENTS_DIR / "consumer-persona.md").read_text(encoding="utf-8")


def build_prompt(persona, task_prompt, skill_name=None):
    """Persona + (loaded-arm prefix if skill_name) + base task prompt."""
    prefix = LOADED_PREFIX_TEMPLATE.format(name=skill_name) if skill_name else ""
    return f"{persona.rstrip()}\n\n{prefix}{task_prompt}"


def claude_version():
    try:
        proc = subprocess.run(
            ["claude", "--version"], capture_output=True, text=True, timeout=60
        )
    except FileNotFoundError:
        raise ConsumerError(
            "claude CLI not found on PATH; it is required for --ab and "
            "--dry-run (see eval/README.md)"
        ) from None
    return proc.stdout.strip() or proc.stderr.strip()


def parse_effort_help(help_text):
    """Extract the --effort option and its advertised levels from CLI help.

    Returns (levels, verbatim_snippet). Raises ConsumerError when the help
    text does not advertise --effort or its level list cannot be parsed:
    running anyway would mean the flag is dropped or ignored, i.e. a silent
    default-effort run stamped with the wrong effort level.
    """
    lines = help_text.splitlines()
    for i, line in enumerate(lines):
        if "--effort" not in line:
            continue
        block = [line.strip()]
        for cont in lines[i + 1:i + 4]:
            if cont.strip().startswith("--"):
                break
            block.append(cont.strip())
        snippet = " ".join(s for s in block if s)
        m = re.search(r"\(([a-z]+(?:,\s*[a-z]+)+)\)", snippet)
        if not m:
            raise ConsumerError(
                "claude --help mentions --effort but its accepted level "
                f"list could not be parsed from: {snippet!r}"
            )
        return [s.strip() for s in m.group(1).split(",")], snippet
    raise ConsumerError(
        "this claude CLI does not advertise an --effort option in --help; "
        "refusing to run with --effort because the level could not reach "
        "the model (upgrade the CLI or drop --effort)"
    )


def verify_effort_support(level, help_text=None):
    """Fail-closed pre-flight for --effort.

    The installed CLI must advertise the --effort flag AND the requested
    level. Returns {"advertised_levels", "cli_help_evidence"} for run-meta.
    help_text is injectable for tests; live callers fetch `claude --help`.
    """
    if help_text is None:
        help_text = _fetch_help()
    levels, snippet = parse_effort_help(help_text)
    if level not in levels:
        raise ConsumerError(
            f"--effort {level!r} is not among the levels this claude CLI "
            f"advertises ({', '.join(levels)}); refusing to run: the CLI "
            f"warns on unknown effort values and silently falls back to "
            f"the default effort"
        )
    return {"advertised_levels": levels, "cli_help_evidence": snippet}


def effort_invariant_model(model):
    """True for models with no effort knob (haiku-class, by marker)."""
    lowered = (model or "").lower()
    return any(marker in lowered for marker in EFFORT_INVARIANT_MODEL_MARKERS)


def _fetch_help():
    try:
        proc = subprocess.run(
            ["claude", "--help"], capture_output=True, text=True, timeout=60
        )
    except FileNotFoundError:
        raise ConsumerError(
            "claude CLI not found on PATH; it is required for effort "
            "verification (see eval/README.md)"
        ) from None
    return proc.stdout + proc.stderr


def enumerate_effort_support(model, help_text=None):
    """Per-model effort enumeration, recorded verbatim in run-meta.

    The CLI's --help advertises one global level list; per-model support
    is that list minus what the model's own behavior rules out. For
    effort-invariant models (haiku-class) the CLI accepts --effort with
    no stderr warning (verified live on 2.1.206), so the behavioral probe
    cannot prove a level was applied: their supported level list is empty
    and --effort with them is unavailable by design. For every other
    model, each consumer invocation's stderr is scanned for the CLI's
    effort warnings (the existing fail-closed probe), so a persisted run
    proves the requested level was accepted.
    """
    if help_text is None:
        help_text = _fetch_help()
    try:
        levels, snippet = parse_effort_help(help_text)
    except ConsumerError as exc:
        levels, snippet = [], f"no --effort support in this CLI: {exc}"
    invariant = effort_invariant_model(model)
    return {
        "model": model,
        "cli_advertised_levels": levels,
        "cli_help_evidence": snippet,
        "effort_invariant": invariant,
        "supported_levels": [] if invariant else levels,
        "detected_default": {
            **ambient_effort_sources(),
            "note": (
                "effort-invariant model: a single fixed deliberation "
                "level, recorded as effort none"
                if invariant else
                "the CLI exposes no per-model default effort in --help or "
                "headless output; the ambient sources above are the only "
                "observable default inputs, and the effort value recorded "
                "in run-meta is authoritative"
            ),
        },
        "probe": (
            "not probeable: the CLI accepts --effort for this model "
            "without any stderr warning (verified live on 2.1.206), so "
            "--effort with this model is refused as unavailable by design "
            "instead of running unverifiable"
            if invariant else
            "stderr effort-warning scan on every consumer invocation, "
            "fail closed"
        ),
    }


def effort_warning(stderr_text):
    """Return the CLI's effort warning line from stderr, or None."""
    for line in (stderr_text or "").splitlines():
        lowered = line.lower()
        if any(marker in lowered for marker in EFFORT_WARNING_MARKERS):
            return line.strip()
    return None


def ambient_effort_sources():
    """Non-flag effort sources that can shape a default-effort run.

    Recorded in run-meta so 'default' is auditable: the CLI also reads an
    effortLevel key from user settings and a CLAUDE_CODE_EFFORT_LEVEL
    environment variable, and either would silently define what 'default'
    meant for this run.
    """
    settings_level = None
    try:
        data = json.loads(
            (Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8")
        )
        if isinstance(data, dict):
            settings_level = data.get("effortLevel")
    except (OSError, json.JSONDecodeError):
        settings_level = None
    return {
        "env_CLAUDE_CODE_EFFORT_LEVEL": os.environ.get("CLAUDE_CODE_EFFORT_LEVEL"),
        "user_settings_effortLevel": settings_level,
    }


def ambient_user_skills(skills_root=None):
    """Names of user-level skills present at run time, for the audit trail.

    Cold-arm isolation from these is enforced elsewhere (no Skill tool in
    the consumer allowlist, no .claude directory in the cold workspace);
    this records what existed on the machine so the isolation claim is
    checkable per run rather than asserted once.
    """
    root = Path(skills_root) if skills_root else Path.home() / ".claude" / "skills"
    try:
        return sorted(p.name for p in root.iterdir() if p.is_dir())
    except OSError:
        return []


def consumer_env(max_output_tokens):
    """Subprocess environment with the pinned output ceiling applied."""
    env = dict(os.environ)
    env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(max_output_tokens)
    return env


def stop_reason(cli_out):
    """Best-available stop reason from headless CLI output.

    The CLI does not expose the API stop_reason directly on every version,
    so this prefers an explicit stop_reason key and falls back to the
    result subtype (e.g. "success").
    """
    for key in ("stop_reason", "stopReason"):
        value = cli_out.get(key)
        if isinstance(value, str) and value:
            return value
    value = cli_out.get("subtype")
    return value if isinstance(value, str) and value else None


def peak_message_output_tokens(cli_out):
    """Largest single-message output_tokens from usage iterations, or None.

    The pinned ceiling is per message, so only per-iteration counts are
    comparable to it; the run-total output_tokens is not (a legitimate
    multi-turn run can exceed the per-message ceiling in total).
    """
    usage = cli_out.get("usage") or {}
    per_msg = [
        i.get("output_tokens")
        for i in (usage.get("iterations") or [])
        if isinstance(i, dict) and isinstance(i.get("output_tokens"), int)
    ]
    return max(per_msg) if per_msg else None


def check_truncation(cli_out, limit):
    """Fail closed when the run hit the pinned output ceiling.

    Truncated-by-limit is a pre-registered invalid-run condition: the
    answer text is not the model's complete answer, so grading it would
    conflate the effort/skill effect with the budget. Raises ConsumerError
    (retried once by run_claude, then the task is excluded-as-invalid).
    """
    sr = stop_reason(cli_out)
    if isinstance(sr, str) and "max_tokens" in sr.lower():
        raise ConsumerError(
            f"consumer output truncated by the pinned {limit}-token ceiling "
            f"(stop reason {sr!r}); truncated-by-limit runs are invalid"
        )
    peak = peak_message_output_tokens(cli_out)
    if peak is not None and peak >= limit:
        raise ConsumerError(
            f"consumer output hit the pinned {limit}-token ceiling (peak "
            f"message {peak} output tokens); truncated-by-limit runs are "
            f"invalid"
        )


def effective_models(cli_out):
    """All model IDs the CLI reports having used for this invocation."""
    return sorted(cli_out.get("modelUsage") or {})


def primary_model(cli_out):
    """The model that produced the most output tokens (the answering
    model), or None when the CLI output carries no modelUsage."""
    mu = cli_out.get("modelUsage") or {}
    if not mu:
        return None
    return max(mu, key=lambda m: (mu[m] or {}).get("outputTokens") or 0)


def model_matches(requested, effective):
    """True when the effective model ID satisfies the requested model.

    Accepts an exact ID match or a CLI alias contained in the full ID
    (e.g. requested "sonnet" served by "claude-sonnet-5").
    """
    if not requested or not effective:
        return False
    r, e = requested.lower(), effective.lower()
    return r == e or r in e


def check_model_fallback(cli_out, requested):
    """Fail closed on cross-model fallback (pre-registered invalid run).

    Returns the effective answering model ID (None when the CLI output has
    no modelUsage to check against). Raises ConsumerError when a different
    model answered than the one requested.
    """
    effective = primary_model(cli_out)
    if effective is not None and not model_matches(requested, effective):
        raise ConsumerError(
            f"cross-model fallback: requested model {requested!r} but the "
            f"answering model was {effective!r} (models used: "
            f"{', '.join(effective_models(cli_out))}); such runs are "
            f"invalid by pre-registered rule"
        )
    return effective


def thinking_usage(cli_out):
    """Thinking/reasoning token counters from usage, when the CLI exposes
    any; None otherwise (output_tokens then includes thinking opaquely)."""
    usage = cli_out.get("usage") or {}
    found = {
        k: v for k, v in usage.items()
        if isinstance(k, str) and ("thinking" in k.lower() or "reasoning" in k.lower())
    }
    return found or None


def build_command(prompt, model, extra_args=(), effort=None):
    cmd = [
        "claude",
        "-p",
        prompt,
        "--model",
        model,
        "--output-format",
        "json",
        *extra_args,
    ]
    if effort:
        cmd += ["--effort", effort]
    return cmd


def _invoke(prompt, cwd, model, timeout, extra_args=(), effort=None,
            max_output_tokens=None, check_model=False):
    cmd = build_command(prompt, model, extra_args, effort)
    env = consumer_env(max_output_tokens) if max_output_tokens else None
    proc = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
        env=env,
    )
    if proc.returncode != 0:
        raise ConsumerError(
            f"claude exited {proc.returncode}: {proc.stderr.strip()[:2000]}"
        )
    if effort:
        warning = effort_warning(proc.stderr)
        if warning:
            # Fail closed: the CLI ran anyway at the default effort, which
            # would silently mislabel this run's effort cell.
            raise ConsumerError(
                f"claude did not apply --effort {effort}: {warning!r}"
            )
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ConsumerError(f"unparseable claude JSON output: {exc}") from exc
    if out.get("is_error"):
        raise ConsumerError(f"claude reported an error result: {str(out)[:2000]}")
    if check_model:
        check_model_fallback(out, model)
    if max_output_tokens:
        check_truncation(out, max_output_tokens)
    return out


def run_claude(prompt, cwd, model, timeout, extra_args=(), effort=None,
               max_output_tokens=None, check_model=False):
    """One retry on timeout/failure, with a backoff when rate limited."""
    attempts = 0
    last_err = None
    while attempts < 2:
        attempts += 1
        try:
            out = _invoke(prompt, cwd, model, timeout, extra_args, effort,
                          max_output_tokens, check_model)
            return out, attempts
        except subprocess.TimeoutExpired as exc:
            last_err = ConsumerError(f"timed out after {timeout}s")
        except ConsumerError as exc:
            last_err = exc
            msg = str(exc)
            if "429" in msg or "rate" in msg.lower():
                time.sleep(30)
    raise last_err


def run_consumer(prompt, workspace, model, timeout=CONSUMER_TIMEOUT, effort=None):
    """Run one consumer. Returns raw CLI output metadata plus the report text."""
    out, attempts = run_claude(
        prompt, workspace, model, timeout,
        extra_args=("--allowedTools", ALLOWED_TOOLS),
        effort=effort,
        max_output_tokens=CONSUMER_MAX_OUTPUT_TOKENS,
        check_model=True,
    )
    report = out.get("result")
    if not isinstance(report, str) or not report.strip():
        raise ConsumerError("claude output had no result text")
    return {
        "report": report,
        "attempts": attempts,
        "usage": out.get("usage"),
        "model_usage": out.get("modelUsage"),
        "total_cost_usd": out.get("total_cost_usd"),
        "duration_ms": out.get("duration_ms"),
        "num_turns": out.get("num_turns"),
        "session_id": out.get("session_id"),
        # Validity provenance. A truncated or cross-model-fallback run
        # raises before reaching this point (retried once, then the task is
        # excluded-as-invalid), so persisted results always carry
        # model_fallback: false and a non-truncating stop reason.
        "stop_reason": stop_reason(out),
        "max_output_tokens": CONSUMER_MAX_OUTPUT_TOKENS,
        "peak_message_output_tokens": peak_message_output_tokens(out),
        "thinking_usage": thinking_usage(out),
        "model_effective": primary_model(out),
        "models_effective": effective_models(out),
        "model_fallback": False,
        # A CLI effort warning also raises (fail closed), so in every
        # persisted result the effective effort equals the requested one.
        "effort_effective": effort or "default",
    }


_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def parse_sections(report):
    """Split a report on ## headings. Returns {lowercased heading: body}."""
    sections = {}
    matches = list(_HEADING_RE.finditer(report))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(report)
        sections[m.group(1).strip().lower()] = report[start:end].strip()
    return sections


def extract_answers(report):
    """Return the ## Answers section, strictly.

    A missing or empty Answers section is a hard error for the run: the
    harness never falls back to full report text (that would leak condition
    signal into judge inputs).
    """
    sections = parse_sections(report)
    body = sections.get("answers")
    if not body:
        raise ReportParseError("report has no non-empty '## Answers' section")
    return body


def comprehension_check(report, skill_name):
    """Stage B (unblinded, non-scoring): did the loaded run read the skill?

    Mechanical grep of the ## Actions section (whole report as fallback when
    the section is missing) for the skill path. Never reaches a judge and
    never changes a score.
    """
    sections = parse_sections(report)
    haystack = sections.get("actions", report)
    needles = (".claude/skills", "SKILL.md", skill_name)
    for line in haystack.splitlines():
        if any(n.lower() in line.lower() for n in needles):
            return {"skill_read": True, "evidence": line.strip()[:300]}
    return {"skill_read": False, "evidence": None}
