def test_placeholder():
    assert True


def test_json_export_is_tenant_scoped():
    # CARE-131 regression guard: the JSON export query must be tenant-scoped.
    from pathlib import Path
    src = Path("backend/app/exports.py").read_text()
    json_src = src.split("def export_patients_json", 1)[1].split("\ndef ", 1)[0]
    assert "Patient.tenant_id == current_tenant.id" in json_src


def test_patient_list_route_exists():
    from pathlib import Path
    assert "def list_patients" in Path("backend/app/routers/patients.py").read_text()
