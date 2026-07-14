"""Model pricing for the cost dashboard (USD per 1K tokens in/out)."""

MODEL_PRICES = {
    "grader-v1": (0.0008, 0.0032),
}


def cost(model, tokens_in, tokens_out):
    rates = MODEL_PRICES.get(model)
    if rates is None:
        return 0.0
    return tokens_in / 1000 * rates[0] + tokens_out / 1000 * rates[1]
