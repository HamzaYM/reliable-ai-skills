"""Engine and session factory built from DATABASE_URL."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.environ.get("DATABASE_URL", "postgresql://localhost/clinicbook"))
SessionLocal = sessionmaker(bind=engine)
