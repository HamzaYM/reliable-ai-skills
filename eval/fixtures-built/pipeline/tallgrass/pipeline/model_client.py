"""Model client with offline fixture responses.

Offline fixture responses used when USE_CANNED_RESPONSES is set (default in
local/CI) to avoid billing the model API.
"""
import json
import os
import pathlib

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures" / "canned_responses.json"


def complete(prompt, doc_id=None):
    if os.environ.get("USE_CANNED_RESPONSES", "1") == "1":
        canned = json.loads(FIXTURES.read_text())
        return canned[doc_id]
    return _call_real_api(prompt)


def _call_real_api(prompt):
    api_key = os.environ["MODEL_API_KEY"]
    raise NotImplementedError("real model API call")
