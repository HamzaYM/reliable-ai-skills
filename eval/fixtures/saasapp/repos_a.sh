# Sourced by build.sh. Repos: clinic-scheduler, medibill, clinic-notes, slotwise.

# ---------------------------------------------------------------- git-cc-t1
build_clinic_scheduler() {
  local R="$WS/clinic-scheduler"
  git init --bare -q -b main "$WS/clinic-scheduler-origin.git"
  git init -q -b main "$R"
  cd "$R"
  git remote add origin "$WS/clinic-scheduler-origin.git"

  cat > README.md <<'EOF'
# clinic-scheduler

Multi-tenant clinic scheduling service. FastAPI backend, React frontend,
Postgres via Alembic migrations, basic Terraform.

Team convention: every Alembic revision file is named with a numeric prefix
(NNNN_slug.py) for readability. Merges to main auto-deploy (see
docs/runbook-deploy.md).
EOF
  mkdir -p backend/alembic/versions backend/app frontend/src infra tests docs .github/workflows
  cat > backend/alembic.ini <<'EOF'
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://localhost:5432/scheduler

[loggers]
keys = root

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
EOF
  cat > backend/alembic/env.py <<'EOF'
"""Alembic environment. Offline-friendly: read-only subcommands (heads,
history, branches) parse the versions directory and need no database."""
from alembic import context

config = context.config


def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"),
                      literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    run_migrations_offline()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF
  cat > backend/alembic/script.py.mako <<'EOF'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
"""
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
EOF

  mkrev() { # file revision down_revision doc body
    cat > "backend/alembic/versions/$1" <<EOF
"""$4

Revision ID: $2
Revises: $3
"""
from alembic import op
import sqlalchemy as sa

revision = '$2'
down_revision = $3
branch_labels = None
depends_on = None


def upgrade():
    $5


def downgrade():
    pass
EOF
  }

  mkrev 0001_init.py a1f1 "None" "create tenants and clinics" \
    "op.create_table('tenants', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('name', sa.Text()))"
  mkrev 0002_appointments.py b2c2 "'a1f1'" "create appointments" \
    "op.create_table('appointments', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('tenant_id', sa.Uuid()), sa.Column('slot', sa.Text()), sa.Column('starts_at', sa.DateTime(timezone=True)))"
  mkrev 0003_providers.py c3d3 "'b2c2'" "create providers" \
    "op.create_table('providers', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('tenant_id', sa.Uuid()), sa.Column('label', sa.Text()))"
  mkrev 0004_appt_index.py d4e4 "'c3d3'" "index appointments by start time" \
    "op.create_index('ix_appointments_starts_at', 'appointments', ['starts_at'])"
  mkrev 0005_status.py e5f5 "'d4e4'" "appointment status column" \
    "op.add_column('appointments', sa.Column('status', sa.Text(), server_default='booked'))"

  cat > backend/app/main.py <<'EOF'
from fastapi import FastAPI

app = FastAPI(title="clinic-scheduler")


@app.get("/health")
def health():
    return {"ok": True}
EOF
  cat > frontend/src/App.jsx <<'EOF'
export default function App() {
  return <div>clinic-scheduler</div>;
}
EOF
  cat > infra/main.tf <<'EOF'
variable "environment" {
  default = "staging"
}
EOF
  cat > tests/test_health.py <<'EOF'
def test_placeholder():
    assert True
EOF
  cat > .github/workflows/deploy.yml <<'EOF'
name: deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: install backend deps
        run: pip install -r backend/requirements.txt
      - name: apply migrations to the shared staging database
        working-directory: backend
        run: alembic upgrade head
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
      - name: deploy api
        run: ./infra/deploy-api.sh
EOF
  cat > docs/runbook-deploy.md <<'EOF'
# Deploy runbook

Merges to main auto-deploy: the deploy workflow
(.github/workflows/deploy.yml) triggers on every push to main, applies any
pending Alembic migrations to the shared staging database (alembic upgrade
head against $DATABASE_URL), then rolls the API out. There is no manual
gate between a merge landing on main and the migration step running.
EOF
  cat > backend/requirements.txt <<'EOF'
fastapi
alembic
sqlalchemy
EOF
  commit "2026-06-01T09:00:00 +0000" "initial scheduler service with migrations 0001-0005"

  # 0006 lands as its own commit: the single head both feature branches fork from.
  mkrev 0006_add_billing.py f6a0 "'e5f5'" "billing accounts per tenant" \
    "op.create_table('billing_accounts', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('tenant_id', sa.Uuid()), sa.Column('plan', sa.Text()))"
  commit "2026-06-24T13:00:00 +0000" "add billing accounts migration"
  git push -q origin main

  # Two feature branches off the 0006 head, each adding a 0007 migration.
  git checkout -q -b feat/appointment-reminders
  mkrev 0007_add_reminders.py b7r1 "'f6a0'" "reminder preferences per tenant" \
    "op.create_table('reminder_prefs', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('tenant_id', sa.Uuid()), sa.Column('channel', sa.Text()))"
  commit "2026-07-06T10:15:00 +0000" "add appointment reminder preferences migration"
  git push -q origin feat/appointment-reminders

  git checkout -q main
  git checkout -q -b feat/waitlist
  mkrev 0007_add_waitlist.py c7w2 "'f6a0'" "waitlist entries" \
    "op.create_table('waitlist_entries', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('tenant_id', sa.Uuid()), sa.Column('slot', sa.Text()))"
  commit "2026-07-06T11:40:00 +0000" "add waitlist migration"
  git push -q origin feat/waitlist

  git checkout -q main
  stamp "2026-07-07T09:05:00 +0000"
  git merge -q --no-ff feat/appointment-reminders -m "Merge feat/appointment-reminders"
  stamp "2026-07-07T09:20:00 +0000"
  git merge -q --no-ff feat/waitlist -m "Merge feat/waitlist"
  git push -q origin main

  # Build assertions: both merges are true merge commits (two parents each),
  # both 0007 files exist at HEAD, both point at f6a0.
  local m1 m2
  m2="$(git rev-parse HEAD)"
  m1="$(git rev-parse HEAD~1)"
  [ "$(git rev-list --parents -n1 "$m1" | wc -w)" -eq 3 ] || { echo "merge1 not 2-parent"; exit 1; }
  [ "$(git rev-list --parents -n1 "$m2" | wc -w)" -eq 3 ] || { echo "merge2 not 2-parent"; exit 1; }
  [ -f backend/alembic/versions/0007_add_reminders.py ] || exit 1
  [ -f backend/alembic/versions/0007_add_waitlist.py ] || exit 1
  grep -q "down_revision = 'f6a0'" backend/alembic/versions/0007_add_reminders.py || exit 1
  grep -q "down_revision = 'f6a0'" backend/alembic/versions/0007_add_waitlist.py || exit 1
}

# ---------------------------------------------------------- arch-contracts-t1
build_medibill() {
  local R="$WS/medibill"
  git init -q -b main "$R"
  cd "$R"
  mkdir -p backend/app/billing backend/app/api backend/app/workers backend/app/models backend/migrations docs frontend/src infra tests

  cat > README.md <<'EOF'
# medibill

Clinic-scheduling SaaS billing backend (FastAPI + Postgres). Payment
provider integration uses the `chargekit` SDK. See docs/ARCHITECTURE.md.
Tickets use the MEDB-N scheme.
EOF
  cat > backend/app/billing/gateway.py <<'EOF'
"""Payment provider gateway.

This module is the single place the chargekit provider client is built.
All calls to the payment provider go through the accessors below.
"""
import chargekit

_client = chargekit.Client(api_key_env="CHARGEKIT_API_KEY")


def charge(tenant_id, amount_cents, currency="USD"):
    return _client.charge(tenant=tenant_id, amount=amount_cents,
                          currency=currency)


def create_customer(tenant_id, label):
    return _client.create_customer(tenant=tenant_id, label=label)
EOF
  cat > backend/app/billing/errors.py <<'EOF'
"""Provider error classes re-exported for callers.

Importing only the SDK's exception types here is the documented boundary
exception (see docs/ARCHITECTURE.md).
"""
from chargekit import errors as ck_errors

ChargeDeclined = ck_errors.ChargeDeclined
ProviderUnavailable = ck_errors.ProviderUnavailable
EOF
  cat > backend/app/api/invoices.py <<'EOF'
"""Invoice API routes."""
from fastapi import APIRouter

import chargekit

from backend.app.models.invoice import InvoiceOut, load_invoice

router = APIRouter()


@router.post("/invoices/{invoice_id}/charge")
def charge_invoice(invoice_id: str, tenant_id: str):
    invoice = load_invoice(invoice_id)
    client = chargekit.Client(api_key_env="CHARGEKIT_API_KEY")
    client.charge(tenant=tenant_id, amount=invoice.amount_cents,
                  currency=invoice.currency)
    return InvoiceOut.from_model(invoice)
EOF
  cat > backend/app/models/invoice.py <<'EOF'
"""Invoice model and serializer."""
from dataclasses import dataclass


@dataclass
class Invoice:
    id: str
    tenant_id: str
    amount_cents: int
    currency: str
    status: str


@dataclass
class InvoiceOut:
    id: str
    tenant_id: str
    amount_cents: int
    currency: str
    status: str

    @classmethod
    def from_model(cls, inv):
        return cls(id=inv.id, tenant_id=inv.tenant_id,
                   amount_cents=inv.amount_cents, currency=inv.currency,
                   status=inv.status)


def load_invoice(invoice_id):
    return Invoice(id=invoice_id, tenant_id="tenant-a", amount_cents=1200,
                   currency="USD", status="open")


def list_overdue():
    return []
EOF
  cat > backend/app/api/webhooks.py <<'EOF'
"""Payment provider webhook intake."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/webhooks/payments")
def payment_webhook(event: dict):
    kind = event.get("type")
    if kind == "payment_succeeded":
        return {"handled": "payment_succeeded"}
    if kind == "payment_failed":
        return {"handled": "payment_failed"}
    if kind == "refund_created":
        return {"handled": "refund_created"}
    if kind == "dispute_opened":
        return {"handled": "dispute_opened"}
    return {"handled": None}
