# Sourced by build.sh. Repos: carelog-api, meadowdesk, juniper.

# ----------------------------------------------------------------- farch-t1
build_carelog_api() {
  local R="$WS/carelog-api"
  git init -q -b main "$R"
  cd "$R"
  mkdir -p backend/app/routers deploy tests

  cat > README.md <<'EOF'
# carelog-api

FastAPI backend for clinic reporting dashboards. Runs as a container on
Cargobox (see deploy/cargobox.yaml). Tickets use the PLAT-N scheme.
EOF
  cat > backend/Dockerfile <<'EOF'
FROM python:3.12-slim
WORKDIR /srv
COPY . /srv
RUN pip install -r requirements.txt
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF
  cat > backend/requirements.txt <<'EOF'
fastapi
sqlalchemy
uvicorn
EOF
  cat > deploy/cargobox.yaml <<'EOF'
# Cargobox container deployment (always-on service)
service: carelog-api
image: registry.example.com/carelog-api:latest
replicas: 2
resources:
  cpu: "1"
  memory: 1Gi
env:
  - name: DATABASE_URL
    secretRef: carelog-db-url
EOF
  cat > backend/app/main.py <<'EOF'
"""carelog-api entrypoint.

The SQLAlchemy connection pool is created once at application startup and
shared by all request handlers for the life of the process.
"""
import os

from fastapi import FastAPI
from sqlalchemy import create_engine

engine = create_engine(os.environ.get("DATABASE_URL", "postgresql://localhost/carelog"),
                       pool_size=10, max_overflow=5)

app = FastAPI(title="carelog-api")

from backend.app.routers.reports import router as reports_router  # noqa: E402

app.include_router(reports_router)
EOF
  cat > backend/app/routers/reports.py <<'EOF'
"""Monthly reporting endpoint."""
from fastapi import APIRouter
from sqlalchemy import text

from backend.app.main import engine

router = APIRouter()

MONTHLY_SQL = """
SELECT t.name,
       count(a.id)              AS appointments,
       count(DISTINCT c.id)     AS clients,
       sum(i.amount_cents)      AS billed_cents
FROM tenants t
JOIN appointments a ON a.tenant_id = t.id
JOIN clients c      ON c.id = a.client_id
LEFT JOIN invoices i ON i.appointment_id = a.id
WHERE a.starts_at >= date_trunc('month', now())
GROUP BY t.name
ORDER BY t.name
"""


@router.get("/reports/monthly")
def monthly_report():
    with engine.connect() as conn:
        rows = conn.execute(text(MONTHLY_SQL))
        return [dict(r._mapping) for r in rows]
EOF
  cat > tests/test_reports.py <<'EOF'
def test_placeholder():
    assert True
EOF
  commit "2026-03-02T09:00:00 +0000" "PLAT-9 reporting API on Cargobox"

  # PLAT-31: serverless migration, attempted and rolled back.
  cat > deploy/edgerunner.toml <<'EOF'
# Edgerunner serverless deployment
[service]
name = "carelog-api"
entry = "backend/serverless_handler.py"

[scaling]
per_request = true
EOF
  cat > backend/serverless_handler.py <<'EOF'
"""Edgerunner entry shim: adapts the FastAPI app to per-request invocation."""
from backend.app.main import app


def handler(request):
    return app(request)
EOF
  commit "2026-04-14T10:00:00 +0000" "Add Edgerunner serverless deploy for API (PLAT-31)"

  cat > backend/serverless_handler.py <<'EOF'
"""Edgerunner entry shim.

Edgerunner runs each request in a fresh isolate and does not keep the
SQLAlchemy connection pool between invocations, so /reports/monthly must
acquire its own Postgres connection per call (stopgap).
"""
import os

from sqlalchemy import create_engine

from backend.app.main import app


def handler(request):
    request.state.engine = create_engine(os.environ["DATABASE_URL"],
                                         poolclass=None)
    return app(request)
EOF
  git add -A
  stamp "2026-04-16T09:30:00 +0000"
  git commit -q -m "Open a dedicated Postgres connection per request in the serverless handler (PLAT-31)" \
    -m "Edgerunner runs each request in a fresh isolate and does not keep the SQLAlchemy connection pool between invocations, so /reports/monthly must acquire its own Postgres connection per call. Stopgap until we settle pooling."

  git rm -q deploy/edgerunner.toml backend/serverless_handler.py
  stamp "2026-04-21T17:45:00 +0000"
  git commit -q -m "Revert Edgerunner migration: serverless isolates cannot hold the Postgres pool; /reports/monthly exhausted Postgres max_connections in production, back to Cargobox container deploy (PLAT-31)" \
    -m "Under normal dashboard load the per-request connections opened faster than Postgres could recycle them and tripped the connection limit ('FATAL: too many connections'), taking the endpoint down. Returning to the always-on Cargobox container with the shared pool."

  # Later unrelated commits so HEAD is well past the revert.
  cat > backend/requirements.txt <<'EOF'
fastapi
sqlalchemy>=2.0.30
uvicorn
EOF
  commit "2026-05-12T09:10:00 +0000" "bump sqlalchemy minimum version"
  cat >> tests/test_reports.py <<'EOF'


def test_report_shape():
    assert isinstance([], list)
EOF
  commit "2026-06-03T15:00:00 +0000" "tidy report tests"
}

