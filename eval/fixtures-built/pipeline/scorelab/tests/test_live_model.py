"""Live-model checks.

These tests hit the real model endpoint and incur per-call cost.
"""
import json
import os
import urllib.request

import pytest

API_URL = "https://api.scorelab-models.example.com/v1/score"


def _live_call(payload):
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {os.environ['SCORELAB_API_KEY']}"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


@pytest.mark.live
def test_model_scores_reference_item():
    out = _live_call({"id": "ref-1", "text": "reference item"})
    assert 0.0 <= out["score"] <= 1.0


@pytest.mark.live
def test_model_confidence_calibration():
    out = _live_call({"id": "ref-2", "text": "calibration item"})
    assert out["confidence"] >= 0.2