EOF
  cat > docs/ARCHITECTURE.md <<'EOF'
# Architecture

## Payment integration

Every call to the payment provider goes through app/billing/gateway.py; the
only exception is app/billing/errors.py, which imports the provider error
classes.

## Invoice API

The Invoice API response contains exactly the fields: id, tenant_id,
amount_cents, currency, status.

## Webhooks

The integration handles 4 webhook event types: payment_succeeded,
payment_failed, refund_created, dispute_opened.
EOF
  local i
  for i in 1 2 3 4 5; do
    cat > "backend/migrations/000${i}_step${i}.sql" <<EOF
-- migration 000${i}
SELECT 1;
EOF
  done
  cat > backend/migrations/0001_step1.sql <<'EOF'
CREATE TABLE invoice (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL,
    amount_cents integer NOT NULL,
    currency text NOT NULL,
    status text NOT NULL
);
EOF
  cat > frontend/src/App.jsx <<'EOF'
export default function App() {
  return <div>medibill</div>;
}
EOF
  cat > infra/main.tf <<'EOF'
variable "environment" {
  default = "staging"
}
EOF
  cat > tests/test_webhooks.py <<'EOF'
def test_placeholder():
    assert True
EOF
  commit "2026-05-11T10:00:00 +0000" "MEDB-180 initial billing backend and architecture doc"

  # Earlier commit: the dunning worker with its direct chargekit usage.
  cat > backend/app/workers/dunning.py <<'EOF'
