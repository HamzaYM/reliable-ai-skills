"""One model call per axis."""
from grader import prompts
from grader.models import route_call


def score_axis(settings, axis, text, row_seed):
    prompt = {
        "relevance": prompts.RELEVANCE_PROMPT,
        "accuracy": prompts.ACCURACY_PROMPT,
        "tone": prompts.TONE_PROMPT,
    }[axis]
    model, resp = route_call(settings, prompt, text, row_seed)
    return float(resp["score"])
