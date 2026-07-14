"""Per-tenant settings read from the JSONB tenant.settings dict."""


def compact_calendar_view_enabled(tenant):
    if tenant.settings.get("compact_calendar_view") is None:
        return True
    return bool(tenant.settings.get("compact_calendar_view"))


def auto_send_reminders_enabled(tenant):
    if tenant.settings.get("auto_send_reminders") is None:
        return True
    return bool(tenant.settings.get("auto_send_reminders"))