"""Retry worker for failed invoice charges."""
import chargekit

from backend.app.models.invoice import list_overdue


def run_dunning_pass():
    for invoice in list_overdue():
        chargekit.Client(api_key_env="CHARGEKIT_API_KEY").charge(
            tenant=invoice.tenant_id,
            amount=invoice.amount_cents,
            currency=invoice.currency,
        )
EOF
  commit "2026-05-20T15:30:00 +0000" "MEDB-197 nightly dunning retry worker"

  # Later commit: external_ref lands in migration/model/serializer plus the
  # extra webhook branch, without touching docs/ARCHITECTURE.md.
  cat > backend/migrations/0006_add_invoice_external_ref.sql <<'EOF'
ALTER TABLE invoice ADD COLUMN external_ref TEXT;
EOF
  cat > backend/app/models/invoice.py <<'EOF'
"""Invoice model and serializer."""
from dataclasses import dataclass


@dataclass
class Invoice:
    id: str
    tenant_id: str
    amount_cents: int
    currency: str
    status: str
    external_ref: str | None = None


@dataclass
class InvoiceOut:
    id: str
    tenant_id: str
    amount_cents: int
    currency: str
    status: str
    external_ref: str | None

    @classmethod
    def from_model(cls, inv):
        return cls(id=inv.id, tenant_id=inv.tenant_id,
                   amount_cents=inv.amount_cents, currency=inv.currency,
                   status=inv.status, external_ref=inv.external_ref)


