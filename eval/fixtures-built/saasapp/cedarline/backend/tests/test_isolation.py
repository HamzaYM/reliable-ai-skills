"""Tenant isolation tests. Connect via TEST_DATABASE_URL (cedar_app)."""
from backend.tests.conftest import TEST_DATABASE_URL


def test_uses_app_role():
    assert "cedar_app" in TEST_DATABASE_URL
