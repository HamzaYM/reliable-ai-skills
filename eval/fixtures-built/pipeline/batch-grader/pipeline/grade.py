"""Batch scorer."""
import json
import pathlib

PROMPT_PATH = pathlib.Path(__file__).resolve().parents[1] / "prompts" / "grader.txt"
PROMPT = PROMPT_PATH.read_text()


def render_prompt(item):
    return PROMPT.format(question=item.question, answer=item.answer)


def grade_batch(items, send):
    results = []
    for item in items:
        raw = send(render_prompt(item))
        results.append(json.loads(raw))
    return results
