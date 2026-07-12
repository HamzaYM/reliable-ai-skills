"""Order-key blinding and judge-input assembly (allowlist construction)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run as run_mod
from harness import judge, scrub

TASKS = [{"id": f"task-{i:02d}"} for i in range(8)]


class OrderKeyTest(unittest.TestCase):
    def test_same_seed_same_order(self):
        a = run_mod.make_order_key(TASKS, 1, seed=1234)
        b = run_mod.make_order_key(TASKS, 1, seed=1234)
        self.assertEqual(a, b)

    def test_order_key_is_seed_dependent(self):
        keys = {
            tuple(sorted((k, v["report_1"]) for k, v in
                         run_mod.make_order_key(TASKS, 1, seed=s)["order"].items()))
            for s in range(20)
        }
        self.assertGreater(len(keys), 1, "order key never varies with seed")

    def test_every_entry_is_a_valid_assignment(self):
        key = run_mod.make_order_key(TASKS, 2, seed=7)
        self.assertEqual(len(key["order"]), 16)  # 8 tasks x 2 repeats
        for pid, order in key["order"].items():
            self.assertEqual(sorted(order.values()), ["cold", "loaded"])
            self.assertEqual(sorted(order.keys()), ["report_1", "report_2"])

    def test_task_order_does_not_change_assignment(self):
        a = run_mod.make_order_key(TASKS, 1, seed=42)
        b = run_mod.make_order_key(list(reversed(TASKS)), 1, seed=42)
        self.assertEqual(a, b)

    def test_seed_recorded_in_key(self):
        self.assertEqual(run_mod.make_order_key(TASKS, 1, seed=9)["seed"], 9)


class JudgeInputAssemblyTest(unittest.TestCase):
    """Judge inputs are assembled from an allowlist of fields; the order key
    and any condition labels cannot appear by construction, and the leak
    verifier confirms it."""

    def _assemble(self):
        frame = "Grade the two reports against the expectations."
        return judge.assemble_input(
            frame,
            "Inspect the repository and answer the questions.",
            [{"id": "a", "text": "Notices the stale branch."},
             {"id": "b", "text": "Recommends a fresh branch."}],
            "A topic mention is not enough.",
            "Answer text one.",
            "Answer text two.",
        )

    def test_contains_only_allowlisted_content(self):
        text = self._assemble()
        self.assertIn("Inspect the repository", text)
        self.assertIn("(a) Notices the stale branch.", text)
        self.assertIn("## Report 1", text)
        self.assertIn("Answer text two.", text)

    def test_verifier_passes_on_clean_assembly(self):
        patterns = scrub.banned_patterns("cat/some-skill", "some-skill")
        self.assertEqual(scrub.verify_no_leak(self._assemble(), patterns), [])

    def test_verifier_catches_condition_label_in_report(self):
        patterns = scrub.banned_patterns("cat/some-skill", "some-skill")
        text = judge.assemble_input(
            "Frame.", "Prompt.", [{"id": "a", "text": "T."}], None,
            "This is the loaded report.", "Other.",
        )
        hits = scrub.verify_no_leak(text, patterns)
        self.assertTrue(any(h["pattern"] == "condition-word" for h in hits))


if __name__ == "__main__":
    unittest.main()
