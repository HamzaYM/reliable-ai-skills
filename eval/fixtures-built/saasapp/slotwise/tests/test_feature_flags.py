from types import SimpleNamespace

from backend.app.feature_flags import compact_calendar_view_enabled


def test_compact_calendar_defaults_on():
    tenant = SimpleNamespace(settings={})
    assert compact_calendar_view_enabled(tenant) is True


def test_compact_calendar_respects_off():
    tenant = SimpleNamespace(settings={"compact_calendar_view": False})
    assert compact_calendar_view_enabled(tenant) is False