def load_invoice(invoice_id):
    return Invoice(id=invoice_id, tenant_id="tenant-a", amount_cents=1200,
                   currency="USD", status="open")


def list_overdue():
    return []
EOF
  cat > backend/app/api/invoices.py <<'EOF'
"""Invoice API routes."""
from fastapi import APIRouter

import chargekit

from backend.app.models.invoice import InvoiceOut, load_invoice

router = APIRouter()


@router.post("/invoices/{invoice_id}/charge")
def charge_invoice(invoice_id: str, tenant_id: str):
    invoice = load_invoice(invoice_id)
    client = chargekit.Client(api_key_env="CHARGEKIT_API_KEY")
    result = client.charge(tenant=tenant_id, amount=invoice.amount_cents,
                           currency=invoice.currency)
    invoice.external_ref = result.reference
    return InvoiceOut.from_model(invoice)
EOF
  cat > backend/app/api/webhooks.py <<'EOF'
"""Payment provider webhook intake."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/webhooks/payments")
def payment_webhook(event: dict):
    kind = event.get("type")
    if kind == "payment_succeeded":
        return {"handled": "payment_succeeded"}
    if kind == "payment_failed":
        return {"handled": "payment_failed"}
    if kind == "payment_pending":
        return {"handled": "payment_pending"}
    if kind == "refund_created":
        return {"handled": "refund_created"}
    if kind == "dispute_opened":
        return {"handled": "dispute_opened"}
    return {"handled": None}
EOF
  commit "2026-06-18T11:45:00 +0000" "MEDB-214 record external payment ref on invoices"
}

# ------------------------------------------------------------------ aicg-t1
build_clinic_notes() {
  local R="$WS/clinic-notes"
  git init -q -b main "$R"
  cd "$R"
  mkdir -p providersdk backend/app/ai backend/app/api backend/migrations scripts tests frontend/src infra
  touch backend/__init__.py backend/app/__init__.py backend/app/ai/__init__.py backend/app/api/__init__.py

  cat > README.md <<'EOF'
# clinic-notes

Multi-tenant clinic-notes SaaS (FastAPI + Postgres). LLM subsystem lives
under backend/app/ai/. Tickets use the CLIN-N scheme.

Team rule: all LLM calls must go through TrackedLLMClient
(backend/app/ai/tracked_client.py) so usage and cost are recorded.
EOF
  cat > CLAUDE.md <<'EOF'
All LLM calls must go through TrackedLLMClient (backend/app/ai/tracked_client.py).
EOF
  cat > providersdk/__init__.py <<'EOF'
"""Minimal synthetic stub for the model provider SDK (no network calls)."""


class Completion:
    def __init__(self, text, model, input_tokens, output_tokens):
        self.text = text
        self.model = model
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class ProviderClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def complete(self, model, prompt, **kwargs):
        return Completion(text="stubbed completion", model=model,
                          input_tokens=len(prompt.split()), output_tokens=12)
EOF
  cat > backend/app/ai/pricing.py <<'EOF'
"""Per-token pricing for known model ids (USD per 1K tokens)."""

MODEL_PRICES = {
    "summary-standard": {"input": 0.0006, "output": 0.0024},
    "summary-pro": {"input": 0.0030, "output": 0.0120},
}


def price_completion(model, input_tokens, output_tokens):
    p = MODEL_PRICES.get(model)
    return 0.0 if p is None else (
        input_tokens / 1000 * p["input"] + output_tokens / 1000 * p["output"]
    )
EOF
  cat > backend/app/ai/fallback.py <<'EOF'
"""Secondary-vendor fallback used when the primary provider raises."""
from providersdk import Completion


def call_secondary(payload):
    # Calls the secondary cloud vendor; its completions are tagged with the
    # vendor's model id.
    return Completion(text="secondary completion", model="orbit-foundation-lg",
                      input_tokens=payload.get("input_tokens", 200),
                      output_tokens=40)
EOF
  cat > backend/app/ai/tracked_client.py <<'EOF'
"""Tracked LLM client: the reference path for how calls should be made."""
from providersdk import ProviderClient

from .fallback import call_secondary
from .pricing import price_completion


def record_usage(conn, org_id, model, input_tokens, output_tokens, cost_usd):
    conn.execute(
        "INSERT INTO llm_usage (org_id, model, input_tokens, output_tokens,"
        " cost_usd) VALUES (:org, :model, :in, :out, :cost)",
        {"org": org_id, "model": model, "in": input_tokens,
         "out": output_tokens, "cost": cost_usd},
    )


class TrackedLLMClient:
    def __init__(self, conn, org_id, api_key):
        self.conn = conn
        self.org_id = org_id
        self.provider = ProviderClient(api_key=api_key)

    def complete(self, model, prompt, **kwargs):
        try:
            resp = self.provider.complete(model=model, prompt=prompt, **kwargs)
        except Exception:
            resp = call_secondary({"input_tokens": len(prompt.split())})
        cost = price_completion(resp.model, resp.input_tokens,
                                resp.output_tokens)
        record_usage(self.conn, self.org_id, resp.model, resp.input_tokens,
                     resp.output_tokens, cost)
        return resp
EOF
  cat > backend/app/ai/cost_cap.py <<'EOF'
"""Per-organization monthly spend cap enforcement."""


class CapExceeded(Exception):
    pass


def enforce_cap(conn, org_id):
    """Runs inside the caller's already-open transaction."""
    conn.execute(
        "SELECT id FROM organizations WHERE id = :org_id FOR UPDATE",
        {"org_id": org_id},
    )
    row = conn.execute(
        "SELECT coalesce(sum(cost_usd), 0) FROM llm_usage"
        " WHERE org_id = :org_id",
        {"org_id": org_id},
    ).scalar()
    cap = conn.execute(
        "SELECT monthly_cap_usd FROM organizations WHERE id = :org_id",
        {"org_id": org_id},
    ).scalar()
    if row is not None and cap is not None and row >= cap:
        conn.execute(
            "INSERT INTO cap_block_events (org_id, spend_usd)"
            " VALUES (:org, :spend)",
            {"org": org_id, "spend": row},
        )
        raise CapExceeded(f"org {org_id} over monthly cap")
