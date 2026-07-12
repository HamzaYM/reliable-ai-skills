"""Codex concordance sample: deterministic hash-parity selection over
committed judge inputs, manifest shape, and the run.py mode wiring."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import concordance


def _make_run(root, run_id, pairs):
    run_dir = Path(root) / run_id
    (run_dir / "judge-inputs").mkdir(parents=True)
    (run_dir / "run-meta.json").write_text(
        json.dumps({"run_id": run_id}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for pid in pairs:
        (run_dir / "judge-inputs" / f"{pid}.json").write_text(
            json.dumps({"pair": pid, "task": pid, "prompt": f"input {pid}",
                        "schema": "eval/schemas/judge.schema.json"},
                       indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return run_dir


class ConcordanceSampleTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        self.run_a = _make_run(self.root, "run-a",
                               [f"task-{i:02d}" for i in range(20)])
        self.run_b = _make_run(self.root, "run-b",
                               [f"other-{i:02d}" for i in range(20)])

    def test_deterministic_across_calls(self):
        m1 = concordance.build_manifest([self.run_a, self.run_b])
        m2 = concordance.build_manifest([self.run_a, self.run_b])
        self.assertEqual(m1, m2)
        # Argument order does not change the selection either.
        m3 = concordance.build_manifest([self.run_b, self.run_a])
        self.assertEqual(m1["selected"], m3["selected"])

    def test_selection_is_even_parity_sorted_by_digest(self):
        manifest = concordance.build_manifest([self.run_a, self.run_b])
        digests = [e["judge_input_sha256"] for e in manifest["selected"]]
        for d in digests:
            self.assertEqual(int(d, 16) % 2, 0, d)
        self.assertEqual(digests, sorted(digests))
        self.assertEqual(manifest["pool_comparisons"], 40)
        expected_kept = 0
        for run_dir in (self.run_a, self.run_b):
            for p in (run_dir / "judge-inputs").glob("*.json"):
                digest = hashlib.sha256(p.read_bytes()).hexdigest()
                expected_kept += 1 - int(digest, 16) % 2
        self.assertEqual(manifest["parity_kept"], expected_kept)

    def test_digest_is_over_committed_file_bytes(self):
        manifest = concordance.build_manifest([self.run_a])
        entry = manifest["selected"][0]
        path = Path(entry["judge_input"])
        if not path.is_absolute():
            path = Path(concordance.REPO_ROOT) / path
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            entry["judge_input_sha256"],
        )

    def test_sample_capped_at_target(self):
        big = _make_run(self.root, "run-big",
                        [f"big-{i:03d}" for i in range(300)])
        manifest = concordance.build_manifest([big], sample_size=50)
        self.assertEqual(manifest["selected_n"], 50)
        self.assertEqual(len(manifest["selected"]), 50)
        self.assertIsNone(manifest["shortfall_note"])

    def test_shortfall_noted_without_backfill(self):
        manifest = concordance.build_manifest([self.run_a], sample_size=50)
        self.assertLess(manifest["selected_n"], 50)
        self.assertEqual(manifest["selected_n"], manifest["parity_kept"])
        self.assertIn("no backfill", manifest["shortfall_note"])

    def test_manifest_fields(self):
        manifest = concordance.build_manifest([self.run_a])
        self.assertIn("SHA-256", manifest["selection_rule"])
        self.assertIn("mod 2 == 0", manifest["selection_rule"])
        self.assertIn("exploratory", manifest["purpose"])
        self.assertIn("never touches any verdict", manifest["purpose"])
        self.assertEqual(manifest["judge_schema"],
                         "eval/schemas/judge.schema.json")
        for entry in manifest["selected"]:
            self.assertEqual(sorted(entry), [
                "judge_input", "judge_input_sha256", "pair", "run_id", "task"
            ])

    def test_duplicate_run_refused(self):
        with self.assertRaises(concordance.ConcordanceError):
            concordance.build_manifest([self.run_a, self.run_a])

    def test_non_run_dir_refused(self):
        empty = Path(self.root) / "not-a-run"
        empty.mkdir()
        with self.assertRaises(concordance.ConcordanceError):
            concordance.build_manifest([empty])

    def test_run_without_judge_inputs_refused(self):
        bare = Path(self.root) / "bare-run"
        bare.mkdir()
        (bare / "run-meta.json").write_text(
            json.dumps({"run_id": "bare-run"}) + "\n", encoding="utf-8"
        )
        with self.assertRaises(concordance.ConcordanceError):
            concordance.build_manifest([bare])


if __name__ == "__main__":
    unittest.main()
