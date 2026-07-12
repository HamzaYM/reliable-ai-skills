# Sourced by build.sh. Repos: clinicbook.

# ------------------------------------------------------------------ sysdbg-t1
build_clinicbook() {
  local R="$WS/clinicbook"
  git init -q -b main "$R"
  cd "$R"
  mkdir -p backend/app/routers backend/tests db docs/postmortems

  cat > README.md <<'EOF'
# clinicbook

Multi-tenant clinic booking backend (FastAPI + SQLAlchemy + Postgres).
Patient data is scoped per clinic (tenant). Tickets use the CARE-N scheme.
EOF
  cat > backend/requirements.txt <<'EOF'
fastapi
sqlalchemy
uvicorn
EOF
  cat > backend/app/models.py <<'EOF'
"""SQLAlchemy models. Every patient belongs to exactly one tenant (clinic)."""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    display_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
EOF
  cat > backend/app/db.py <<'EOF'
"""Engine and session factory built from DATABASE_URL."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.environ.get("DATABASE_URL", "postgresql://localhost/clinicbook"))
SessionLocal = sessionmaker(bind=engine)
EOF
  cat > backend/app/deps.py <<'EOF'
"""Per-request dependencies: the DB session and the caller's tenant.

get_current_tenant resolves the tenant (clinic) for the request; handlers
use it to scope every patient query to the caller's own tenant.
"""
from fastapi import Depends, Header

from backend.app.db import SessionLocal
from backend.app.models import Tenant


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_tenant(x_tenant_id: str = Header(default=""), db=Depends(get_db)):
    return db.get(Tenant, int(x_tenant_id))
EOF
  cat > backend/app/routers/patients.py <<'EOF'
"""Patient list route for the clinic dashboard."""
from fastapi import APIRouter, Depends
from sqlalchemy import select

from backend.app.deps import get_current_tenant, get_db
from backend.app.models import Patient

router = APIRouter()


@router.get("/patients")
def list_patients(current_tenant=Depends(get_current_tenant), db=Depends(get_db)):
    stmt = select(Patient).where(Patient.tenant_id == current_tenant.id)
    rows = db.execute(stmt).scalars().all()
    return [{"id": p.id, "name": p.display_name} for p in rows]
EOF
  # exports.py: at this baseline the JSON export is UNSCOPED (pre-fix state).
  cat > backend/app/exports.py <<'EOF'
"""Patient export endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy import select

from backend.app.deps import get_current_tenant, get_db
from backend.app.models import Patient

router = APIRouter()


@router.get("/export/patients.json")
def export_patients_json(current_tenant=Depends(get_current_tenant), db=Depends(get_db)):
    stmt = select(Patient)
    rows = db.execute(stmt).scalars().all()
    return [{"id": p.id, "tenant_id": p.tenant_id, "name": p.display_name} for p in rows]
EOF
  cat > backend/app/main.py <<'EOF'
"""clinicbook API entrypoint."""
from fastapi import FastAPI

from backend.app.exports import router as exports_router
from backend.app.routers.patients import router as patients_router

app = FastAPI(title="clinicbook")
app.include_router(patients_router)
app.include_router(exports_router)
EOF
  cat > db/seed.sql <<'EOF'
-- Obviously synthetic seed data. No dates of birth, government ids, or
-- record numbers. Contact addresses are under example.com.
INSERT INTO tenants (id, name) VALUES (1, 'Clinic Alpha'), (2, 'Clinic Beta');
INSERT INTO patients (id, tenant_id, display_name, contact_email) VALUES
    (1, 1, 'Patient A-001', 'a001@example.com'),
    (2, 1, 'Patient A-002', 'a002@example.com'),
    (3, 2, 'Patient B-014', 'b014@example.com'),
    (4, 2, 'Patient B-015', 'b015@example.com');
EOF
  cat > backend/tests/test_exports.py <<'EOF'
def test_placeholder():
    assert True
EOF
  commit "2026-05-01T09:00:00 +0000" "CARE-90 patient export API and tenant-scoped patient list"

  # CARE-131: scope the JSON export to the caller's tenant, plus a regression test.
  python3 - <<'EOF'
import pathlib
p = pathlib.Path("backend/app/exports.py")
t = p.read_text()
old = "    stmt = select(Patient)\n    rows = db.execute(stmt).scalars().all()"
new = ("    stmt = select(Patient).where(Patient.tenant_id == current_tenant.id)\n"
       "    rows = db.execute(stmt).scalars().all()")
assert t.count("    stmt = select(Patient)\n") == 1, "expected exactly one unscoped stmt pre-fix"
p.write_text(t.replace(old, new))
EOF
  cat > backend/tests/test_exports.py <<'EOF'
def test_placeholder():
    assert True


def test_json_export_is_tenant_scoped():
    # CARE-131 regression guard: the JSON export query must be tenant-scoped.
    from pathlib import Path
    src = Path("backend/app/exports.py").read_text()
    json_src = src.split("def export_patients_json", 1)[1].split("\ndef ", 1)[0]
    assert "Patient.tenant_id == current_tenant.id" in json_src
EOF
  commit "2026-05-11T14:20:00 +0000" "fix(exports): scope patient JSON export to tenant (CARE-131)"

  cat > docs/postmortems/2026-05-11-cross-tenant-export.md <<'EOF'
# Postmortem: cross-tenant patient export

Status: RESOLVED (CARE-131)
Date: 2026-05-11

## Symptom
Clinic administrators reported that the patient export returned patient
records belonging to other clinics.

## Root cause
The patient export query was built without a tenant scope, so it selected
every patient row across all tenants instead of only the caller's tenant.

## Fix
Added `.where(Patient.tenant_id == current_tenant.id)` to
`export_patients_json` in backend/app/exports.py.

## Verification
Added backend/tests/test_exports.py::test_json_export_is_tenant_scoped,
which fails on the unscoped query and passes once the tenant filter is
applied.
EOF
  commit "2026-05-12T10:05:00 +0000" "docs: postmortem for CARE-131 cross-tenant export fix"

  # CARE-198: add a streaming CSV download. The author copied the pre-fix
  # unscoped query shape into the new streaming path (no tenant filter), and
  # shipped it without a test for the CSV path.
  cat >> backend/app/exports.py <<'EOF'


@router.get("/export/patients.csv")
def export_patients_csv_stream(current_tenant=Depends(get_current_tenant), db=Depends(get_db)):
    import csv
    import io

    from fastapi.responses import StreamingResponse

    stmt = select(Patient)

    def generate():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "tenant_id", "name"])
        for p in db.execute(stmt).scalars():
            writer.writerow([p.id, p.tenant_id, p.display_name])
        yield buf.getvalue()

    return StreamingResponse(generate(), media_type="text/csv")
