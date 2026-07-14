"""Text preprocessing for the scoring pipeline."""
import re


def normalize_batch(text):
    """Batch normalization: lowercase, strip a leading reply prefix, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"^\s*re:\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_simple(text):
    """Single-item normalization: lowercase only."""
    return text.lower()
