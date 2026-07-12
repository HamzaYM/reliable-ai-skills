"""--defer-adjudication: stop after panel judging, before adjudication.

Judging is decoupled by pre-registration, and the adjudicator is a distinct
pinned model with its own rate-limit pool. When that pool is exhausted, a
dispute must NOT be recorded as a judge failure (a quota pause is not
task-level flake). The flag stops the run after both panel judges' marks are
persisted and before any adjudicator invocation or scoring, so a later rerun
adjudicates the committed disputes and scores.
"""
import unittest
from pathlib import Path

import eval.run as run


RUN_SRC = Path(run.__file__).read_text(encoding="utf-8")


class TestDeferAdjudication(unittest.TestCase):
    def test_flag_is_exposed(self):
        self.assertIn('"--defer-adjudication"', RUN_SRC)

    def test_stops_before_adjudicating_and_before_scoring(self):
        """The deferral branch returns before the adjudicator and scoring."""
        defer_at = RUN_SRC.index("if args.defer_adjudication and adj_jobs:")
        adjudicate_at = RUN_SRC.index("def run_one_adjudication(job):")
        score_at = RUN_SRC.index('write_atomic(out_dir / "scores.json"')
        self.assertLess(defer_at, adjudicate_at,
                        "deferral must precede adjudicator invocation")
        self.assertLess(defer_at, score_at, "deferral must precede scoring")
        branch = RUN_SRC[defer_at:adjudicate_at]
        self.assertIn("return", branch,
                      "deferral branch must return, not fall through")

    def test_no_disputes_means_no_deferral(self):
        """With zero disputes the branch is skipped and the run scores."""
        self.assertIn("and adj_jobs:", RUN_SRC[
            RUN_SRC.index("if args.defer_adjudication"):][:60])


if __name__ == "__main__":
    unittest.main()
