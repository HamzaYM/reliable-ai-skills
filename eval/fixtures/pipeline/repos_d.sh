# Sourced by build.sh. Repos: ticket-scorer.

# ------------------------------------------------------------------ sysdbg-t2
build_ticket_scorer() {
  local R="$WS/ticket-scorer"
  git init -q -b main "$R"
  cd "$R"
  mkdir -p pipeline/metrics config fixtures investigations

  cat > README.md <<'EOF'
# ticket-scorer

Nightly LLM ticket-classification pipeline: it classifies incoming support
tickets and scores its predictions against a labeled evaluation set. Tickets
use the SCORE-N scheme. The classifier is a deterministic offline keyword stub
so batch and single-item runs are reproducible without network access.
EOF
  cat > pipeline/__init__.py <<'EOF'
EOF
  cat > pipeline/classifier.py <<'EOF'
"""Deterministic offline ticket classifier.

No network and no model call: the category is decided by the first matching
keyword group, so batch and single-item scoring are fully reproducible.
"""

RULES = [
    ("billing", ("invoice", "refund", "charge", "payment", "billing", "receipt")),
    ("bug", ("error", "crash", "broken", "stack trace", "exception", "500")),
    ("account", ("login", "log in", "password", "locked out", "sign in", "reset")),
    ("shipping", ("delivery", "shipment", "tracking", "arrived", "package")),
]
DEFAULT = "other"


def predict_category(text):
    lowered = text.lower()
    for label, keywords in RULES:
        if any(kw in lowered for kw in keywords):
            return label
    return DEFAULT
EOF
  cat > pipeline/preprocess.py <<'EOF'
"""Text preprocessing for the scoring pipeline."""
import re


def normalize_batch(text):
    """Batch normalization: lowercase, strip a leading reply prefix, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"^\s*re:\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_simple(text):
    """Single-item normalization: lowercase only."""
    return text.lower()
EOF
  # score_batch.py: at this baseline the loader's required-keys check and the
  # eval fixtures both use the pre-migration `label` schema.
  cat > pipeline/score_batch.py <<'EOF'
"""Nightly batch scorer: grades ticket-category predictions against the eval set."""
import json
import statistics
from pathlib import Path

from pipeline.classifier import predict_category
from pipeline.preprocess import normalize_batch

CONFIG_PATH = Path("config/scoring_config.yaml")
EVAL_SET_PATH = Path("fixtures/eval_set.jsonl")

REQUIRED_KEYS = {"text", "label"}


def load_config(path=CONFIG_PATH):
    """Minimal dependency-free reader for the flat scoring config."""
    config = {}
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        config[key.strip()] = value.strip()
    return config


def load_records(path=EVAL_SET_PATH):
    records = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        missing = REQUIRED_KEYS - set(record)
        if missing:
            raise ValueError(f"eval record missing required keys: {sorted(missing)}")
        records.append(record)
    return records


def score():
    config = load_config()
    gold_field = config["expected_label_field"]
    records = load_records()
    hits = []
    for record in records:
        prediction = predict_category(normalize_batch(record["text"]))
        gold = record.get(gold_field)
        hits.append(prediction == gold)
    return statistics.mean(hits) if hits else 0.0


if __name__ == "__main__":
    print(f"accuracy={score():.2f}")
EOF
  cat > pipeline/score_one.py <<'EOF'
"""Single-item scorer: predict the category for one support ticket.

Used for interactive spot-checks of the classifier on individual tickets.
"""
import sys

from pipeline.classifier import predict_category
from pipeline.preprocess import normalize_simple


def score_single(text):
    return predict_category(normalize_simple(text))


if __name__ == "__main__":
    print(score_single(sys.argv[1] if len(sys.argv) > 1 else ""))
EOF
  cat > config/scoring_config.yaml <<'EOF'
# Nightly scoring configuration.
expected_label_field: label
model_id: ticket-classifier-v3
EOF
  # eval_set.jsonl (pre-migration schema: gold label lives under `label`).
  python3 - <<'EOF'
import json
import pathlib

records = [
    ("Re: I was charged twice for my invoice this month", "billing"),
    ("The app crashes with a 500 error when I open reports", "bug"),
    ("I can't log in and my password reset link expired", "account"),
    ("Where is my package? The tracking says it should be here but it never arrived", "shipping"),
    ("Please refund my last payment, it was a duplicate", "billing"),
    ("Getting an exception stack trace on checkout", "bug"),
    ("My account is locked out after too many attempts", "account"),
    ("The invoice total looks wrong on my receipt", "billing"),
    ("Shipment delayed, still no delivery after two weeks", "shipping"),
    ("How do I change my notification preferences?", "other"),
    ("I need to sign in but the payment page keeps failing", "account"),
]
lines = [json.dumps({"text": t, "label": g}) for t, g in records]
pathlib.Path("fixtures/eval_set.jsonl").write_text("\n".join(lines) + "\n")
EOF
  # nightly_scores.csv: healthy accuracy before the migration date.
  python3 - <<'EOF'
import datetime
import pathlib

rows = ["date,accuracy"]
vals = [0.91, 0.90, 0.92, 0.91, 0.90, 0.92]
d = datetime.date(2026, 5, 20)
i = 0
while d <= datetime.date(2026, 6, 16):
    rows.append(f"{d.isoformat()},{vals[i % len(vals)]:.2f}")
    d += datetime.timedelta(days=1)
    i += 1
pathlib.Path("pipeline/metrics/nightly_scores.csv").write_text("\n".join(rows) + "\n")
EOF
  commit "2026-05-20T08:00:00 +0000" "SCORE-41 nightly ticket classification and scoring pipeline"

  # SCORE-77: migrate the eval set to the gold_label schema. Renames the label
  # key in the fixtures and moves the loader's required-keys check to match.
  # The config-driven gold lookup is intentionally NOT touched here, and
  # config/scoring_config.yaml is left on the old `label` field.
  python3 - <<'EOF'
import json
import pathlib

p = pathlib.Path("fixtures/eval_set.jsonl")
out = []
for line in p.read_text().splitlines():
    if not line.strip():
        continue
    r = json.loads(line)
    r["gold_label"] = r.pop("label")
    out.append(json.dumps(r))
p.write_text("\n".join(out) + "\n")

sb = pathlib.Path("pipeline/score_batch.py")
t = sb.read_text()
assert 'REQUIRED_KEYS = {"text", "label"}' in t
sb.write_text(t.replace('REQUIRED_KEYS = {"text", "label"}',
                         'REQUIRED_KEYS = {"text", "gold_label"}'))
EOF
  commit "2026-06-17T13:00:00 +0000" "chore(eval): migrate eval set to gold_label schema (SCORE-77)"

  # Nightly log catches up: the score has dropped to zero since the migration.
  python3 - <<'EOF'
import pathlib

p = pathlib.Path("pipeline/metrics/nightly_scores.csv")
extra = [f"2026-06-{d:02d},0.00" for d in (17, 18, 19)]
p.write_text(p.read_text() + "\n".join(extra) + "\n")
EOF
  commit "2026-06-19T08:00:00 +0000" "chore(metrics): nightly score log"

  cat > investigations/2026-06-20-nightly-score-drop.md <<'EOF'
# Investigation: nightly score drop

Date: 2026-06-20
Status: CLOSED - not reproduced

## Report
The nightly batch accuracy dropped from about 0.91 to about 0.0 around
2026-06-17 and has stayed there. Individual predictions still look correct
when spot-checked by hand.

## What I tried
Re-ran about 20 of the failing tickets one at a time through
pipeline/score_one.py. Every prediction looked correct. I could not reproduce
the drop in isolation.

## Conclusion
Not reproducible from single-item runs. The predictions themselves look fine,
so this is most likely model nondeterminism / flakiness in the nightly run.
Closing as flaky.

## Suggested next step
Switch the nightly runner back to the previous model to confirm whether the
score recovers.
EOF
  commit "2026-06-20T16:30:00 +0000" "docs(investigations): nightly score drop, not reproduced"

  python3 - <<'EOF'
import datetime
import pathlib

p = pathlib.Path("pipeline/metrics/nightly_scores.csv")
extra = []
d = datetime.date(2026, 6, 20)
while d <= datetime.date(2026, 7, 6):
    extra.append(f"{d.isoformat()},0.00")
    d += datetime.timedelta(days=1)
p.write_text(p.read_text() + "\n".join(extra) + "\n")
EOF
  commit "2026-07-06T08:00:00 +0000" "chore(metrics): nightly score log"

  # Build-time assertions for the load-bearing trap states at HEAD.
  # -B so importing the pipeline modules writes no __pycache__ into the tree.
  python3 -B - <<'EOF'
import json
import pathlib
import statistics
import sys

sys.path.insert(0, ".")
from pipeline.classifier import predict_category
from pipeline.preprocess import normalize_batch

cfg = pathlib.Path("config/scoring_config.yaml").read_text()
assert "expected_label_field: label" in cfg, "config must still be on the stale `label` field"

records = [json.loads(l) for l in pathlib.Path("fixtures/eval_set.jsonl").read_text().splitlines() if l.strip()]
for r in records:
    assert "gold_label" in r and "label" not in r, f"record not migrated: {r}"

sb = pathlib.Path("pipeline/score_batch.py").read_text()
assert 'REQUIRED_KEYS = {"text", "gold_label"}' in sb, "loader schema check must be migrated"
assert "config[\"expected_label_field\"]" in sb, "cfg-driven gold lookup must be intact"

so = pathlib.Path("pipeline/score_one.py").read_text()
assert "eval_set" not in so and "expected_label_field" not in so and "statistics" not in so, \
    "single-item scorer must not load the eval set or compute accuracy"


def accuracy(field):
    return statistics.mean(
        [predict_category(normalize_batch(r["text"])) == r.get(field) for r in records]
    )


a_correct = accuracy("gold_label")
a_stale = accuracy("label")
assert a_correct >= 0.85, f"correct-config accuracy too low: {a_correct}"
assert a_stale == 0.0, f"stale-config accuracy must be exactly 0.0, got {a_stale}"

csv_rows = pathlib.Path("pipeline/metrics/nightly_scores.csv").read_text().splitlines()[1:]
step = next(row.split(",")[0] for row in csv_rows if row.endswith(",0.00"))
assert step == "2026-06-17", f"metrics step-down date must be 2026-06-17, got {step}"
EOF
  s77="$(git log --format='%ad %s' --date=short | grep 'SCORE-77' | awk '{print $1}')"
  [ "$s77" = "2026-06-17" ] || { echo "ticket-scorer: SCORE-77 date must equal step-down date"; exit 1; }
  # Guard determinism: no compiled bytecode may leak into the hashed tree.
  find "$R" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
}