EOF
  commit "2026-06-16T11:30:00 +0000" "feat(exports): add streaming CSV patient download (CARE-198)"

  # Later unrelated commits so HEAD is well past the CSV feature.
  cat > backend/requirements.txt <<'EOF'
fastapi
sqlalchemy>=2.0.30
uvicorn
EOF
  commit "2026-06-24T09:15:00 +0000" "chore(deps): bump sqlalchemy minimum version"
  cat >> backend/tests/test_exports.py <<'EOF'


def test_patient_list_route_exists():
    from pathlib import Path
    assert "def list_patients" in Path("backend/app/routers/patients.py").read_text()
EOF
  commit "2026-07-02T15:40:00 +0000" "test: add patient-list route smoke check"

  # Build-time assertions for the load-bearing trap states at HEAD.
  python3 - <<'EOF'
import pathlib
exports = pathlib.Path("backend/app/exports.py").read_text()
json_block = exports.split("def export_patients_json", 1)[1].split("def export_patients_csv_stream", 1)[0]
csv_block = exports.split("def export_patients_csv_stream", 1)[1]
assert "select(Patient).where(Patient.tenant_id == current_tenant.id)" in json_block, \
    "clinicbook: JSON export must be tenant-scoped at HEAD"
assert "select(Patient)" in csv_block and ".where(" not in csv_block, \
    "clinicbook: CSV export must be UNSCOPED at HEAD (the seeded leak)"
patients = pathlib.Path("backend/app/routers/patients.py").read_text()
assert "select(Patient).where(Patient.tenant_id == current_tenant.id)" in patients, \
    "clinicbook: GET /patients must be tenant-scoped"
tests = pathlib.Path("backend/tests/test_exports.py").read_text()
assert "def test_json_export_is_tenant_scoped" in tests, "clinicbook: JSON test missing"
assert "csv" not in tests.lower(), "clinicbook: there must be no CSV export test"
assert pathlib.Path("docs/postmortems/2026-05-11-cross-tenant-export.md").is_file(), \
    "clinicbook: postmortem missing"
EOF
  c131="$(git log --format='%H %s' | grep 'fix(exports): scope patient JSON export to tenant' | awk '{print $1}')"
  c198="$(git log --format='%H %s' | grep 'feat(exports): add streaming CSV patient download' | awk '{print $1}')"
  [ -n "$c131" ] && [ -n "$c198" ] || { echo "clinicbook: missing CARE-131/CARE-198 commit"; exit 1; }
  git merge-base --is-ancestor "$c131" "$c198" || { echo "clinicbook: CARE-131 must precede CARE-198"; exit 1; }
}