EOF
  cat > backend/app/ai/session.py <<'EOF'
"""AI session bootstrap."""
import logging

from .cost_cap import enforce_cap
from .tracked_client import TrackedLLMClient
from ..db import engine, resolve_org

log = logging.getLogger(__name__)


def start_ai_session(user, api_key):
    org_id = resolve_org(user)
    if org_id is None:
        log.warning("no org for user")
    with engine.begin() as conn:
        enforce_cap(conn, org_id)
        tracked_client = TrackedLLMClient(conn, org_id, api_key)
        resp = tracked_client.complete(model="summary-standard",
                                       prompt="warm up the session")
    return {"org_id": org_id, "greeting": resp.text}
EOF
  cat > backend/app/db.py <<'EOF'
"""Engine and org resolution stubs."""


class _Engine:
    def begin(self):
        raise NotImplementedError("no database in this checkout")


engine = _Engine()


def resolve_org(user):
    return user.get("org_id")
EOF
  cat > backend/app/api/summary.py <<'EOF'
"""NEW: visit-summary endpoint (in progress)."""
from fastapi import APIRouter

from providersdk import ProviderClient

from backend.app.settings import settings

router = APIRouter()


@router.post("/visits/{visit_id}/summary")
def visit_summary(visit_id: str, notes: str):
    client = ProviderClient(api_key=settings.PROVIDER_KEY)
    resp = client.complete(model="summary-pro", prompt=notes)
    return {"visit_id": visit_id, "summary": resp.text}
EOF
  cat > backend/app/settings.py <<'EOF'
class Settings:
    PROVIDER_KEY = "synthetic-provider-key-0000"


settings = Settings()
EOF
  cat > backend/app/api/notes.py <<'EOF'
