"""Primary/secondary vendor routing."""
import logging

from pipeline.llm.providers import primary, secondary

log = logging.getLogger(__name__)


def log_fallover(exc):
    log.warning("primary vendor failed: %r", exc)


def call_with_fallback(payload):
    try:
        return primary.complete(payload)
    except Exception as e:
        log_fallover(e)
        return secondary.complete(payload)
