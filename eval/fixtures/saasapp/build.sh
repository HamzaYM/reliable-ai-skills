#!/usr/bin/env bash
# saasapp archetype fixture: a workspace of small, fully synthetic SaaS
# product repositories. Each task in the golden suite that declares
# fixture=saasapp targets exactly one repository in this workspace (see the
# task's repo:<dir> tag in eval/tasks/golden-suite.jsonl).
#
# Everything is invented: products, code, commit messages, ticket schemes
# (CLIN/SLOT/METRIC/CED/PLAT/ROTA/REL/MEDB, declared in manifest.json).
# Determinism: every commit pins author/committer identity and dates, so all
# SHAs are identical on every machine. Generated PNGs are written by a pure
# stdlib bitmap renderer (no fonts, no PIL) so they are byte-stable.
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

This workspace contains several unrelated internal project repositories:

- clinic-scheduler/   multi-tenant clinic scheduling service (Alembic migrations)
- medibill/           clinic scheduling SaaS billing/payments backend
- clinic-notes/       multi-tenant clinic-notes SaaS with an AI visit-summary subsystem
- slotwise/           Slotwise, appointment scheduling for independent clinics
- metricsboard/       MetricsBoard, a multi-tenant analytics dashboard
- clinic-comms/       clinic appointment-scheduling backend (patient messaging)
- clinic-portal/      clinic scheduling web app plus its release-notes drafts
- cedarline/          Cedarline, clinic scheduling backend (local-dev tooling)
- carelog-api/        FastAPI backend deployed as a container on Cargobox
- meadowdesk/         meadowdesk, a multi-tenant desk-booking SaaS
- juniper/            juniper, a multi-tenant clinic scheduling app
- rosterly/           multi-tenant clinic scheduling backend (search PR under review)
- deskly/             coworking-space desk-booking SaaS
- medislot/           MediSlot, clinic scheduling SaaS (staging + prod infra)
- clinicbook/         multi-tenant clinic booking backend (patient exports)

Each directory is its own git repository.
EOF

source "$HERE/repos_a.sh"   # clinic-scheduler medibill clinic-notes slotwise
source "$HERE/repos_b.sh"   # metricsboard clinic-comms clinic-portal cedarline
source "$HERE/repos_c.sh"   # carelog-api meadowdesk juniper
source "$HERE/repos_d.sh"   # rosterly deskly medislot
source "$HERE/repos_e.sh"   # clinicbook

build_clinic_scheduler
build_medibill
build_clinic_notes
build_slotwise
build_metricsboard
build_clinic_comms
build_clinic_portal
build_cedarline
build_carelog_api
build_meadowdesk
build_juniper
build_rosterly
build_deskly
build_medislot
build_clinicbook

# Remove git auto-generated sample hooks (they contain third-party URLs).
find "$WS" -name "*.sample" -path "*hooks*" -delete

echo "built saasapp fixture at $WS"