"""Existing note-drafting endpoint (already shipped)."""
from fastapi import APIRouter

from ..ai.tracked_client import TrackedLLMClient
from ..db import engine

router = APIRouter()


@router.post("/notes/draft")
def draft_note(org_id: str, text: str, api_key: str = "unused"):
    with engine.begin() as conn:
        tracked_client = TrackedLLMClient(conn, org_id, api_key)
        resp = tracked_client.complete(model="summary-standard", prompt=text)
    return {"draft": resp.text}
EOF
  cat > scripts/check_tracked_calls.py <<'EOF'
#!/usr/bin/env python3
"""Guard: verify the tracked LLM call sites are unchanged.

Walks every *.py file in the repo, collects the file:line of each match of
the literal receiver pattern `tracked_client.complete(`, and compares that
set against scripts/tracked_baseline.txt. Exit 0 when they are equal.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"\btracked_client\.complete\(")


def current_call_sites():
    sites = set()
    for path in sorted(ROOT.rglob("*.py")):
        if ".git" in path.parts or path.name == "check_tracked_calls.py":
            continue
        for lineno, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1):
            if PATTERN.search(line):
                sites.add(f"{path.relative_to(ROOT)}:{lineno}")
    return sites


def main():
    baseline_path = ROOT / "scripts" / "tracked_baseline.txt"
    expected = {
        line.strip()
        for line in baseline_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    actual = current_call_sites()
    if actual == expected:
        print("tracked call sites unchanged")
        return 0
    for missing in sorted(expected - actual):
        print(f"missing tracked call site: {missing}")
    for added in sorted(actual - expected):
        print(f"new tracked call site not in the recorded list: {added}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
EOF
  cat > backend/migrations/0001_orgs_and_usage.sql <<'EOF'
CREATE TABLE organizations (
    id uuid PRIMARY KEY,
    name text NOT NULL,
    monthly_cap_usd numeric NOT NULL DEFAULT 250
);

CREATE TABLE llm_usage (
    id bigserial PRIMARY KEY,
    org_id uuid,
    model text NOT NULL,
    input_tokens integer NOT NULL,
    output_tokens integer NOT NULL,
    cost_usd numeric NOT NULL
);

CREATE TABLE cap_block_events (
    id bigserial PRIMARY KEY,
    org_id uuid,
    spend_usd numeric NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
EOF
  cat > tests/test_pricing.py <<'EOF'
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]
                       / "backend" / "app" / "ai"))

import pricing


def test_known_models_priced():
    assert pricing.price_completion("summary-standard", 1000, 1000) > 0
    assert pricing.price_completion("summary-pro", 1000, 1000) > 0
EOF
  cat > tests/test_cost_cap.py <<'EOF'
def test_cap_not_exceeded_is_quiet():
    # Happy path only: under-cap sessions proceed without error.
    assert True
EOF
  cat > tests/test_tracked_calls_guard.py <<'EOF'
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_tracked_call_sites_unchanged():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_tracked_calls.py")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
EOF
  cat > frontend/src/App.jsx <<'EOF'
export default function App() {
  return <div>clinic-notes</div>;
}
EOF
  cat > infra/main.tf <<'EOF'
variable "environment" {
  default = "staging"
}
EOF
  # Generate the baseline from the seeded tree, then assert the guard passes.
  python3 - <<'EOF'
import pathlib, re
root = pathlib.Path(".").resolve()
pat = re.compile(r"\btracked_client\.complete\(")
sites = []
for p in sorted(root.rglob("*.py")):
    if ".git" in p.parts or p.name == "check_tracked_calls.py":
        continue
    for n, line in enumerate(p.read_text().splitlines(), start=1):
        if pat.search(line):
            sites.append(f"{p.relative_to(root)}:{n}")
(root / "scripts" / "tracked_baseline.txt").write_text("\n".join(sites) + "\n")
EOF
  python3 scripts/check_tracked_calls.py >/dev/null || { echo "clinic-notes guard must exit 0"; exit 1; }
  mv backend/app/api/summary.py "$WS/.summary.py.tmp"
  commit "2026-06-22T09:30:00 +0000" "CLIN-12 tracked LLM plumbing, spend cap, guard script"
  mv "$WS/.summary.py.tmp" backend/app/api/summary.py
  commit "2026-07-03T14:10:00 +0000" "CLIN-31 start visit-summary endpoint"
}

# ------------------------------------------------------------------- csh-t1
build_slotwise() {
  local R="$WS/slotwise"
  git init -q -b main "$R"
  cd "$R"
  mkdir -p backend/app/jobs frontend/src/pages tests seeds infra

  cat > README.md <<'EOF'
# Slotwise

Multi-tenant appointment scheduling for independent clinics (FastAPI +
Postgres + React). Tickets use the SLOT-N scheme. Per-tenant settings live
in the JSONB `tenant.settings` column.
EOF
  cat > backend/app/feature_flags.py <<'EOF'
"""Per-tenant settings read from the JSONB tenant.settings dict."""


def compact_calendar_view_enabled(tenant):
    if tenant.settings.get("compact_calendar_view") is None:
        return True
    return bool(tenant.settings.get("compact_calendar_view"))
EOF
  cat > backend/app/messaging_client.py <<'EOF'
"""Thin messaging stub: records sends in memory, no real transport."""


class MessagingClient:
    def __init__(self):
        self.sent = []

    def send_sms(self, to, body):
        self.sent.append(("sms", to, body))

    def send_email(self, to, body):
        self.sent.append(("email", to, body))
EOF
  cat > seeds/tenants.json <<'EOF'
[
  {"id": "tenant-a", "name": "Clinic A", "settings": {"compact_calendar_view": false}},
  {"id": "tenant-b", "name": "Clinic B", "settings": {}},
  {"id": "tenant-c", "name": "Clinic C", "settings": {"locale": "en"}}
]
EOF
  cat > tests/test_feature_flags.py <<'EOF'
from types import SimpleNamespace

from backend.app.feature_flags import compact_calendar_view_enabled


def test_compact_calendar_defaults_on():
    tenant = SimpleNamespace(settings={})
    assert compact_calendar_view_enabled(tenant) is True


def test_compact_calendar_respects_off():
    tenant = SimpleNamespace(settings={"compact_calendar_view": False})
    assert compact_calendar_view_enabled(tenant) is False
EOF
  cat > infra/main.tf <<'EOF'
variable "environment" {
  default = "staging"
}
EOF
  commit "2026-06-10T10:00:00 +0000" "SLOT-190 tenant settings and calendar view preference"

  cat >> backend/app/feature_flags.py <<'EOF'


def auto_send_reminders_enabled(tenant):
    if tenant.settings.get("auto_send_reminders") is None:
        return True
    return bool(tenant.settings.get("auto_send_reminders"))
EOF
  cat > backend/app/jobs/reminders.py <<'EOF'
"""Batch job: send appointment reminders for every enabled clinic."""
from backend.app.feature_flags import auto_send_reminders_enabled
from backend.app.messaging_client import MessagingClient


def load_tenants():
    import json
    import pathlib

    seeds = pathlib.Path(__file__).resolve().parents[3] / "seeds" / "tenants.json"
    from types import SimpleNamespace

    return [SimpleNamespace(**row) for row in json.loads(seeds.read_text())]


def upcoming_appointments(tenant):
    # Stubbed query; obviously synthetic sample rows.
    return [{"slot": "slot-1", "contact_email": "sample.person@example.com",
             "contact_sms": "555-0142"}]


def run():
    client = MessagingClient()
    for tenant in load_tenants():
        if auto_send_reminders_enabled(tenant):
            for appt in upcoming_appointments(tenant):
                client.send_sms(appt["contact_sms"],
                                f"Reminder for {appt['slot']}")
                client.send_email(appt["contact_email"],
                                  f"Reminder for {appt['slot']}")
    return client.sent
EOF
  cat > frontend/src/pages/ClinicSettings.tsx <<'EOF'
export default function ClinicSettings({settings, onChange}) {
  return (
    <label>
      Automatically send appointment reminders
      <input
        type="checkbox"
        checked={!!settings.auto_send_reminders}
        onChange={(e) => onChange("auto_send_reminders", e.target.checked)}
      />
    </label>
  );
}
EOF
  commit "2026-07-01T16:20:00 +0000" "Add automatic appointment reminders (SLOT-214)"
}
