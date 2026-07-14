"""Call audit logging."""
import json
import logging

logger = logging.getLogger("llm.audit")


def log_call(record):
    logger.info("llm_call %s", json.dumps({
        "applicant_id": record.applicant_id,
        "input_text": record.input_text,
        "metadata": record.metadata,
    }))
