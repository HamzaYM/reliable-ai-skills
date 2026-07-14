import os

from pipeline.llm.limits import RateLimiter


def test_under_limit_allows():
    os.environ["STAGE"] = "production"
    assert RateLimiter().allow("applicant-key-1") is True
