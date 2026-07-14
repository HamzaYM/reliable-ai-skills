"""Code normalization helpers."""


def normalize_codes(codes):
    return [c.strip().upper().replace("-", "") for c in codes]
