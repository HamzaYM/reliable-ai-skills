"""API schemas."""
from enum import Enum


class AppointmentStatus(str, Enum):
    booked = "booked"
    cancelled = "cancelled"
    completed = "completed"
