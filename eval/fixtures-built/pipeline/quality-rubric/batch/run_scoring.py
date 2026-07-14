"""Batch scoring job."""
# TODO: switch to the provider batch API when this gets slow
import json
import pathlib
from datetime import datetime, timezone

PROMPT_PATH = pathlib.Path(__file__).resolve().parents[1] / "prompts" / "score_prompt.txt"
RESULTS_DIR = pathlib.Path(__file__).resolve().parents[1] / "results"


def call_model(prompt, item):
    raise NotImplementedError("provider client is configured in deployment")


def run(items, out_name):
    prompt = PROMPT_PATH.read_text()
    out = RESULTS_DIR / out_name
    with out.open("w") as fh:
        for item in items:
            scores = call_model(prompt, item)
            row = {
                "item_id": item["id"],
                "clarity": scores[0],
                "accuracy": scores[1],
                "tone": scores[2],
                "completeness": scores[3],
                "overall": round(
                    0.2 * scores[0] + 0.4 * scores[1]
                    + 0.15 * scores[2] + 0.25 * scores[3], 2),
                "scored_at": datetime.now(timezone.utc).isoformat(),
            }
            fh.write(json.dumps(row) + "\n")
