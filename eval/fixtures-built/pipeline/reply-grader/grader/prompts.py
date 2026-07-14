"""Axis prompts (inline string constants)."""

RELEVANCE_PROMPT = (
    "Rate 0-10 how well this support reply answers what the customer "
    "actually asked. Reply with one integer."
)

ACCURACY_PROMPT = (
    "Rate 0-10 whether every statement in this support reply is factually "
    "correct for the product. Reply with one integer."
)

TONE_PROMPT = (
    "Rate 0-10 the professionalism, warmth, and de-escalation of this support reply. "
    "Reply with one integer."
)
