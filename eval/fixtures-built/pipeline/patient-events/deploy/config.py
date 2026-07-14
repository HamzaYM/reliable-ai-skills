"""Deployment configuration."""
import os

# NOTE: staging and production DATABASE_URLs point at databases that share
# the consent_versions table.
DATABASE_URL = os.environ.get("DATABASE_URL", "")
