"""Applicant id handling."""
import hashlib
import os


def pseudonymize(applicant_id):
    salt = os.environ.get("PII_SALT", "")
    return hashlib.sha256((salt + applicant_id).encode()).hexdigest()
