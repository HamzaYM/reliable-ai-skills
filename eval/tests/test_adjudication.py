"""Third-adjudicator path: pinned adjudicator, minimal input, narrow
schema, two-of-three majority with disputed marks kept in denominators,
judge-failure floor (failure only, never disagreement), persistence, and
report/replay integration. Legacy panel and single-judge runs must be
untouched."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run as run_mod
from harness import judge, report, scoring

SONNET = "claude-sonnet-5"
OPUS = "claude-opus-4-8"
FABLE = "claude-fable-5"
ORDER = {"report_1": "cold", "report_2": "loaded"}


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


def _adjudication(pid, marks, task="t1", repeat=1):
    """marks: {(mh, slot): True|False|None (None = adjudicator failed)}."""
    disputes = []
    for (mh, slot), hit in sorted(marks.items()):
        entry = {
            "must_hit": mh,
            "slot": slot,
            "judge_marks": {
                SONNET: {"hit": True, "votes": [{"hit": True, "evidence": "q"}]},
                OPUS: {"hit": False, "votes": [{"hit": False, "evidence": ""}]},
            },
            "rule": scoring.ADJUDICATION_RULE,
        }
        if hit is None:
            entry.update({"adjudicator_mark": None, "final_mark": None,
                          "adjudicator_error": "timed out after 300s"})
        else:
            entry.update({
                "adjudicator_mark": {"hit": hit, "evidence": "q" if hit else ""},
                "final_mark": hit,
            })
        disputes.append(entry)
    return {
        "pair": pid, "task": task, "repeat": repeat,
        "adjudicator_model": FABLE, "adjudicator_effort": "medium",
        "schema": "eval/schemas/adjudicator.schema.json",
        "disputes": disputes,
    }


def _meta(tasks_meta, excluded=()):
    return {
        "run_id": "20260710T000000Z-adj-test",
        "created_at": "2026-07-10T00:00:00Z",
        "model": "claude-fable-5",
        "effort": "low",
        "judge_model": "two-judge panel (see judge_panel)",
        "judge_panel": {
            "models": [SONNET, OPUS],
            "effort": "medium",
            "combination_rule": scoring.ADJUDICATED_UNIT,
        },
        "adjudicator": {
            "model": FABLE,
            "effort": "medium",
            "schema": "eval/schemas/adjudicator.schema.json",
            "rule": scoring.ADJUDICATED_UNIT,
            "floor_rule": scoring.FAILURE_FLOOR_RULE,
        },
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


TASKS_META = {
    "t1": {"skill": "cat/skill-x", "fixture": "fx",
           "must_hit_ids": ["a", "b", "c"]},
}


class PinnedAdjudicatorTest(unittest.TestCase):
    def test_adjudicator_pinned_exact_id_and_effort(self):
        self.assertEqual(judge.ADJUDICATOR_MODEL, "claude-fable-5")
        self.assertEqual(judge.ADJUDICATOR_EFFORT, "medium")

    def test_schema_is_narrow_binary_mark(self):
        schema = json.loads(
            judge.adjudicator_schema_path().read_text(encoding="utf-8")
        )
        self.assertEqual(sorted(schema["required"]), ["evidence", "hit"])
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["hit"]["type"], "boolean")

    def test_cli_schema_payload_strips_dollar_schema(self):
        payload = json.loads(judge.adjudicator_schema_for_cli())
        self.assertNotIn("$schema", payload)
        self.assertIn("hit", payload["properties"])


class AdjudicatorInputTest(unittest.TestCase):
    def test_minimal_input_frame_expectation_and_slots(self):
        text = judge.assemble_adjudicator_input(
            "FRAME TEXT", "states the root cause", "report_2",
            "answers one", "answers two",
        )
        self.assertTrue(text.startswith("FRAME TEXT"))
        self.assertIn("## Disputed expectation", text)
        self.assertIn("states the root cause", text)
        self.assertIn("## Report under dispute: Report 2", text)
        self.assertIn("## Report 1\n\nanswers one", text)
        self.assertIn("## Report 2\n\nanswers two", text)

    def test_unknown_slot_raises(self):
        with self.assertRaises(judge.JudgeError):
            judge.assemble_adjudicator_input("f", "mh", "report_3", "a", "b")

    def test_validate_adjudication_shapes(self):
        self.assertEqual(
            judge.validate_adjudication({"hit": True, "evidence": "q"}),
            {"hit": True, "evidence": "q"},
        )
        for bad in (None, [], {"hit": "yes", "evidence": ""}, {"hit": True}):
            with self.assertRaises(judge.JudgeError):
                judge.validate_adjudication(bad)


class RunAdjudicatorInvocationTest(unittest.TestCase):
    def test_invocation_shape_pinned_and_schema_bound(self):
        captured = {}

        def fake_run_claude(prompt, cwd, model, timeout, extra_args=(),
                            effort=None, max_output_tokens=None,
                            check_model=False):
            captured.update({
                "prompt": prompt, "model": model, "effort": effort,
                "extra_args": extra_args, "check_model": check_model,
            })
            return {
                "result": json.dumps({"hit": True, "evidence": "q"}),
                "modelUsage": {FABLE: {"outputTokens": 10}},
                "usage": {},
            }, 1

        with mock.patch.object(judge, "run_claude", fake_run_claude):
            mark, meta = judge.run_adjudicator("the input", "/tmp/x")
        self.assertEqual(mark, {"hit": True, "evidence": "q"})
        self.assertEqual(captured["model"], "claude-fable-5")
        self.assertEqual(captured["effort"], "medium")
        self.assertTrue(captured["check_model"])
        args = list(captured["extra_args"])
        self.assertIn("--json-schema", args)
        schema = json.loads(args[args.index("--json-schema") + 1])
        self.assertNotIn("$schema", schema)
        self.assertEqual(sorted(schema["required"]), ["evidence", "hit"])
        self.assertEqual(args[args.index("--allowedTools") + 1], "")
        self.assertEqual(meta["model_requested"], "claude-fable-5")
        self.assertEqual(meta["model_effective"], FABLE)
        self.assertEqual(meta["effort_effective"], "medium")


class SlotDisputesTest(unittest.TestCase):
    def test_detects_disputed_report_slots(self):
        per_judge = {
            SONNET: [_judgment([True, False], [True, True], ["a", "b"])],
            OPUS: [_judgment([True, True], [True, False], ["a", "b"])],
        }
        self.assertEqual(
            scoring.slot_disputes(per_judge, ["a", "b"]),
            [("b", "report_1"), ("b", "report_2")],
        )

    def test_no_disputes_when_identical(self):
        per_judge = {
            SONNET: [_judgment([True, False], [True, True], ["a", "b"])],
            OPUS: [_judgment([True, False], [True, True], ["a", "b"])],
        }
        self.assertEqual(scoring.slot_disputes(per_judge, ["a", "b"]), [])

    def test_within_judge_repeat_majority_first(self):
        # Sonnet's votes on b/report_2: HIT, HIT, MISS -> HIT; opus: HIT.
        per_judge = {
            SONNET: [_judgment([True, False], [True, True], ["a", "b"]),
                     _judgment([True, False], [True, True], ["a", "b"]),
                     _judgment([True, False], [True, False], ["a", "b"])],
            OPUS: [_judgment([True, False], [True, True], ["a", "b"])],
        }
        self.assertEqual(scoring.slot_disputes(per_judge, ["a", "b"]), [])

    def test_requires_exactly_two_judges(self):
        with self.assertRaises(scoring.ScoringError):
            scoring.slot_disputes(
                {SONNET: [_judgment([True], [True], ["a"])]}, ["a"]
            )


class PanelAdjudicatedTest(unittest.TestCase):
    def _per_judge(self):
        # Judges agree on a (cold MISS, loaded HIT) and c (both HIT);
        # disagree on b's loaded slot (report_2).
        return {
            SONNET: [_judgment([False, False, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, False, True], [True, False, True],
                             ["a", "b", "c"])],
        }

    def test_majority_resolves_and_keeps_mark_in_denominator(self):
        adjudication = _adjudication("t1", {("b", "report_2"): True})
        resolved, stats = scoring.panel_adjudicated(
            self._per_judge(), adjudication, ORDER, ["a", "b", "c"]
        )
        # All three must-hits stay: the disputed mark never leaves.
        self.assertEqual(sorted(resolved), ["a", "b", "c"])
        self.assertEqual(resolved["b"], {"cold": False, "loaded": True})
        self.assertEqual(stats["disagreed"], ["b"])
        self.assertEqual(stats["failed"], [])
        self.assertEqual(stats["n_disputed_slots"], 1)
        self.assertEqual(stats["n_adjudicated"], 1)
        self.assertEqual(stats["by_slot"], {"report_1": 0, "report_2": 1})
        self.assertEqual(stats["by_arm"], {"cold": 0, "loaded": 1})
        self.assertFalse(stats["floor_excluded"])

    def test_adjudicator_can_side_either_way(self):
        adjudication = _adjudication("t1", {("b", "report_2"): False})
        resolved, _ = scoring.panel_adjudicated(
            self._per_judge(), adjudication, ORDER, ["a", "b", "c"]
        )
        self.assertEqual(resolved["b"], {"cold": False, "loaded": False})

    def test_unresolved_dispute_is_failure_exclusion_not_disagreement(self):
        adjudication = _adjudication("t1", {("b", "report_2"): None})
        resolved, stats = scoring.panel_adjudicated(
            self._per_judge(), adjudication, ORDER, ["a", "b", "c"]
        )
        self.assertEqual(sorted(resolved), ["a", "c"])
        self.assertEqual(stats["failed"], ["b"])
        # 1 of 3 marks failure-excluded: not more than one third, no floor.
        self.assertFalse(stats["floor_excluded"])

    def test_floor_triggers_on_failures_over_one_third(self):
        # a disputed on report_1, b disputed on both slots, c agreed.
        per_judge = {
            SONNET: [_judgment([False, False, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([True, True, True], [True, False, True],
                             ["a", "b", "c"])],
        }
        adjudication = _adjudication("t1", {
            ("a", "report_1"): None,
            ("b", "report_1"): None, ("b", "report_2"): None,
        })
        # Disputes on a and b unresolved: 2 of 3 marks failure-excluded.
        _, stats = scoring.panel_adjudicated(
            per_judge, adjudication, ORDER, ["a", "b", "c"]
        )
        self.assertEqual(stats["failed"], ["a", "b"])
        self.assertTrue(stats["floor_excluded"])

    def test_floor_never_triggers_on_adjudicated_disagreements(self):
        # Every single must-hit disputed, all adjudicated: no floor.
        per_judge = {
            SONNET: [_judgment([True, True, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, False, False], [False, False, False],
                             ["a", "b", "c"])],
        }
        marks = {(m, s): True for m in ("a", "b", "c")
                 for s in ("report_1", "report_2")}
        resolved, stats = scoring.panel_adjudicated(
            per_judge, _adjudication("t1", marks), ORDER, ["a", "b", "c"]
        )
        self.assertEqual(sorted(resolved), ["a", "b", "c"])
        self.assertEqual(stats["disagreed"], ["a", "b", "c"])
        self.assertEqual(stats["failed"], [])
        self.assertFalse(stats["floor_excluded"])

    def test_missing_adjudication_record_counts_as_failure(self):
        _, stats = scoring.panel_adjudicated(
            self._per_judge(), None, ORDER, ["a", "b", "c"]
        )
        self.assertEqual(stats["failed"], ["b"])


class AdjudicatedScoreRunTest(unittest.TestCase):
    def _score(self, outputs, tasks_meta=TASKS_META, excluded=()):
        meta = _meta(tasks_meta, excluded=excluded)
        order_key = {"seed": 5, "order": {pid: ORDER for pid in outputs}}
        return scoring.score_run(meta, outputs, order_key)

    def test_disputed_marks_stay_in_denominator(self):
        outputs = {"t1": {
            SONNET: [_judgment([False, False, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, False, True], [True, False, True],
                             ["a", "b", "c"])],
            "_adjudication": _adjudication("t1", {("b", "report_2"): True}),
        }}
        scores = self._score(outputs)
        t1 = scores["tasks"]["t1"]
        # Denominator stays 3: the disputed mark scored via majority.
        self.assertEqual(t1["n_must_hits"], 3)
        self.assertEqual(t1["cold_hits"], 1)
        self.assertEqual(t1["loaded_hits"], 3)
        self.assertEqual(scores["aggregate"]["n_expectations"], 3)

    def test_rates_published_with_slot_and_arm_breakdown(self):
        outputs = {"t1": {
            SONNET: [_judgment([False, False, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, False, True], [True, False, True],
                             ["a", "b", "c"])],
            "_adjudication": _adjudication("t1", {("b", "report_2"): True}),
        }}
        d = self._score(outputs)["judge_disagreement"]
        self.assertEqual(d["unit"], scoring.ADJUDICATED_UNIT)
        self.assertEqual((d["n_marks"], d["n_disagreed"]), (3, 1))
        self.assertEqual(d["disagreement_rate_pct"], 33.3)
        self.assertEqual(d["by_slot"], {"report_1": 0, "report_2": 1})
        self.assertEqual(d["by_arm"], {"cold": 0, "loaded": 1})
        adj = d["adjudication"]
        self.assertEqual(adj["model"], FABLE)
        self.assertEqual(adj["effort"], "medium")
        self.assertEqual(adj["n_slot_marks"], 6)
        self.assertEqual(adj["n_disputed_slot_marks"], 1)
        self.assertEqual(adj["n_adjudicated"], 1)
        self.assertEqual(adj["n_unresolved"], 0)
        self.assertEqual(adj["adjudication_rate_pct"], 16.7)
        floor = d["failure_floor"]
        self.assertEqual(floor["rule"], scoring.FAILURE_FLOOR_RULE)
        self.assertEqual(floor["floor_excluded_comparisons"], [])

    def test_unresolved_mark_shrinks_denominator_as_failure(self):
        outputs = {"t1": {
            SONNET: [_judgment([False, False, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, False, True], [True, False, True],
                             ["a", "b", "c"])],
            "_adjudication": _adjudication("t1", {("b", "report_2"): None}),
        }}
        scores = self._score(outputs)
        self.assertEqual(scores["tasks"]["t1"]["n_must_hits"], 2)
        d = scores["judge_disagreement"]
        self.assertEqual(d["adjudication"]["n_unresolved"], 1)
        self.assertEqual(
            d["failure_floor"]["failure_excluded_must_hits"], {"t1": ["b"]}
        )
        self.assertEqual(d["failure_floor"]["floor_excluded_comparisons"], [])

    def test_floor_excludes_whole_comparison_and_task(self):
        # Disputes on b (both slots) and c (report_2), all unresolved:
        # 2 of 3 must-hit marks are judge-failure exclusions, which is
        # more than one third, so the entire paired comparison leaves.
        outputs = {"t1": {
            SONNET: [_judgment([False, False, True], [True, True, False],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, True, True], [True, False, True],
                             ["a", "b", "c"])],
            "_adjudication": _adjudication("t1", {
                ("b", "report_1"): None, ("b", "report_2"): None,
                ("c", "report_2"): None,
            }),
        }}
        scores = self._score(outputs)
        d = scores["judge_disagreement"]
        self.assertEqual(d["failure_floor"]["floor_excluded_comparisons"],
                         ["t1"])
        self.assertNotIn("t1", scores["tasks"])
        self.assertIn("t1", scores["excluded_tasks"])
        self.assertEqual(
            d["failure_floor"]["tasks_excluded_no_scorable_marks"], ["t1"]
        )

    def test_legacy_panel_meta_without_adjudicator_unchanged(self):
        meta = _meta(TASKS_META)
        del meta["adjudicator"]
        outputs = {"t1": {
            SONNET: [_judgment([False, False, True], [True, True, True],
                               ["a", "b", "c"])],
            OPUS: [_judgment([False, False, True], [True, False, True],
                             ["a", "b", "c"])],
        }}
        order_key = {"seed": 5, "order": {"t1": ORDER}}
        scores = scoring.score_run(meta, outputs, order_key)
        d = scores["judge_disagreement"]
        self.assertEqual(d["unit"], scoring.AGREEMENT_UNIT)
        self.assertNotIn("adjudication", d)
        self.assertNotIn("failure_floor", d)
        # Pre-adjudicator behavior: the disagreed mark leaves both arms.
        self.assertEqual(scores["tasks"]["t1"]["n_must_hits"], 2)


def _write_adjudicated_run(root, judgments_per_judge, adjudications,
                           tasks_meta=TASKS_META):
    run_dir = Path(root) / "20260710T000000Z-adj-test"
    (run_dir / "judge-outputs").mkdir(parents=True)
    meta = _meta(tasks_meta)
    (run_dir / "run-meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    pids = {pid for j in judgments_per_judge.values() for pid in j}
    order = {"seed": 5, "order": {pid: dict(ORDER) for pid in pids}}
    (run_dir / "order-key.json").write_text(
        json.dumps(order, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for jm, per_pair in judgments_per_judge.items():
        for pid, judgment in per_pair.items():
            run_mod.judge_file(run_dir, pid, jm).write_text(
                json.dumps({"pair": pid, "task": pid, "repeat": 1,
                            "judge_model": jm, "judge_effort": "medium",
                            "judgments": [judgment], "cli_meta": []},
                           indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    for pid, record in adjudications.items():
        run_mod.adjudication_file(run_dir, pid).write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return run_dir


class AdjudicatedRunDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.run_dir = _write_adjudicated_run(self._tmp.name, {
            SONNET: {"t1": _judgment([False, False, True],
                                     [True, True, True], ["a", "b", "c"])},
            OPUS: {"t1": _judgment([False, False, True],
                                   [True, False, True], ["a", "b", "c"])},
        }, {"t1": _adjudication("t1", {("b", "report_2"): True})})

    def test_adjudication_file_naming(self):
        path = run_mod.adjudication_file(Path("/x"), "t1-r2")
        self.assertEqual(str(path), "/x/judge-outputs/t1-r2.adjudication.json")

    def test_load_run_dir_groups_adjudication_under_reserved_key(self):
        _, judge_outputs, _, _, _ = report.load_run_dir(self.run_dir)
        self.assertEqual(sorted(judge_outputs["t1"]),
                         ["_adjudication", OPUS, SONNET])
        self.assertEqual(
            judge_outputs["t1"]["_adjudication"]["adjudicator_model"], FABLE
        )

    def test_report_renders_adjudication_and_persists_evidence(self):
        _, report_text = report.recompute(self.run_dir)
        self.assertIn(
            f"- Adjudicator: {FABLE} (pinned at --effort medium", report_text)
        self.assertIn("1 adjudicated by claude-fable-5 at --effort medium",
                      report_text)
        self.assertIn("kept in every denominator", report_text)
        self.assertIn("two-of-three majority", report_text)
        record = json.loads(
            run_mod.adjudication_file(self.run_dir, "t1")
            .read_text(encoding="utf-8")
        )
        dispute = record["disputes"][0]
        # Both original marks with evidence, the adjudicator mark, and the
        # final majority result are persisted.
        self.assertIn(SONNET, dispute["judge_marks"])
        self.assertIn(OPUS, dispute["judge_marks"])
        self.assertEqual(dispute["adjudicator_mark"]["hit"], True)
        self.assertEqual(dispute["final_mark"], True)

    def test_adjudicated_run_replays_byte_for_byte(self):
        scores_text, report_text = report.recompute(self.run_dir)
        (self.run_dir / "scores.json").write_text(scores_text, encoding="utf-8")
        (self.run_dir / "REPORT.md").write_text(report_text, encoding="utf-8")
        self.assertEqual(report.replay_diff(self.run_dir), [])

    def test_adjudicated_limitation_wording(self):
        _, report_text = report.recompute(self.run_dir)
        self.assertIn("two-of-three\n   majority", report_text)
        self.assertIn("disputed marks never leave any denominator",
                      report_text)

    def test_matrix_propagates_adjudication_rates(self):
        matrix = report.matrix_scores([self.run_dir])
        cell = matrix["cells"]["claude-fable-5@low"]
        adj = cell["judge_disagreement"]["adjudication"]
        self.assertEqual(adj["n_adjudicated"], 1)
        self.assertEqual(adj["n_unresolved"], 0)
        overall = matrix["judge_panel_overall"]
        self.assertEqual(overall["n_disagreed"], 1)
        self.assertEqual(overall["adjudication"]["n_adjudicated"], 1)
        text = report.render_matrix(matrix)
        self.assertIn("report-slot marks adjudicated", text)
        self.assertIn("- Overall: 1 of 3 marks disagreed", text)


class LoadAdjudicationTest(unittest.TestCase):
    def test_missing_torn_and_valid_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t1.adjudication.json"
            self.assertIsNone(run_mod.load_adjudication(path))
            path.write_text("{torn", encoding="utf-8")
            self.assertIsNone(run_mod.load_adjudication(path))
            path.write_text(json.dumps({"pair": "t1"}), encoding="utf-8")
            self.assertIsNone(run_mod.load_adjudication(path))
            record = _adjudication("t1", {("b", "report_2"): True})
            path.write_text(json.dumps(record), encoding="utf-8")
            self.assertEqual(run_mod.load_adjudication(path), record)


class JudgeSlotMarksTest(unittest.TestCase):
    def test_extracts_votes_and_majority(self):
        judgments = [
            _judgment([True], [True], ["a"]),
            _judgment([True], [False], ["a"]),
            _judgment([False], [False], ["a"]),
        ]
        marks = run_mod.judge_slot_marks(judgments, "a", "report_2")
        self.assertFalse(marks["hit"])
        self.assertEqual([v["hit"] for v in marks["votes"]],
                         [True, False, False])
        self.assertEqual(marks["votes"][0]["evidence"], "quote")


if __name__ == "__main__":
    unittest.main()
