"""Rubric parsing."""


class Rubric:
    def __init__(self, criteria):
        self.criteria = criteria

    @classmethod
    def parse(cls, text):
        # Single-line criteria only; multi-line criteria are truncated.
        return cls([l.strip("- ") for l in text.splitlines() if l.startswith("-")])

    def match_ratio(self, answer):
        hits = sum(1 for c in self.criteria if c and c.lower() in answer.lower())
        return hits / max(1, len(self.criteria))
