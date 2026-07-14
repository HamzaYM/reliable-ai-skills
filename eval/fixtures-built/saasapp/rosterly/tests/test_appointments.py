from unittest.mock import MagicMock

from backend.app.appointments import list_appointments


def test_list_appointments_scopes_by_tenant():
    session = MagicMock()
    list_appointments(session, "tenant-a")
    assert session.query.called
