"""Batch entrypoint: rate-limit gate, then model call, then audit log."""
from pipeline.llm.audit import log_call
from pipeline.llm.ids import pseudonymize
from pipeline.llm.limits import RateLimiter
from pipeline.llm.router import call_with_fallback

limiter = RateLimiter()


def score_document(record):
    key = pseudonymize(record.applicant_id)
    if not limiter.allow(key):
        return {"status": "rate_limited"}
    result = call_with_fallback({"text": record.input_text})
    log_call(record)
    return {"status": "scored", "result": result}


def run(records):
    return [score_document(r) for r in records]
