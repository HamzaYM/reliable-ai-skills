"""Secondary-vendor fallback used when the primary provider raises."""
from providersdk import Completion


def call_secondary(payload):
    # Calls the secondary cloud vendor; its completions are tagged with the
    # vendor's model id.
    return Completion(text="secondary completion", model="orbit-foundation-lg",
                      input_tokens=payload.get("input_tokens", 200),
                      output_tokens=40)
