"""Scoring math: pass rules, majority votes, unblinding, denominators."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import scoring


def _arm_hits(pairs):
    """pairs: {mh_id: (cold, loaded)} -> scoring input shape."""
    return {m: {"cold": c, "loaded": l} for m, (c, l) in pairs.items()}


class ThresholdTest(unittest.TestCase):
    def test_ceil_two_thirds(self):
        self.assertEqual(scoring.threshold(2), 2)
        self.assertEqual(scoring.threshold(3), 2)
        self.assertEqual(scoring.threshold(4), 3)
        self.assertEqual(scoring.threshold(5), 4)
        self.assertEqual(scoring.threshold(6), 4)


class MajorityTest(unittest.TestCase):
    def test_strict_majority(self):
        self.assertTrue(scoring.majority([True, True, False]))
        self.assertFalse(scoring.majority([True, False]))  # tie is not a majority
        self.assertFalse(scoring.majority([False]))
        self.assertTrue(scoring.majority([True]))

    def test_empty_raises(self):
        with self.assertRaises(scoring.ScoringError):
            scoring.majority([])


class TaskPassRuleTest(unittest.TestCase):
    def test_pass_needs_win_and_threshold(self):
        s = scoring.score_task(
            _arm_hits({"a": (True, True), "b": (False, True), "c": (False, True)}),
            ["a", "b", "c"],
        )
        self.assertEqual((s["cold_hits"], s["loaded_hits"]), (1, 3))
        self.assertTrue(s["pass"])

    def test_tie_fails(self):
        s = scoring.score_task(
            _arm_hits({"a": (True, True), "b": (True, True), "c": (False, False)}),
            ["a", "b", "c"],
        )
        self.assertFalse(s["pass"])
        self.assertFalse(s["regression"])

    def test_win_below_threshold_fails(self):
        # loaded 1 > cold 0 but 1 < ceil(2/3 * 3) = 2
        s = scoring.score_task(
            _arm_hits({"a": (False, True), "b": (False, False), "c": (False, False)}),
            ["a", "b", "c"],
        )
        self.assertFalse(s["pass"])

    def test_regression_flag(self):
        s = scoring.score_task(
            _arm_hits({"a": (True, False), "b": (True, True), "c": (False, False)}),
            ["a", "b", "c"],
        )
        self.assertTrue(s["regression"])
        self.assertFalse(s["pass"])

    def test_missing_expectation_raises(self):
        with self.assertRaises(scoring.ScoringError):
            scoring.score_task(_arm_hits({"a": (True, True)}), ["a", "b"])


class SkillPassRuleTest(unittest.TestCase):
    def _task(self, cold, loaded, n=3):
        return {
            "cold_hits": cold,
            "loaded_hits": loaded,
            "n_must_hits": n,
            "pass": loaded > cold and loaded >= scoring.threshold(n),
            "regression": loaded < cold,
        }

    def test_one_win_no_regression_passes(self):
        s = scoring.score_skill([self._task(1, 3), self._task(2, 2)])
        self.assertTrue(s["pass"])
        self.assertEqual(s["wins"], 1)

    def test_regression_fails_skill_despite_win(self):
        s = scoring.score_skill([self._task(0, 3), self._task(3, 2)])
        self.assertFalse(s["pass"])
        self.assertEqual(s["regressions"], 1)

    def test_no_wins_fails(self):
        s = scoring.score_skill([self._task(2, 2), self._task(1, 1)])
        self.assertFalse(s["pass"])


class UnblindTest(unittest.TestCase):
    def test_unblind_maps_slots_to_arms(self):
        merged = {"a": {"report_1": True, "report_2": False}}
        ub = scoring.unblind(merged, {"report_1": "loaded", "report_2": "cold"})
        self.assertEqual(ub, {"a": {"loaded": True, "cold": False}})

    def test_bad_order_key_raises(self):
        with self.assertRaises(scoring.ScoringError):
            scoring.unblind({}, {"report_1": "cold", "report_2": "cold"})


class MergeJudgeVotesTest(unittest.TestCase):
    def _judgment(self, r1, r2):
        return {
            "expectations": [
                {"expectation_id": "a",
                 "report_1": {"hit": r1, "evidence": ""},
                 "report_2": {"hit": r2, "evidence": ""}}
            ],
            "comparative_verdict": "x",
        }

    def test_majority_across_judges(self):
        merged = scoring.merge_judge_votes(
            [self._judgment(True, False), self._judgment(True, True),
             self._judgment(False, False)]
        )
        self.assertEqual(merged["a"], {"report_1": True, "report_2": False})


def _run_meta(excluded=()):
    return {
        "repeats": 1,
        "judge_repeats": 1,
        "preregistered": True,
        "excluded_tasks": [{"task": t, "reason": "consumer failed"} for t in excluded],
        "tasks": {
            "t1": {"skill": "cat/skill-one", "fixture": "fx", "must_hit_ids": ["a", "b", "c"]},
            "t2": {"skill": "cat/skill-one", "fixture": "fx", "must_hit_ids": ["a", "b"]},
        },
    }


def _judgment_for(hits_1, hits_2, ids):
    return {
        "expectations": [
            {"expectation_id": i,
             "report_1": {"hit": h1, "evidence": "q"},
             "report_2": {"hit": h2, "evidence": "q"}}
            for i, h1, h2 in zip(ids, hits_1, hits_2)
        ],
        "comparative_verdict": "comparable",
    }


ORDER = {"order": {
    "t1": {"report_1": "cold", "report_2": "loaded"},
    "t2": {"report_1": "loaded", "report_2": "cold"},
}}


class DenominatorTest(unittest.TestCase):
    def test_denominator_computed_from_data(self):
        outputs = {
            "t1": [_judgment_for([False, True, False], [True, True, True], ["a", "b", "c"])],
            "t2": [_judgment_for([True, True], [False, True], ["a", "b"])],
        }
        scores = scoring.score_run(_run_meta(), outputs, ORDER)
        agg = scores["aggregate"]
        self.assertEqual(agg["n_expectations"], 5)  # 3 + 2, from the data
        self.assertEqual(agg["cold_hits"], 2)   # t1 cold=1 (r1), t2 cold=1 (r2)
        self.assertEqual(agg["loaded_hits"], 5)  # t1 loaded=3, t2 loaded=2
        self.assertTrue(scores["skills"]["cat/skill-one"]["pass"])

    def test_excluded_task_shrinks_denominator(self):
        outputs = {
            "t1": [_judgment_for([False, True, False], [True, True, True], ["a", "b", "c"])],
        }
        scores = scoring.score_run(_run_meta(excluded=("t2",)), outputs, ORDER)
        self.assertEqual(scores["aggregate"]["n_expectations"], 3)
        self.assertEqual(scores["excluded_tasks"], ["t2"])
        self.assertNotIn("t2", scores["tasks"])

    def test_missing_judge_output_raises(self):
        with self.assertRaises(scoring.ScoringError):
            scoring.score_run(_run_meta(), {"t1": [_judgment_for(
                [False, True, False], [True, True, True], ["a", "b", "c"])]}, ORDER)


class RepeatsTest(unittest.TestCase):
    def test_strict_majority_across_repeats(self):
        meta = {
            "repeats": 3,
            "judge_repeats": 1,
            "excluded_tasks": [],
            "tasks": {"t1": {"skill": "cat/s", "fixture": "fx", "must_hit_ids": ["a", "b"]}},
        }
        order = {"order": {
            "t1-r1": {"report_1": "cold", "report_2": "loaded"},
            "t1-r2": {"report_1": "loaded", "report_2": "cold"},
            "t1-r3": {"report_1": "cold", "report_2": "loaded"},
        }}
        # expectation a: loaded hits in 2/3 repeats -> HIT; cold 1/3 -> MISS
        # expectation b: loaded 1/3 -> MISS; cold 0/3 -> MISS
        outputs = {
            "t1-r1": [_judgment_for([True, False], [True, True], ["a", "b"])],   # cold slot 1
            "t1-r2": [_judgment_for([True, False], [False, False], ["a", "b"])], # loaded slot 1
            "t1-r3": [_judgment_for([False, False], [False, False], ["a", "b"])],
        }
        scores = scoring.score_run(meta, outputs, order)
        t = scores["tasks"]["t1"]
        self.assertEqual(t["per_expectation"]["a"], {"cold": "MISS", "loaded": "HIT"})
        self.assertEqual(t["per_expectation"]["b"], {"cold": "MISS", "loaded": "MISS"})
        self.assertIn("hit_rates", scores)
        self.assertAlmostEqual(scores["hit_rates"]["t1"]["a"]["loaded"], 2 / 3)

    def test_pair_id(self):
        self.assertEqual(scoring.pair_id("t1", 1, 1), "t1")
        self.assertEqual(scoring.pair_id("t1", 2, 3), "t1-r2")


if __name__ == "__main__":
    unittest.main()
