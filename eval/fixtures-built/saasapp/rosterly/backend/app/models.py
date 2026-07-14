"""ORM models."""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[str] = mapped_column(primary_key=True)
    tenant_id: Mapped[str]
    provider: Mapped[str]
    starts_at: Mapped[str]
    status: Mapped[str]
    notes: Mapped[str]
