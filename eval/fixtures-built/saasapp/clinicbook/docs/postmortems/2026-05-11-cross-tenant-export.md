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
