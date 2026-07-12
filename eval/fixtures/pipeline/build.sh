#!/usr/bin/env bash
# pipeline archetype fixture: a workspace of small, fully synthetic batch /
# LLM-pipeline repositories. Each task with fixture=pipeline targets exactly
# one repository here (see the task's repo:<dir> tag in golden-suite.jsonl).
#
# Everything is invented: products, code, vendors, ticket schemes
# (SCORE/TG/EVAL/DATA/ML/PEG, declared in manifest.json). Determinism: every
# commit pins author/committer identity and dates.
set -euo pipefail

WS="$1"
mkdir -p "$WS"
WS="$(cd "$WS" && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export GIT_AUTHOR_NAME="Fixture Bot"
export GIT_AUTHOR_EMAIL="fixture@example.com"
export GIT_COMMITTER_NAME="Fixture Bot"
export GIT_COMMITTER_EMAIL="fixture@example.com"
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_NOSYSTEM=1

stamp() {
  export GIT_AUTHOR_DATE="$1"
  export GIT_COMMITTER_DATE="$1"
}

commit() { # commit "<date>" "<message>"
  git add -A
  stamp "$1"
  git commit -q -m "$2"
}

cat > "$WS/README.md" <<'EOF'
# Workspace

This workspace contains several unrelated internal pipeline repositories:

- intake-scoring/          batch LLM scoring of applicant intake documents
- quality-rubric/          LLM response-quality scoring pipeline (rubric based)
- transcript-scoring/      nightly transcript-quality scoring pipeline
- prompt-eval-grid/        nightly adversarial prompt-evaluation grid
- patient-events/          patient-event analytics batch jobs
- tallgrass/               Tallgrass document-scoring data pipeline
- batch-grader/            batch grading of saved model outputs
- answer-scoring-pipeline/ LLM answer-scoring pipeline (PR in flight)
- reply-grader/            grades customer-support agent replies on three axes
- outputs-review/          offline scoring pipeline with a findings backlog
- scorelab/                scoring pipeline with golden-file tests
- scoreforge/              ScoreForge batch document-scoring service
- risk-scorer/             transaction-risk scorer (v1 and proposed v2)
- ticket-scorer/           nightly ticket-classification scoring pipeline

Each directory is its own git repository.
EOF

source "$HERE/repos_a.sh"   # intake-scoring quality-rubric transcript-scoring prompt-eval-grid
source "$HERE/repos_b.sh"   # patient-events tallgrass batch-grader answer-scoring-pipeline
source "$HERE/repos_c.sh"   # reply-grader outputs-review scorelab scoreforge risk-scorer
source "$HERE/repos_d.sh"   # ticket-scorer

build_intake_scoring
build_quality_rubric
build_transcript_scoring
build_prompt_eval_grid
build_patient_events
build_tallgrass
build_batch_grader
build_answer_scoring_pipeline
build_reply_grader
build_outputs_review
build_scorelab
build_scoreforge
build_risk_scorer
build_ticket_scorer

# Remove git auto-generated sample hooks (they contain third-party URLs).
find "$WS" -name "*.sample" -path "*hooks*" -delete

echo "built pipeline fixture at $WS"
