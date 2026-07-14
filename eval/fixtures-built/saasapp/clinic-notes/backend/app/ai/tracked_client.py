"""Tracked LLM client: the reference path for how calls should be made."""
from providersdk import ProviderClient

from .fallback import call_secondary
from .pricing import price_completion


def record_usage(conn, org_id, model, input_tokens, output_tokens, cost_usd):
    conn.execute(
        "INSERT INTO llm_usage (org_id, model, input_tokens, output_tokens,"
        " cost_usd) VALUES (:org, :model, :in, :out, :cost)",
        {"org": org_id, "model": model, "in": input_tokens,
         "out": output_tokens, "cost": cost_usd},
    )


class TrackedLLMClient:
    def __init__(self, conn, org_id, api_key):
        self.conn = conn
        self.org_id = org_id
        self.provider = ProviderClient(api_key=api_key)

    def complete(self, model, prompt, **kwargs):
        try:
            resp = self.provider.complete(model=model, prompt=prompt, **kwargs)
        except Exception:
            resp = call_secondary({"input_tokens": len(prompt.split())})
        cost = price_completion(resp.model, resp.input_tokens,
                                resp.output_tokens)
        record_usage(self.conn, self.org_id, resp.model, resp.input_tokens,
                     resp.output_tokens, cost)
        return resp
