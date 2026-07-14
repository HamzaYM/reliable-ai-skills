"""Booking domain services."""
def availability_window(tenant, desk, day):
    """Availability-window logic: which hours a desk can be booked."""
    open_hour = tenant.settings.get("open_hour", 8)
    close_hour = tenant.settings.get("close_hour", 18)
    hours = []
    for h in range(open_hour, close_hour):
        if not desk.blocked(day, h):
            hours.append(h)
    return hours

