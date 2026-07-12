"""Two-judge panel: pinned IDs, per must-hit agreement rule, disagreement
rate publication, per-judge file grouping and resumability, and panel
report rendering (legacy single-judge runs must be untouched)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run as run_mod
from harness import judge, report, scoring

SONNET = "claude-sonnet-5"
OPUS = "claude-opus-4-8"


def _judgment(hits_1, hits_2, ids, verdict="Report 2 was stronger."):
    return {
        "expectations": [
            {"expectation_id": i,
             "report_1": {"hit": h1, "evidence": "quote"},
             "report_2": {"hit": h2, "evidence": "quote"}}
            for i, h1, h2 in zip(ids, hits_1, hits_2)
        ],
        "comparative_verdict": verdict,
    }


ORDER = {"report_1": "cold", "report_2": "loaded"}


def _meta(tasks_meta, judge_panel=True, excluded=()):
    meta = {
        "run_id": "20260710T000000Z-panel-test",
        "created_at": "2026-07-10T00:00:00Z",
        "model": "claude-fable-5",
        "effort": "low",
        "judge_model": "two-judge panel (see judge_panel)",
        "claude_cli_version": "2.1.206 (test)",
        "seed": 5,
        "repeats": 1,
        "judge_repeats": 1,
        "preregistered": True,
        "freeze": {"frozen_at": "2026-07-09T00:00:00Z",
                   "task_file_sha256": "cd" * 32},
        "excluded_tasks": [{"task": t, "reason": "consumer failed"}
                           for t in excluded],
        "workspace_mutation_warnings": [],
        "wall_clock_seconds": 10.0,
        "tasks": tasks_meta,
    }
    if judge_panel:
        meta["judge_panel"] = {
            "models": [SONNET, OPUS],
            "effort": "medium",
            "combination_rule": scoring.AGREEMENT_UNIT,
            "judges": {
                SONNET: {"model_requested": SONNET,
                         "models_effective": [SONNET],
                         "effort_requested": "medium",
                         "effort_effective": "medium"},
                OPUS: {"model_requested": OPUS,
                       "models_effective": [OPUS],
                       "effort_requested": "medium",
                       "effort_effective": "medium"},
            },
        }
    return meta


TASKS_META = {
    "t1": {"skill": "cat/skill-x", "fixture": "fx",
           "must_hit_ids": ["a", "b", "c"]},
}


class PinnedPanelTest(unittest.TestCase):
    def test_panel_ids_are_exact_full_model_ids(self):
        # Full IDs, not aliases: alias drift in a future CLI cannot move a
        # judge, and cross-model fallback checks against an exact string.
        self.assertEqual(judge.JUDGE_PANEL, (SONNET, OPUS))
        for jm in judge.JUDGE_PANEL:
            self.assertTrue(jm.startswith("claude-"), jm)

    def test_panel_effort_pinned_medium(self):
        self.assertEqual(judge.JUDGE_EFFORT, "medium")


class PanelAgreementTest(unittest.TestCase):
    def test_identical_marks_score(self):
        per_judge = {
            SONNET: [_judgment([True, False], [True, True], ["a", "b"])],
            OPUS: [_judgment([True, False], [True, True], ["a", "b"])],
        }
        agreed, disagreed = scoring.panel_agreement(per_judge, ORDER, ["a", "b"])
        self.assertEqual(disagreed, [])
        self.assertEqual(agreed["a"], {"cold": True, "loaded": True})
        self.assertEqual(agreed["b"], {"cold": False, "loaded": True})

    def test_one_slot_difference_excludes_the_must_hit(self):
        per_judge = {
            SONNET: [_judgment([True, False], [True, True], ["a", "b"])],
            OPUS: [_judgment([True, False], [True, False], ["a", "b"])],
        }
        agreed, disagreed = scoring.panel_agreement(per_judge, ORDER, ["a", "b"])
        self.assertEqual(disagreed, ["b"])
        self.assertEqual(sorted(agreed), ["a"])

    def test_needs_exactly_two_judges(self):
        with self.assertRaises(scoring.ScoringError):
            scoring.panel_agreement(
                {SONNET: [_judgment([True], [True], ["a"])]}, ORDER, ["a"]
            )
        with self.assertRaises(scoring.ScoringError):
            scoring.panel_agreement(
                {SONNET: [_judgment([True], [True], ["a"])],
                 OPUS: [_judgment([True], [True], ["a"])],
                 "third": [_judgment([True], [True], ["a"])]},
                ORDER, ["a"],
            )

    def test_missing_expectation_raises(self):
        per_judge = {
            SONNET: [_judgment([True], [True], ["a"])],
            OPUS: [_judgment([True], [True], ["a"])],
        }
        with self.assertRaises(scoring.ScoringError):
            scoring.panel_agreement(per_judge, ORDER, ["a", "b"])

    def test_within_judge_repeats_majority_then_cross_judge_identity(self):
        # Sonnet votes b: MISS, MISS, HIT -> MISS; opus votes b: MISS.
        per_judge = {
            SONNET: [_judgment([True, False], [True, False], ["a", "b"]),
                     _judgment([True, False], [True, False], ["a", "b"]),
                     _judgment([True, True], [True, True], ["a", "b"])],
            OPUS: [_judgment([True, False], [True, False], ["a", "b"])],
        }
        agreed, disagreed = scoring.panel_agreement(per_judge, ORDER, ["a", "b"])
        self.assertEqual(disagreed, [])
        self.assertEqual(agreed["b"], {"cold": False, "loaded": False})


class PanelScoreRunTest(unittest.TestCase):
    def _score(self, outputs, tasks_meta=TASKS_META, excluded=()):
        meta = _meta(tasks_meta, excluded=excluded)
        order_key = {"seed": 5, "order": {pid: ORDER for pid in outputs}}
        return scoring.score_run(meta, outputs, order_key)

    def test_agreed_marks_score_and_disagreed_leave_both_arms(self):
        outputs = {"t1": {
            # Judges agree on a (cold MISS, loaded HIT) and c (both HIT),
            # disagree on b's loaded slot.
            SONNET: [_judgment([False, False, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, False, True], [True, False, True],
                             ["a", "b", "c"])],
        }}
        scores = self._score(outputs)
        t1 = scores["tasks"]["t1"]
        # b excluded from BOTH arms: denominator 2, not 3.
        self.assertEqual(t1["n_must_hits"], 2)
        self.assertEqual(t1["cold_hits"], 1)
        self.assertEqual(t1["loaded_hits"], 2)
        self.assertEqual(t1["disagreed_must_hits"], ["b"])
        self.assertEqual(sorted(t1["per_expectation"]), ["a", "c"])
        agg = scores["aggregate"]
        self.assertEqual(agg["n_expectations"], 2)

    def test_disagreement_rate_published(self):
        outputs = {"t1": {
            SONNET: [_judgment([False, False, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, False, True], [True, False, True],
                             ["a", "b", "c"])],
        }}
        scores = self._score(outputs)
        d = scores["judge_disagreement"]
        self.assertEqual(d["n_marks"], 3)
        self.assertEqual(d["n_disagreed"], 1)
        self.assertEqual(d["disagreement_rate_pct"], 33.3)
        self.assertEqual(d["per_task"]["t1"]["disagreed_must_hits"], ["b"])
        self.assertEqual(d["unit"], scoring.AGREEMENT_UNIT)
        self.assertEqual(d["tasks_excluded_zero_agreement"], [])

    def test_full_agreement_rate_zero(self):
        outputs = {"t1": {
            SONNET: [_judgment([False, True, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, True, True], [True, True, True],
                             ["a", "b", "c"])],
        }}
        scores = self._score(outputs)
        d = scores["judge_disagreement"]
        self.assertEqual((d["n_marks"], d["n_disagreed"]), (3, 0))
        self.assertEqual(d["disagreement_rate_pct"], 0.0)
        self.assertEqual(scores["tasks"]["t1"]["n_must_hits"], 3)

    def test_zero_agreement_task_is_excluded_and_listed(self):
        outputs = {"t1": {
            SONNET: [_judgment([True, True, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, False, False], [False, False, False],
                             ["a", "b", "c"])],
        }}
        scores = self._score(outputs)
        self.assertNotIn("t1", scores["tasks"])
        self.assertIn("t1", scores["excluded_tasks"])
        d = scores["judge_disagreement"]
        self.assertEqual(d["tasks_excluded_zero_agreement"], ["t1"])
        self.assertEqual(d["n_disagreed"], 3)

    def test_comparative_verdicts_carry_both_judges(self):
        outputs = {"t1": {
            SONNET: [_judgment([False, True, True], [True, True, True],
                               ["a", "b", "c"], verdict="sonnet view")],
            OPUS: [_judgment([False, True, True], [True, True, True],
                             ["a", "b", "c"], verdict="opus view")],
        }}
        scores = self._score(outputs)
        verdict = scores["comparative_verdicts"]["t1"][0]
        self.assertIn(f"{OPUS}: opus view", verdict)
        self.assertIn(f"{SONNET}: sonnet view", verdict)

    def test_legacy_single_judge_runs_score_unchanged(self):
        # Legacy shape (list of judgments) must not gain any panel keys.
        meta = _meta(TASKS_META, judge_panel=False)
        meta["judge_model"] = "sonnet"
        outputs = {"t1": [_judgment([False, True, True], [True, True, True],
                                    ["a", "b", "c"])]}
        order_key = {"seed": 5, "order": {"t1": ORDER}}
        scores = scoring.score_run(meta, outputs, order_key)
        self.assertNotIn("judge_disagreement", scores)
        self.assertNotIn("disagreed_must_hits", scores["tasks"]["t1"])
        self.assertEqual(scores["tasks"]["t1"]["n_must_hits"], 3)


def _write_panel_run(root, outputs_per_judge, tasks_meta=TASKS_META,
                     excluded=()):
    """A completed panel run dir with per-judge judge-output files."""
    run_dir = Path(root) / "20260710T000000Z-panel-test"
    (run_dir / "judge-outputs").mkdir(parents=True)
    meta = _meta(tasks_meta, excluded=excluded)
    (run_dir / "run-meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    pids = {pid for j in outputs_per_judge.values() for pid in j}
    order = {"seed": 5, "order": {pid: dict(ORDER) for pid in pids}}
    (run_dir / "order-key.json").write_text(
        json.dumps(order, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for jm, per_pair in outputs_per_judge.items():
        for pid, judgment in per_pair.items():
            path = run_mod.judge_file(run_dir, pid, jm)
            path.write_text(
                json.dumps({"pair": pid, "judge_model": jm,
                            "judge_effort": "medium",
                            "judgments": [judgment], "cli_meta": []},
                           indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    return run_dir


class PanelRunDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.run_dir = _write_panel_run(self._tmp.name, {
            SONNET: {"t1": _judgment([False, False, True], [True, True, True],
                                     ["a", "b", "c"])},
            OPUS: {"t1": _judgment([False, False, True], [True, False, True],
                                   ["a", "b", "c"])},
        })

    def test_load_run_dir_groups_per_judge_files(self):
        _, judge_outputs, _, _, _ = report.load_run_dir(self.run_dir)
        self.assertEqual(sorted(judge_outputs), ["t1"])
        self.assertEqual(sorted(judge_outputs["t1"]), [OPUS, SONNET])

    def test_report_renders_panel_and_disagreement(self):
        _, report_text = report.recompute(self.run_dir)
        self.assertIn(
            f"- Judge panel: {SONNET} + {OPUS} (both pinned at --effort "
            f"medium)", report_text)
        self.assertIn("Judge panel disagreement: 1 of 3 marks (33.3%)",
                      report_text)
        self.assertIn("Agreement unit: per must-hit mark", report_text)
        self.assertIn("Judge panel disagreed (excluded from both arms): b",
                      report_text)
        # Panel runs carry the two-judge limitation wording.
        self.assertIn("Same-vendor judging", report_text)
        self.assertNotIn("Same-family judging", report_text)

    def test_panel_run_replays_byte_for_byte(self):
        scores_text, report_text = report.recompute(self.run_dir)
        (self.run_dir / "scores.json").write_text(scores_text, encoding="utf-8")
        (self.run_dir / "REPORT.md").write_text(report_text, encoding="utf-8")
        self.assertEqual(report.replay_diff(self.run_dir), [])

    def test_resume_pending_is_per_judge(self):
        # One judge's file exists; only the other judge should be missing.
        # judge_file naming keeps the two separable on disk.
        sonnet_file = run_mod.judge_file(self.run_dir, "t1", SONNET)
        opus_file = run_mod.judge_file(self.run_dir, "t1", OPUS)
        self.assertTrue(sonnet_file.is_file())
        self.assertTrue(opus_file.is_file())
        self.assertNotEqual(sonnet_file, opus_file)
        opus_file.unlink()
        _, judge_outputs, _, _, _ = report.load_run_dir(self.run_dir)
        self.assertEqual(sorted(judge_outputs["t1"]), [SONNET])


class ZeroAgreementReportTest(unittest.TestCase):
    def test_zero_agreement_note_in_run_notes(self):
        with tempfile.TemporaryDirectory() as root:
            run_dir = _write_panel_run(root, {
                SONNET: {"t1": _judgment([True, True, True],
                                         [True, True, True], ["a", "b", "c"])},
                OPUS: {"t1": _judgment([False, False, False],
                                       [False, False, False], ["a", "b", "c"])},
            })
            _, report_text = report.recompute(run_dir)
        self.assertIn("Tasks excluded by judge-panel zero agreement", report_text)
        self.assertIn("- Excluded tasks: t1", report_text)


class JudgeFileNamingTest(unittest.TestCase):
    def test_judge_slug_sanitizes(self):
        self.assertEqual(run_mod.judge_slug("claude-sonnet-5"),
                         "claude-sonnet-5")
        self.assertEqual(run_mod.judge_slug("org/judge:v1"), "org-judge-v1")

    def test_judge_file_path(self):
        path = run_mod.judge_file(Path("/x"), "t1-r2", OPUS)
        self.assertEqual(
            str(path), f"/x/judge-outputs/t1-r2.{OPUS}.json"
        )


if __name__ == "__main__":
    unittest.main()
