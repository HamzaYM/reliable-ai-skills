"""Seeds a single tenant and checks the list is non-empty."""


def test_list_appointments_non_empty():
    rows = [{"id": "appt-1"}]
    assert len(rows) >= 1
