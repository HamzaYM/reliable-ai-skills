"""Blinding scrubber and abort-on-leak verifier.

Judges see only scrubbed ## Answers sections. The scrubber replaces, per
task, an automatically built banned-token list with the neutral phrase
"project documentation" (cold reports naturally cite project docs, so the
replacement does not mark the treated report). Condition words and bare
"skill"/"skills" mentions are scrubbed with the same replacement in both
arms, so an innocent echo ("a skill guided me", "cold cache") never marks
an arm or wedges a run. Every substitution is logged.

Before any judge runs, verify_no_leak() greps the fully assembled judge
input for banned tokens plus condition words and the loaded-arm prompt
prefix; any hit aborts the run.
"""
import re

REPLACEMENT = "project documentation"

# Words that would reveal the experimental condition, including any bare
# mention of "skill(s)" (only loaded consumers are told about skills).
# Word-bounded so that e.g. "downloaded" or "harmless" do not
# false-positive.
CONDITION_WORDS_RE = re.compile(
    r"\b(cold|loaded|arm|arms|baseline|treatment|skills?)\b", re.IGNORECASE
)

# Static fragments of the loaded arm's prompt prefix (see consumer.py).
PREFIX_FRAGMENTS = (
    "Before starting, read",
    "let it guide your approach",
)


def _name_pattern(name):
    """Separator-agnostic skill-name regex.

    The folder name's segments may echo back joined by any run of hyphens,
    underscores, or spaces, in any mix, or with no separator at all
    ("git change-control for agents", "gitchangecontrolforagents"), so the
    segments are joined by [-_ ]* rather than matched as literal variants.
    """
    segments = [s for s in re.split(r"[-_ ]+", name) if s]
    return re.compile(
        r"\b" + r"[-_ ]*".join(re.escape(s) for s in segments) + r"\b",
        re.IGNORECASE,
    )


def banned_patterns(skill_rel, skill_name, other_skill_names=()):
    """Ordered (label, compiled_regex) list for one task's skill.

    Path-shaped patterns come first so a whole path is consumed in one
    substitution rather than leaving fragments behind.

    other_skill_names bans sibling skills by name as well. A staged skill's
    SKILL.md may cite another skill by its exact folder name, and a consumer
    that quotes that cross-reference leaks the loaded arm just as plainly as
    an echo of its own skill name. Task-scoped banning alone leaves those
    sibling names in the judge input (both the scrubber and verify_no_leak
    share this list, so the leak passes both). Each sibling name is matched
    separator-agnostically like the primary name.
    """
    pats = []
    # Any path-like token containing the markers, including the markers
    # alone. PATH_CHARS deliberately excludes punctuation like commas,
    # quotes, and parens so surrounding prose survives the substitution.
    path_chars = r"[\w./\\~-]*"
    pats.append(
        ("path:.claude/skills",
         re.compile(path_chars + r"\.claude/skills" + path_chars, re.IGNORECASE))
    )
    pats.append(
        ("path:SKILL.md",
         re.compile(path_chars + r"SKILL\.md" + path_chars, re.IGNORECASE))
    )
    pats.append(
        ("path:skill-folder",
         re.compile(path_chars + re.escape(skill_rel) + path_chars, re.IGNORECASE))
    )
    pats.append((f"name:{skill_name}", _name_pattern(skill_name)))
    for other in other_skill_names:
        if other and other != skill_name:
            pats.append((f"name:{other}", _name_pattern(other)))
    for phrase in ("the skill", "this skill", "skill file"):
        pats.append(
            (f"phrase:{phrase}", re.compile(r"\b" + re.escape(phrase) + r"\b", re.IGNORECASE))
        )
    # Last so multi-word phrases above are consumed whole first. Applied to
    # both arms' answers, so the substitution itself carries no signal.
    pats.append(("condition-word", CONDITION_WORDS_RE))
    return pats


def scrub_text(text, patterns):
    """Apply patterns in order. Returns (scrubbed_text, substitutions).

    Each substitution records the pattern label, the original matched text,
    the replacement, and the character offset at the time of substitution.
    """
    subs = []
    for label, pat in patterns:
        def _record(match, _label=label):
            subs.append(
                {
                    "pattern": _label,
                    "original": match.group(0),
                    "replacement": REPLACEMENT,
                    "offset": match.start(),
                }
            )
            return REPLACEMENT

        text = pat.sub(_record, text)
    return text, subs


def verify_no_leak(text, patterns):
    """Grep an assembled judge input for anything condition-revealing.

    Returns a list of hits: {"pattern", "offset", "snippet"}. Empty list
    means the input is clean. Any hit must abort the run before judging.
    """
    hits = []

    def _add(label, match):
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 30)
        hits.append(
            {
                "pattern": label,
                "offset": match.start(),
                "snippet": text[start:end],
            }
        )

    for label, pat in patterns:
        for m in pat.finditer(text):
            _add(label, m)
    for frag in PREFIX_FRAGMENTS:
        for m in re.finditer(re.escape(frag), text, re.IGNORECASE):
            _add("prompt-prefix", m)
    return hits
