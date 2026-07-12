"""Replay determinism: scores.json and REPORT.md must reproduce
byte-for-byte from a run directory's raw judge outputs."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import report


def _judgment(hits_1, hits_2, ids):
    return {
        "expectations": [
            {"expectation_id": i,
             "report_1": {"hit": h1, "evidence": "quote"},
             "report_2": {"hit": h2, "evidence": "quote"}}
            for i, h1, h2 in zip(ids, hits_1, hits_2)
        ],
        "comparative_verdict": "Report 2 answered the task better overall.",
    }


def _make_run_dir(root):
    run_dir = Path(root) / "20260709T000000Z-test"
    (run_dir / "judge-outputs").mkdir(parents=True)
    meta = {
        "run_id": run_dir.name,
        "created_at": "2026-07-09T00:00:00Z",
        "model": "sonnet",
        "judge_model": "sonnet",
        "claude_cli_version": "2.1.x (test)",
        "seed": 99,
        "repeats": 1,
        "judge_repeats": 1,
        "preregistered": True,
        "freeze": {"frozen_at": "2026-07-08T00:00:00Z", "task_file_sha256": "ab" * 32},
        "excluded_tasks": [{"task": "t3", "reason": "consumer failed twice"}],
        "workspace_mutation_warnings": [],
        "wall_clock_seconds": 12.5,
        "tasks": {
            "t1": {"skill": "cat/skill-x", "fixture": "fx", "must_hit_ids": ["a", "b", "c"]},
            "t2": {"skill": "cat/skill-x", "fixture": "fx", "must_hit_ids": ["a", "b"]},
            "t3": {"skill": "cat/skill-y", "fixture": "fx", "must_hit_ids": ["a", "b"]},
        },
    }
    (run_dir / "run-meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    order = {"seed": 99, "order": {
        "t1": {"report_1": "loaded", "report_2": "cold"},
        "t2": {"report_1": "cold", "report_2": "loaded"},
        "t3": {"report_1": "cold", "report_2": "loaded"},
    }}
    (run_dir / "order-key.json").write_text(
        json.dumps(order, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    outputs = {
        "t1": _judgment([True, True, True], [False, True, False], ["a", "b", "c"]),
        "t2": _judgment([True, False], [True, True], ["a", "b"]),
    }
    for pid, j in outputs.items():
        (run_dir / "judge-outputs" / f"{pid}.json").write_text(
            json.dumps({"pair": pid, "judgments": [j]}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    (run_dir / "comprehension.json").write_text(
        json.dumps({"t1": [{"skill_read": True, "evidence": "read the file"}],
                    "t2": [{"skill_read": True, "evidence": "read the file"}]},
                   indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "scrub-manifest.json").write_text(
        json.dumps({"substitutions": []}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return run_dir


class ReplayTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.run_dir = _make_run_dir(self._tmp.name)
        scores_text, report_text = report.recompute(self.run_dir)
        (self.run_dir / "scores.json").write_text(scores_text, encoding="utf-8")
        (self.run_dir / "REPORT.md").write_text(report_text, encoding="utf-8")

    def test_recompute_is_deterministic(self):
        a = report.recompute(self.run_dir)
        b = report.recompute(self.run_dir)
        self.assertEqual(a, b)

    def test_replay_clean_on_untouched_run(self):
        self.assertEqual(report.replay_diff(self.run_dir), [])

    def test_scores_content(self):
        scores = json.loads((self.run_dir / "scores.json").read_text(encoding="utf-8"))
        # t1: order maps report_1 -> loaded: loaded (T,T,T)=3, cold (F,T,F)=1: PASS
        self.assertTrue(scores["tasks"]["t1"]["pass"])
        # t2: report_1 -> cold: cold (T,F)=1, loaded (T,T)=2, threshold 2: PASS
        self.assertTrue(scores["tasks"]["t2"]["pass"])
        self.assertTrue(scores["skills"]["cat/skill-x"]["pass"])
        # denominator excludes the excluded task t3 (3 + 2, not + 2 more)
        self.assertEqual(scores["aggregate"]["n_expectations"], 5)
        self.assertEqual(scores["excluded_tasks"], ["t3"])
        # t3's skill never scored
        self.assertNotIn("cat/skill-y", scores["skills"])

    def test_tampered_scores_detected(self):
        path = self.run_dir / "scores.json"
        scores = json.loads(path.read_text(encoding="utf-8"))
        scores["aggregate"]["loaded_hits"] += 1  # cook the books
        path.write_text(json.dumps(scores, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        errs = report.replay_diff(self.run_dir)
        self.assertTrue(any("scores.json" in e for e in errs))

    def test_tampered_judge_output_detected(self):
        jpath = self.run_dir / "judge-outputs" / "t2.json"
        data = json.loads(jpath.read_text(encoding="utf-8"))
        data["judgments"][0]["expectations"][0]["report_1"]["hit"] = False
        jpath.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
        errs = report.replay_diff(self.run_dir)
        self.assertTrue(errs)

    def test_missing_committed_files_detected(self):
        (self.run_dir / "REPORT.md").unlink()
        errs = report.replay_diff(self.run_dir)
        self.assertTrue(any("missing REPORT.md" in e for e in errs))

    def test_report_mentions_exclusions_and_denominator(self):
        text = (self.run_dir / "REPORT.md").read_text(encoding="utf-8")
        self.assertIn("Excluded tasks: t3", text)
        self.assertIn("/5", text)  # data-computed denominator in aggregate


if __name__ == "__main__":
    unittest.main()
