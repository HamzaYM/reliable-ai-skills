"""Publishability lint, run by --validate over tasks and fixtures.

Hard fail (errors):
  - email addresses outside example.com
  - 12-digit AWS-account-shaped numbers
  - IPs outside documentation ranges and loopback
  - URLs/hostnames not under example.com, example.org, example.net,
    localhost, or loopback
  - SSN-shaped and phone-shaped strings
  - any term from the maintainer's private denylist file
    (eval/denylist.local.txt or eval/private-denylist.txt, gitignored,
    loaded only if present)

Warn:
  - ticket-ID shapes ([A-Z]{2,5}-\\d+) outside the fixture's declared fake
    scheme (manifest.json "fake_ticket_prefixes")
  - PHI-ish terms
  - person-name heuristics (honorific followed by a capitalized name)
  - condition words that would trip the pre-judging leak verifier if they
    appeared in a task prompt or must-hit
"""
import ipaddress
import re

from . import EVAL_DIR
from .scrub import CONDITION_WORDS_RE

DENYLIST_FILENAMES = ("denylist.local.txt", "private-denylist.txt")

EMAIL_RE = re.compile(r"\b[\w.+-]+@([\w-]+(?:\.[\w-]+)+)\b")
AWS_ACCOUNT_RE = re.compile(r"\b\d{12}\b")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
URL_RE = re.compile(r"\bhttps?://([^/\s\"'<>]+)", re.IGNORECASE)
HOSTNAME_RE = re.compile(
    r"\b([a-z0-9][a-z0-9-]*(?:\.[a-z0-9][a-z0-9-]*)*\.(?:com|net|org|io|ai|dev|co|edu|gov))\b",
    re.IGNORECASE,
)
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE_RE = re.compile(r"\b\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b")
TICKET_RE = re.compile(r"\b([A-Z]{2,5})-\d+\b")
PERSON_RE = re.compile(r"\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+\b")
PHI_RE = re.compile(
    r"\b(patient|diagnosis|medical record|mrn|date of birth|social security"
    r"|health record|prescription|clinical note)\b",
    re.IGNORECASE,
)

ALLOWED_DOMAINS = ("example.com", "example.org", "example.net", "localhost")
DOC_NETWORKS = [
    ipaddress.ip_network(n)
    for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "127.0.0.0/8")
]


def load_denylist(eval_dir=EVAL_DIR):
    """Private client-term denylist; each non-comment line is a banned term."""
    terms = []
    for name in DENYLIST_FILENAMES:
        path = eval_dir / name
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    terms.append(line)
    return terms


def _domain_allowed(host):
    host = host.lower().rstrip(".").split(":")[0]
    if host in ALLOWED_DOMAINS:
        return True
    if any(host.endswith("." + d) for d in ALLOWED_DOMAINS):
        return True
    try:
        return _ip_allowed(host)
    except ValueError:
        return False


def _ip_allowed(text):
    ip = ipaddress.ip_address(text)
    return any(ip in net for net in DOC_NETWORKS) or str(ip) == "0.0.0.0"


def lint_text(text, source, allowed_ticket_prefixes=(), denylist=()):
    """Returns (errors, warnings), each a list of strings."""
    errors, warnings = [], []

    def err(msg):
        errors.append(f"{source}: {msg}")

    def warn(msg):
        warnings.append(f"{source}: {msg}")

    for m in EMAIL_RE.finditer(text):
        if not _domain_allowed(m.group(1)):
            err(f"email outside example.com: {m.group(0)!r}")
    for m in AWS_ACCOUNT_RE.finditer(text):
        err(f"AWS-account-shaped 12-digit number: {m.group(0)!r}")
    for m in IP_RE.finditer(text):
        try:
            if not _ip_allowed(m.group(0)):
                err(f"IP outside documentation ranges: {m.group(0)!r}")
        except ValueError:
            pass  # e.g. 999.1.1.1 is not an IP
    for m in URL_RE.finditer(text):
        if not _domain_allowed(m.group(1)):
            err(f"URL host not under example.com/localhost: {m.group(1)!r}")
    for m in HOSTNAME_RE.finditer(text):
        if not _domain_allowed(m.group(1)):
            err(f"hostname-shaped string: {m.group(1)!r}")
    for m in SSN_RE.finditer(text):
        err(f"SSN-shaped string: {m.group(0)!r}")
    for m in PHONE_RE.finditer(text):
        err(f"phone-shaped string: {m.group(0)!r}")
    for term in denylist:
        if term.lower() in text.lower():
            err(f"private denylist term present: {term!r}")
    for m in TICKET_RE.finditer(text):
        if m.group(1) not in allowed_ticket_prefixes:
            warn(f"ticket-ID shape outside declared fake scheme: {m.group(0)!r}")
    for m in PHI_RE.finditer(text):
        warn(f"PHI-ish term: {m.group(0)!r}")
    for m in PERSON_RE.finditer(text):
        warn(f"person-name heuristic: {m.group(0)!r}")
    return errors, warnings


def lint_task(task, allowed_ticket_prefixes=(), denylist=()):
    errors, warnings = [], []
    parts = [("prompt", task.get("prompt", ""))]
    for mh in task.get("must_hits", []):
        parts.append((f"must_hit {mh.get('id')}", mh.get("text", "")))
    if task.get("judge_notes"):
        parts.append(("judge_notes", task["judge_notes"]))
    for label, text in parts:
        e, w = lint_text(
            text, f"task {task.get('id')} {label}", allowed_ticket_prefixes, denylist
        )
        errors.extend(e)
        warnings.extend(w)
        for m in CONDITION_WORDS_RE.finditer(text):
            warnings.append(
                f"task {task.get('id')} {label}: contains {m.group(0)!r}, which "
                f"will abort every A/B run at the pre-judging leak check"
            )
    return errors, warnings


def lint_fixture_files(fixture_dir, allowed_ticket_prefixes=(), denylist=()):
    """Lint every text file in the fixture source directory (not .git)."""
    errors, warnings = [], []
    for p in sorted(fixture_dir.rglob("*")):
        if not p.is_file() or ".git" in p.relative_to(fixture_dir).parts:
            continue
        if p.name == "manifest.json":
            continue  # machine-generated hashes
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        e, w = lint_text(
            text,
            f"fixture file {p.relative_to(fixture_dir.parent)}",
            allowed_ticket_prefixes,
            denylist,
        )
        errors.extend(e)
        warnings.extend(w)
    return errors, warnings
