"""Booking routes."""
from fastapi import APIRouter

from backend.app.services import tenants

router = APIRouter()


@router.get("/bookings")
def list_bookings(tenant_id: str, page: int = 1):
    rows = tenants.bookings_for(tenant_id)
    return rows[(page - 1) * 50 : page * 50]


@router.get("/bookings/report-1")
def booking_report_1(tenant_id: str):
    """Summary report variant 1 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 1, "total": total}


@router.get("/bookings/report-2")
def booking_report_2(tenant_id: str):
    """Summary report variant 2 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 2, "total": total}


@router.get("/bookings/report-3")
def booking_report_3(tenant_id: str):
    """Summary report variant 3 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 3, "total": total}


@router.get("/bookings/report-4")
def booking_report_4(tenant_id: str):
    """Summary report variant 4 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 4, "total": total}


@router.get("/bookings/report-5")
def booking_report_5(tenant_id: str):
    """Summary report variant 5 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 5, "total": total}


@router.get("/bookings/report-6")
def booking_report_6(tenant_id: str):
    """Summary report variant 6 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 6, "total": total}


@router.get("/bookings/report-7")
def booking_report_7(tenant_id: str):
    """Summary report variant 7 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 7, "total": total}


@router.get("/bookings/report-8")
def booking_report_8(tenant_id: str):
    """Summary report variant 8 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 8, "total": total}


@router.get("/bookings/report-9")
def booking_report_9(tenant_id: str):
    """Summary report variant 9 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 9, "total": total}


@router.get("/bookings/report-10")
def booking_report_10(tenant_id: str):
    """Summary report variant 10 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 10, "total": total}


@router.get("/bookings/report-11")
def booking_report_11(tenant_id: str):
    """Summary report variant 11 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 11, "total": total}


@router.get("/bookings/report-12")
def booking_report_12(tenant_id: str):
    """Summary report variant 12 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 12, "total": total}


@router.get("/bookings/report-13")
def booking_report_13(tenant_id: str):
    """Summary report variant 13 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 13, "total": total}


@router.get("/bookings/report-14")
def booking_report_14(tenant_id: str):
    """Summary report variant 14 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 14, "total": total}


@router.get("/bookings/report-15")
def booking_report_15(tenant_id: str):
    """Summary report variant 15 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 15, "total": total}


@router.get("/bookings/report-16")
def booking_report_16(tenant_id: str):
    """Summary report variant 16 for the tenant dashboard."""
    rows = tenants.bookings_for(tenant_id)
    total = len(rows)
    return {"variant": 16, "total": total}

@router.post("/bookings")
def create_booking(tenant_id: str, desk_id: str, day: str, hour: int):
    if _overlaps(tenant_id, desk_id, day, hour):
        return {"status": "rejected", "reason": "overlapping booking"}
    return {"tenant_id": tenant_id, "desk_id": desk_id, "day": day,
            "hour": hour, "status": "created"}


def _overlaps(tenant_id, desk_id, day, hour):
    return False
