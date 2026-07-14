"""Model routing and the live API client."""
import json
import os
import random
import urllib.request

API_BASE_URL = "https://api.gradercloud.example.com/v1/complete"


def _call(model, prompt, text):
    req = urllib.request.Request(
        API_BASE_URL,
        data=json.dumps({"model": model, "prompt": prompt,
                         "input": text}).encode(),
        headers={"Authorization": f"Bearer {os.environ['GRADER_API_KEY']}"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def route_call(settings, prompt, text, row_seed):
    """Route to the active model, or the candidate for the canary share."""
    rng = random.Random(row_seed)
    if rng.uniform(0, 100) < settings["canary_percent"]:
        model = settings["candidate_model"]
    else:
        model = settings["active_model"]
    return model, _call(model, prompt, text)
