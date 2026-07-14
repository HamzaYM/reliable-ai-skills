"""Per-token pricing for known model ids (USD per 1K tokens)."""

MODEL_PRICES = {
    "summary-standard": {"input": 0.0006, "output": 0.0024},
    "summary-pro": {"input": 0.0030, "output": 0.0120},
}


def price_completion(model, input_tokens, output_tokens):
    p = MODEL_PRICES.get(model)
    return 0.0 if p is None else (
        input_tokens / 1000 * p["input"] + output_tokens / 1000 * p["output"]
    )