# ------------------------------------------------------------------ mabc-t1
build_meadowdesk() {
  local R="$WS/meadowdesk"
  git init --bare -q -b main "$WS/meadowdesk-origin.git"
  git init -q -b main "$R"
  cd "$R"
  git remote add origin "$WS/meadowdesk-origin.git"
  mkdir -p backend/app/routers backend/app/services backend/migrations backend/tests frontend/src infra campaign

  cat > README.md <<'EOF'
# meadowdesk

Multi-tenant desk-booking SaaS (FastAPI backend, React frontend, Postgres,
basic Terraform). Review remediation findings are tracked in
REVIEW_BACKLOG.md; the campaign log is campaign/PROGRESS.log.
EOF
  # bookings.py with the availability-window logic INLINE at first.
  python3 - <<'EOF'
import pathlib

head = '''"""Booking routes."""
from fastapi import APIRouter

from backend.app.services import tenants

router = APIRouter()


@router.get("/bookings")
def list_bookings(tenant_id: str, page: int = 1):
    rows = tenants.bookings_for(tenant_id)
    return rows[(page - 1) * 50 : page * 50]
'''

filler = []
for i in range(1, 17):
    filler.append(f'''

@router.get("/bookings/report-{i}")
def booking_report_{i}(tenant_id: str):
    """Summary report variant {i} for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {{"variant": {i}, "total": total}}
''')

avail = '''
def availability_window(tenant, desk, day):
    """Availability-window logic: which hours a desk can be booked."""
    open_hour = tenant.settings.get("open_hour", 8)
    close_hour = tenant.settings.get("close_hour", 18)
    hours = []
    for h in range(open_hour, close_hour):
        if not desk.blocked(day, h):
            hours.append(h)
    return hours
'''

tail = '''

@router.post("/bookings")
def create_booking(tenant_id: str, desk_id: str, day: str, hour: int):
    return {"tenant_id": tenant_id, "desk_id": desk_id, "day": day,
            "hour": hour, "status": "created"}
'''
text = head + "".join(filler) + avail + tail
lines = text.splitlines()
# The availability-window block must span line 142 (REVIEW_BACKLOG cites
# backend/app/routers/bookings.py:142 before the refactor rots it).
assert "def availability_window" in lines[141], lines[139:144]
pathlib.Path("backend/app/routers/bookings.py").write_text(text)
EOF
  cat > backend/app/services/tenants.py <<'EOF'
"""Tenant data access."""


def bookings_for(tenant_id):
    return []
EOF
  cat > backend/app/routers/desks.py <<'EOF'
"""Desk routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/desks")
def list_desks(tenant_id: str):
    return []
EOF
  cat > backend/migrations/0001_init.sql <<'EOF'
CREATE TABLE tenants (id uuid PRIMARY KEY, subdomain text, name text);
CREATE TABLE desks (id uuid PRIMARY KEY, tenant_id uuid, label text);
CREATE TABLE bookings (
    id uuid PRIMARY KEY,
    tenant_id uuid,
    desk_id uuid,
    day date,
    hour integer,
    created_at timestamptz DEFAULT now()
);
EOF
  cat > backend/tests/test_bookings.py <<'EOF'
def test_placeholder():
    assert True
EOF
  cat > frontend/src/App.jsx <<'EOF'
export default function App() {
  return <div>meadowdesk</div>;
}
EOF
  cat > infra/main.tf <<'EOF'
resource "synthetic_security_group" "api" {
  name    = "meadowdesk-api"
  ingress = ["0.0.0.0/0"]  # F-10: over-permissive
}
EOF
  commit "2026-06-15T09:00:00 +0000" "baseline desk-booking app"
  git push -q origin main

  # Refactor on main: move availability-window logic into a service module,
  # rotting the F-03 citation at backend/app/routers/bookings.py:142.
  python3 - <<'EOF'
import pathlib
p = pathlib.Path("backend/app/routers/bookings.py")
t = p.read_text()
start = t.index("\n\ndef availability_window")
marker = "@router.post"
end = t.index("\n\n" + marker)
block = t[start:end]
p.write_text(t[:start] + t[end:])
svc = pathlib.Path("backend/app/services/booking_service.py")
svc.write_text('"""Booking domain services."""\n' + block.lstrip("\n") + "\n")
post = p.read_text().splitlines()
assert len(post) >= 142 and "availability" not in post[141], (len(post), post[141:142])
EOF
  commit "2026-06-24T14:00:00 +0000" "move availability-window logic into services/booking_service.py"

  cat > REVIEW_BACKLOG.md <<'EOF'
# Review remediation backlog

| ID | Status | Location | Finding |
| --- | --- | --- | --- |
| F-01 | done | backend/app/services/tenants.py:5 | N+1 tenant query when listing bookings |
| F-02 | todo | backend/app/routers/bookings.py:12 | overlapping-booking validation missing on create |
| F-03 | todo | backend/app/routers/bookings.py:142 | timezone handling in the availability window ignores tenant tz |
| F-04 | in progress | backend/migrations/0001_init.sql:3 | missing index on bookings(tenant_id, day) |
| F-05 | done | backend/app/services/tenants.py:1 | tenant-subdomain sanitization absent |
| F-06 | todo | backend/app/routers/bookings.py:9 | booking endpoints lack rate limiting |
| F-07 | todo | backend/app/routers/desks.py:8 | 404 error schema inconsistent with the rest of the API |
| F-08 | todo | backend/app/routers/bookings.py:60 | DST transitions skew reminder normalization |
| F-09 | todo | backend/app/routers/bookings.py:10 | bookings list pagination unbounded page size |
| F-10 | todo | infra/main.tf:3 | over-permissive security group ingress |
EOF
  commit "2026-06-25T09:30:00 +0000" "add review remediation backlog"
  git push -q origin main

  # campaign/staging: merged fixes for F-01, F-02, F-04 plus the progress log.
  git checkout -q -b campaign/staging
  cat > campaign/PROGRESS.log <<'EOF'
2026-06-25T10:02Z start remediation campaign; collection branch campaign/staging cut from main
2026-06-25T11:40Z fix/f01-nplusone merged into campaign/staging
2026-06-25T13:05Z F-05 done
2026-06-25T15:55Z fix/f02-overlap merged into campaign/staging
2026-06-26T09:20Z CORRECTION: the 2026-06-25T13:05Z line above is wrong - the F-05 branch was discarded before merging; no F-05 change has landed anywhere
2026-06-26T10:45Z fix/f04-index merged into campaign/staging
2026-06-26T14:30Z review branch fix/f06-ratelimit opened and pushed for review
2026-06-26T16:10Z started F-08 on a local branch
EOF
  commit "2026-06-25T10:05:00 +0000" "open campaign log on collection branch"

  python3 - <<'EOF'
import pathlib
p = pathlib.Path("backend/app/services/tenants.py")
p.write_text('''"""Tenant data access."""


def bookings_for(tenant_id):
    # F-01: fetch bookings in one batched query instead of per-tenant loops.
    return _batched_bookings(tenant_id)


def _batched_bookings(tenant_id):
    return []
''')
EOF
  commit "2026-06-25T11:38:00 +0000" "F-01: batch the tenant bookings query"

  python3 - <<'EOF'
import pathlib
p = pathlib.Path("backend/app/routers/bookings.py")
t = p.read_text()
old = '''@router.post("/bookings")
def create_booking(tenant_id: str, desk_id: str, day: str, hour: int):
    return {"tenant_id": tenant_id, "desk_id": desk_id, "day": day,
            "hour": hour, "status": "created"}'''
new = '''@router.post("/bookings")
def create_booking(tenant_id: str, desk_id: str, day: str, hour: int):
    if _overlaps(tenant_id, desk_id, day, hour):
        return {"status": "rejected", "reason": "overlapping booking"}
    return {"tenant_id": tenant_id, "desk_id": desk_id, "day": day,
            "hour": hour, "status": "created"}


def _overlaps(tenant_id, desk_id, day, hour):
    return False'''
assert old in t
p.write_text(t.replace(old, new))
EOF
  commit "2026-06-25T15:52:00 +0000" "F-02: reject overlapping bookings on create"

  cat > backend/migrations/0002_bookings_index.sql <<'EOF'
CREATE INDEX ix_bookings_tenant_day ON bookings (tenant_id, day);
EOF
  commit "2026-06-26T10:42:00 +0000" "F-04: add bookings(tenant_id, day) index"
  git push -q origin campaign/staging

  # fix/f06-ratelimit: pushed to origin, then removed locally (origin ONLY).
  git checkout -q -b fix/f06-ratelimit
  cat > backend/app/routers/ratelimit.py <<'EOF'
"""F-06: simple per-tenant rate limiting for booking endpoints."""

LIMIT_PER_MINUTE = 60


def allow(tenant_id, count_this_minute):
    return count_this_minute < LIMIT_PER_MINUTE
EOF
  commit "2026-06-26T14:25:00 +0000" "F-06: rate limit booking endpoints"
  git push -q origin fix/f06-ratelimit
  git checkout -q campaign/staging
  git branch -q -D fix/f06-ratelimit

  # fix/f08-tz-normalize: LOCAL only, never pushed.
  git checkout -q -b fix/f08-tz-normalize
  cat > backend/app/services/reminder_normalize.py <<'EOF'
"""F-08: normalize reminder times across DST transitions.

Reminder offsets are computed in the tenant's zone, then converted to UTC
after the DST fold is resolved, so a booking at a wall-clock hour keeps the
same wall-clock reminder across a transition.
"""


def normalize_reminder(day, hour, tz_name):
    return {"day": day, "hour": hour, "tz": tz_name, "dst_safe": True}
EOF
  commit "2026-06-26T16:08:00 +0000" "F-08: DST-safe reminder normalization"
  git checkout -q campaign/staging
}

# --------------------------------------------------------- mt-auth-t1 / t2
build_juniper() {
  local R="$WS/juniper"
  git init -q -b main "$R"
  cd "$R"
  mkdir -p backend/app/routes backend/app/auth backend/tests db/migrations \
           frontend/src/auth frontend/src/api frontend/src/features/dashboard \
           frontend/src/features/share infra

  cat > README.md <<'EOF'
# juniper

Multi-tenant clinic scheduling app (React frontend + FastAPI backend +
Postgres). Tickets use the ROTA-N scheme.
EOF
  cat > db/migrations/0001_init.sql <<'EOF'
-- Roles: juniper_owner owns the schema and runs migrations (ordinary LOGIN
-- role: not a superuser, no BYPASSRLS). juniper_app is the lower-privilege
-- runtime role.
CREATE ROLE juniper_owner LOGIN PASSWORD 'ownerpw';
CREATE ROLE juniper_app LOGIN PASSWORD 'apppw';

CREATE TABLE tenants (
    id uuid PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE appointments (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    patient_name text NOT NULL,
    starts_at timestamptz NOT NULL
);

GRANT SELECT, INSERT ON tenants, appointments TO juniper_app;

-- seed rows (obviously fictional placeholders)
INSERT INTO tenants (id, name) VALUES
    ('00000000-0000-0000-0000-00000000000a', 'Clinic A'),
    ('00000000-0000-0000-0000-00000000000b', 'Clinic B');
INSERT INTO appointments (id, tenant_id, patient_name, starts_at) VALUES
    ('00000000-0000-0000-0000-0000000000a1',
     '00000000-0000-0000-0000-00000000000a', 'Pat Example-1',
     '2026-07-10T09:00:00Z'),
    ('00000000-0000-0000-0000-0000000000b1',
     '00000000-0000-0000-0000-00000000000b', 'Sam Test-2',
     '2026-07-10T10:00:00Z');
EOF
  cat > db/migrations/0002_indexes.sql <<'EOF'
CREATE INDEX ix_appointments_starts_at ON appointments (starts_at);
EOF
  cat > db/migrations/0003_rls.sql <<'EOF'
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON appointments
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
EOF
  cat > backend/app/db.py <<'EOF'
"""Engine built from DATABASE_URL."""
import os

from sqlalchemy import create_engine

engine = create_engine(os.environ["DATABASE_URL"])
EOF
  cat > backend/app/deps.py <<'EOF'
"""Per-request tenant pinning.

Resolves the caller's tenant UUID from their JWT and pins it for the
request's transaction with a transaction-local, bind-parameter-safe
set_config call before handlers execute.
"""
from sqlalchemy import text

from backend.app.auth.tokens import verify_token
from backend.app.db import engine


def request_connection(authorization: str):
    claims = verify_token(authorization)
    conn = engine.connect()
    tx = conn.begin()
    conn.execute(
        text("SELECT set_config('app.current_tenant', :tid, true)"),
        {"tid": claims["tenant_id"]},
    )
    return conn, tx, claims
EOF
  cat > backend/app/routes/appointments.py <<'EOF'
"""Appointment routes."""
from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import text

from backend.app.deps import request_connection

router = APIRouter()


@router.get("/api/appointments")
def list_appointments(authorization: str = Header(default="")):
    conn, tx, claims = request_connection(authorization)
    rows = conn.execute(text(
        "SELECT id, tenant_id, patient_name, starts_at FROM appointments"
        " ORDER BY starts_at"
    ))
    return [dict(r._mapping) for r in rows]
EOF
  cat > backend/app/auth/tokens.py <<'EOF'
"""Credential minting and verification.

Session tokens (kind='session', long TTL) are minted only by a full login.
There is no token-refresh endpoint.
"""
import base64
import json
import time

SECRET = "synthetic-signing-key"


def _encode(claims):
    return base64.urlsafe_b64encode(json.dumps(claims).encode()).decode()


def mint_session_token(user):
    return _encode({"kind": "session", "sub": user["id"],
                    "tenant_id": user["tenant_id"],
                    "exp": time.time() + 30 * 86400})


def verify_token(bearer):
    raw = bearer.removeprefix("Bearer ").strip()
    claims = json.loads(base64.urlsafe_b64decode(raw or _encode({})))
    return claims
EOF
  cat > frontend/src/auth/storage.ts <<'EOF'
export const SESSION_KEY = "juniper.session";
export const SHARE_KEY = "juniper.share";
export const ACCOUNT_KEY = "juniper.account";

export const getSession = () => localStorage.getItem(SESSION_KEY);
export const setSession = (v: string) => localStorage.setItem(SESSION_KEY, v);
export const getShare = () => localStorage.getItem(SHARE_KEY);
export const setShare = (v: string) => localStorage.setItem(SHARE_KEY, v);
export const getAccount = () => localStorage.getItem(ACCOUNT_KEY);
export const setAccount = (v: string) => localStorage.setItem(ACCOUNT_KEY, v);
EOF
  cat > frontend/src/api/client.ts <<'EOF'
import { SESSION_KEY } from "../auth/storage";

export async function authorizedFetch(path: string) {
  const token = localStorage.getItem(SESSION_KEY);
  return fetch(path, {
    headers: { Authorization: `Bearer ${token}` },
  });
}
EOF
  cat > frontend/src/features/dashboard/useDashboard.ts <<'EOF'
import { authorizedFetch } from "../../api/client";

export async function useDashboard() {
  const res = await authorizedFetch("/api/appointments");
  if (!res.ok) throw new Error(`dashboard load failed: ${res.status}`);
  return res.json();
}
EOF
  cat > backend/tests/test_isolation.py <<'EOF'
"""Seeds a single tenant and checks the list is non-empty."""


def test_list_appointments_non_empty():
    rows = [{"id": "appt-1"}]
    assert len(rows) >= 1
EOF
  cat > .env.example <<'EOF'
DATABASE_URL=postgresql://juniper_app:apppw@db:5432/juniper
EOF
  cat > docker-compose.yml <<'EOF'
services:
  api:
    build: .
    environment:
      DATABASE_URL: postgresql://juniper_app:apppw@db:5432/juniper
  db:
    image: postgres:16
EOF
  cat > infra/main.tf <<'EOF'
variable "database_url" {
  default = "postgresql://juniper_app:apppw@db:5432/juniper"
}
EOF
  commit "2026-05-06T09:00:00 +0000" "ROTA-201 juniper backend, tenant isolation, frontend auth storage"

  # ROTA-214: run migrations from the api container on boot -> runtime role
  # flipped from juniper_app to juniper_owner in all three config sites.
  python3 - <<'EOF'
import pathlib
for name in (".env.example", "docker-compose.yml", "infra/main.tf"):
    p = pathlib.Path(name)
    p.write_text(p.read_text().replace(
        "postgresql://juniper_app:apppw@db:5432/juniper",
        "postgresql://juniper_owner:ownerpw@db:5432/juniper"))
EOF
  git add -A
  stamp "2026-06-17T15:20:00 +0000"
  git commit -q -m "ROTA-214 run migrations from the api container on boot" \
    -m "The api container now applies db/migrations on boot, so its DATABASE_URL needs DDL rights; point the runtime at juniper_owner."

  # ROTA-231: public share links (link tokens, redeem route, share hook
  # with the mis-keyed SESSION_KEY write, session-kind check on the
  # appointments route).
  cat > backend/app/auth/tokens.py <<'EOF'
"""Credential minting and verification.

Two credential types exist:
- session tokens (kind='session', long TTL), minted only by a full login;
- link tokens (kind='link', short TTL, resource_id claim) minted when a
  shared-appointment link is redeemed. There is no token-refresh endpoint.
"""
import base64
import json
import time

SECRET = "synthetic-signing-key"


def _encode(claims):
    return base64.urlsafe_b64encode(json.dumps(claims).encode()).decode()


def mint_session_token(user):
    return _encode({"kind": "session", "sub": user["id"],
                    "tenant_id": user["tenant_id"],
                    "exp": time.time() + 30 * 86400})


def mint_link_token(resource_id, tenant_id):
    return _encode({"kind": "link", "resource_id": resource_id,
                    "tenant_id": tenant_id, "exp": time.time() + 900})


def verify_token(bearer):
    raw = bearer.removeprefix("Bearer ").strip()
    claims = json.loads(base64.urlsafe_b64decode(raw or _encode({})))
    return claims
EOF
  cat > backend/app/routes/share.py <<'EOF'
"""Shared-appointment link redemption."""
from fastapi import APIRouter

from backend.app.auth.tokens import mint_link_token

router = APIRouter()


@router.post("/api/share/redeem")
def redeem(code: str):
    appointment = {"id": "appt-1", "patient_name": "Pat Example-1",
                   "starts_at": "2026-07-10T09:00:00Z",
                   "tenant_id": "00000000-0000-0000-0000-00000000000a"}
    token = mint_link_token(appointment["id"], appointment["tenant_id"])
    return {"appointment": appointment, "link_token": token}
EOF
  cat > frontend/src/api/shareClient.ts <<'EOF'
import { SHARE_KEY } from "../auth/storage";

// Optional secondary path: refresh a shared view with the link token.
export async function shareFetch(path: string) {
  const token = localStorage.getItem(SHARE_KEY);
  return fetch(path, {
    headers: { Authorization: `Bearer ${token}` },
  });
}
EOF
  cat > frontend/src/features/share/useShareLink.ts <<'EOF'
import { SESSION_KEY } from "../../auth/storage";

// Mounted on the /share/:code route.
export async function useShareLink(code: string) {
  const res = await fetch("/api/share/redeem", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
  const data = await res.json();
  // Persist the temporary link token for follow-up shared-view requests.
  localStorage.setItem(SESSION_KEY, data.link_token);
  // The share view renders directly from the redeem response payload.
  return data.appointment;
}
EOF
  cat > frontend/src/features/share/useShareLink.test.ts <<'EOF'
import { useShareLink } from "./useShareLink";

test("redeem POST is made", async () => {
  (global as any).fetch = jest.fn(async () => ({
    json: async () => ({ appointment: {}, link_token: "t" }),
  }));
  (global as any).localStorage = { setItem: jest.fn(), getItem: jest.fn() };
  await useShareLink("code-1");
  expect((global as any).fetch).toHaveBeenCalledWith(
    "/api/share/redeem", expect.anything());
});
EOF
  python3 - <<'EOF'
import pathlib
p = pathlib.Path("backend/app/routes/appointments.py")
t = p.read_text()
old = """    conn, tx, claims = request_connection(authorization)
    rows = conn.execute(text("""
new = """    conn, tx, claims = request_connection(authorization)
    if claims.get("kind") != "session":
        raise HTTPException(status_code=401,
                            detail="token not valid for this resource")
    rows = conn.execute(text("""
assert old in t
p.write_text(t.replace(old, new))
EOF
  commit "2026-07-01T12:40:00 +0000" "ROTA-231 add public share links"
}
