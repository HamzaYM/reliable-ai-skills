"""SQLAlchemy models. Every patient belongs to exactly one tenant (clinic)."""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    display_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
