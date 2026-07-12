"""Pass rules and aggregation, generalized from the pre-registered protocol.

- Per must-hit: HIT/MISS per arm from the blinded judge (majority vote
  across judge repeats when > 1).
- Per task: PASS if loaded_hits > cold_hits AND
  loaded_hits >= ceil(2/3 * n_must_hits).
- Per skill: PASS if at least one task passes AND no task regresses
  (loaded_hits < cold_hits on any task fails the skill).
- Aggregate: total hits per arm over all included expectations. The
  denominator is always computed from the data, never hand-written.

With --repeats N, a must-hit counts as HIT for an arm when it hits in a
strict majority of repeats.

Two-judge panel runs (judge outputs keyed per judge) apply the
pre-registered agreement rule before any of the above: a must-hit mark
scores only when both judges return identical verdicts for both reports;
disagreed marks are excluded from both arms of that comparison and the
disagreement rate is published (see AGREEMENT_UNIT).

Adjudicated runs (run-meta carries an "adjudicator" block) replace the
exclusion path with a third pinned adjudicator judge: each report-slot
mark the two primary judges disagree on is scored once by the
adjudicator, the final mark is the two-of-three majority, and disputed
marks never leave any denominator (see ADJUDICATED_UNIT). A disputed
mark with no adjudicator result is a judge-failure exclusion, and the
more-than-one-third floor triggers ONLY on such judge-failure
exclusions, never on adjudicated disagreements (see FAILURE_FLOOR_RULE).
"""
import math


class ScoringError(Exception):
    pass


# Pre-registered unit of agreement for the two-judge panel. A "mark" is
# one must-hit's two arm verdicts within one cold-vs-loaded comparison.
AGREEMENT_UNIT = (
    "per must-hit mark: a mark is one must-hit's two arm verdicts within "
    "one cold-vs-loaded comparison; the mark scores only when both judges "
    "return identical HIT/MISS verdicts for both reports, otherwise that "
    "must-hit is excluded from both arms of that comparison and tallied "
    "into the published disagreement rate"
)

# Pre-registered combination rule for adjudicated runs (the three-judge
# path): the exclusion path above is replaced by a pinned adjudicator.
ADJUDICATED_UNIT = (
    "per report-slot must-hit mark: both primary judges score every "
    "blinded comparison fully and independently; each report-slot mark "
    "they disagree on is scored once by the pinned adjudicator, which "
    "sees only the disputed expectation, the two blinded report slots, "
    "and the judging frame; the final mark is the two-of-three majority "
    "and disputed marks never leave any denominator"
)

# How a disputed mark resolves under adjudication.
ADJUDICATION_RULE = (
    "two-of-three majority: the two primary judges' marks plus the "
    "adjudicator's mark; because the primaries split one-to-one on a "
    "disputed mark, the majority equals the adjudicator's mark, and the "
    "mark stays in every denominator"
)

# Judge-failure floor (the FAILURE backstop, never the disagreement
# path): adjudicated disagreements stay in denominators, so the only
# mark-level exclusion left is judge failure (a disputed mark with no
# adjudicator result after the pre-registered retry).
FAILURE_FLOOR_RULE = (
    "a must-hit whose disputed mark has no adjudicator result "
    "(adjudicator failure after the pre-registered retry) is excluded "
    "from both arms of that comparison as a judge-failure exclusion, "
    "never as a disagreement; when more than one third of a comparison's "
    "must-hit marks are excluded this way, the entire paired comparison "
    "is excluded and reported; adjudicated disagreements never trigger "
    "this floor"
)


def threshold(n_must_hits):
    """Minimum loaded hits for a task pass: ceil(2/3 * n)."""
    return math.ceil(2 * n_must_hits / 3)


def majority(bools):
    """Strict majority of a non-empty list of booleans."""
    if not bools:
        raise ScoringError("majority of empty vote set")
    return sum(bool(b) for b in bools) * 2 > len(bools)


def pair_id(task_id, repeat, repeats):
    """Run/judge pair identifier: plain task id unless repeats > 1."""
    return task_id if repeats == 1 else f"{task_id}-r{repeat}"


def merge_judge_votes(judgments):
    """Majority vote per expectation per report slot across judge repeats.

    Returns {expectation_id: {"report_1": bool, "report_2": bool}}.
    """
    votes = {}
    for j in judgments:
        for e in j["expectations"]:
            slot = votes.setdefault(e["expectation_id"], {"report_1": [], "report_2": []})
            slot["report_1"].append(bool(e["report_1"]["hit"]))
            slot["report_2"].append(bool(e["report_2"]["hit"]))
    return {
        eid: {"report_1": majority(v["report_1"]), "report_2": majority(v["report_2"])}
        for eid, v in votes.items()
    }


def unblind(merged, order):
    """Map report slots back to arms using the persisted order key.

    order is {"report_1": "cold"|"loaded", "report_2": ...}.
    Returns {expectation_id: {"cold": bool, "loaded": bool}}.
    """
    if sorted(order.values()) != ["cold", "loaded"]:
        raise ScoringError(f"bad order key entry: {order}")
    return {
        eid: {order["report_1"]: marks["report_1"], order["report_2"]: marks["report_2"]}
        for eid, marks in merged.items()
    }


def panel_agreement(per_judge_judgments, order, must_hit_ids):
    """Apply the two-judge agreement rule to one comparison.

    per_judge_judgments is {judge_model: [judgments...]} for exactly two
    judges (each judge's list is its own repeats; majority within a judge
    first, then cross-judge identity). Returns (agreed, disagreed):
    agreed is {mh_id: {"cold": bool, "loaded": bool}} for the marks both
    judges returned identically, disagreed the sorted mh_ids excluded from
    both arms of this comparison.
    """
    judges = sorted(per_judge_judgments)
    if len(judges) != 2:
        raise ScoringError(
            f"judge panel requires exactly 2 judges per comparison, "
            f"got {judges}"
        )
    unblinded = {}
    for j in judges:
        if not per_judge_judgments[j]:
            raise ScoringError(f"judge {j}: empty judgment list")
        unblinded[j] = unblind(merge_judge_votes(per_judge_judgments[j]), order)
    first, second = (unblinded[j] for j in judges)
    agreed, disagreed = {}, []
    for mh_id in must_hit_ids:
        mark_a, mark_b = first.get(mh_id), second.get(mh_id)
        if mark_a is None or mark_b is None:
            missing = judges[0] if mark_a is None else judges[1]
            raise ScoringError(f"judge {missing} missing expectation {mh_id}")
        if mark_a == mark_b:
            agreed[mh_id] = mark_a
        else:
            disagreed.append(mh_id)
    return agreed, sorted(disagreed)


def _merged_panel_slots(per_judge_judgments, must_hit_ids):
    """Per-judge blinded slot verdicts for exactly two judges.

    Returns (sorted_judge_ids, {judge: {mh_id: {"report_1": bool,
    "report_2": bool}}}) after within-judge repeat majority.
    """
    judges = sorted(per_judge_judgments)
    if len(judges) != 2:
        raise ScoringError(
            f"judge panel requires exactly 2 judges per comparison, "
            f"got {judges}"
        )
    merged = {}
    for j in judges:
        if not per_judge_judgments[j]:
            raise ScoringError(f"judge {j}: empty judgment list")
        merged[j] = merge_judge_votes(per_judge_judgments[j])
    for mh_id in must_hit_ids:
        for j in judges:
            if mh_id not in merged[j]:
                raise ScoringError(f"judge {j} missing expectation {mh_id}")
    return judges, merged


def slot_disputes(per_judge_judgments, must_hit_ids):
    """Report-slot marks the two primary judges disagree on.

    Returns a sorted list of (must_hit_id, slot) pairs, one per disputed
    report-slot mark, computed on the blinded slots (no unblinding is
    needed to detect or adjudicate a dispute).
    """
    judges, merged = _merged_panel_slots(per_judge_judgments, must_hit_ids)
    disputes = []
    for mh_id in must_hit_ids:
        for slot in ("report_1", "report_2"):
            if merged[judges[0]][mh_id][slot] != merged[judges[1]][mh_id][slot]:
                disputes.append((mh_id, slot))
    return sorted(disputes)


def panel_adjudicated(per_judge_judgments, adjudication, order, must_hit_ids):
    """Adjudicated two-of-three resolution of one comparison.

    per_judge_judgments is the two primary judges' judgment lists;
    adjudication is the persisted adjudication record for this pair (or
    None when the pair had nothing to adjudicate), whose "disputes"
    entries carry an "adjudicator_mark" of {"hit": bool, ...} or null on
    adjudicator failure. Returns (resolved, stats): resolved is
    {mh_id: {"cold": bool, "loaded": bool}} with every adjudicated mark
    resolved by two-of-three majority and kept in the denominator; stats
    carries the disagreement, adjudication, failure, and floor bookkeeping
    for this comparison. A must-hit with an unresolved dispute (no
    adjudicator mark) is a judge-failure exclusion, and
    stats["floor_excluded"] is True when more than one third of the
    comparison's must-hit marks are excluded that way.
    """
    if sorted(order.values()) != ["cold", "loaded"]:
        raise ScoringError(f"bad order key entry: {order}")
    judges, merged = _merged_panel_slots(per_judge_judgments, must_hit_ids)
    adj_marks = {}
    for d in (adjudication or {}).get("disputes", []):
        mark = d.get("adjudicator_mark")
        adj_marks[(d.get("must_hit"), d.get("slot"))] = (
            bool(mark.get("hit")) if isinstance(mark, dict) else None
        )
    resolved_slots = {}
    disagreed, failed = [], []
    n_disputed = n_adjudicated = 0
    by_slot = {"report_1": 0, "report_2": 0}
    for mh_id in must_hit_ids:
        marks = {}
        unresolved = False
        for slot in ("report_1", "report_2"):
            a = merged[judges[0]][mh_id][slot]
            b = merged[judges[1]][mh_id][slot]
            if a == b:
                marks[slot] = a
                continue
            n_disputed += 1
            by_slot[slot] += 1
            if mh_id not in disagreed:
                disagreed.append(mh_id)
            final = adj_marks.get((mh_id, slot))
            if final is None:
                unresolved = True
            else:
                # The primaries split one-to-one, so the two-of-three
                # majority equals the adjudicator's mark.
                n_adjudicated += 1
                marks[slot] = final
        if unresolved:
            failed.append(mh_id)
        else:
            resolved_slots[mh_id] = marks
    resolved = {
        mh_id: {order["report_1"]: m["report_1"],
                order["report_2"]: m["report_2"]}
        for mh_id, m in resolved_slots.items()
    }
    stats = {
        "disagreed": sorted(disagreed),
        "failed": sorted(failed),
        "n_slot_marks": 2 * len(must_hit_ids),
        "n_disputed_slots": n_disputed,
        "n_adjudicated": n_adjudicated,
        "by_slot": by_slot,
        "by_arm": {order["report_1"]: by_slot["report_1"],
                   order["report_2"]: by_slot["report_2"]},
        # The floor triggers ONLY on judge-failure exclusions: strictly
        # more than one third of the comparison's must-hit marks.
        "floor_excluded": len(failed) * 3 > len(must_hit_ids),
    }
    return resolved, stats


def score_task(arm_hits_by_expectation, must_hit_ids):
    """arm_hits_by_expectation: {mh_id: {"cold": bool, "loaded": bool}}."""
    missing = [m for m in must_hit_ids if m not in arm_hits_by_expectation]
    if missing:
        raise ScoringError(f"missing expectation results: {missing}")
    n = len(must_hit_ids)
    cold = sum(1 for m in must_hit_ids if arm_hits_by_expectation[m]["cold"])
    loaded = sum(1 for m in must_hit_ids if arm_hits_by_expectation[m]["loaded"])
    thr = threshold(n)
    return {
        "n_must_hits": n,
        "cold_hits": cold,
        "loaded_hits": loaded,
        "threshold": thr,
        "pass": loaded > cold and loaded >= thr,
        "regression": loaded < cold,
        "per_expectation": {
            m: {
                "cold": "HIT" if arm_hits_by_expectation[m]["cold"] else "MISS",
                "loaded": "HIT" if arm_hits_by_expectation[m]["loaded"] else "MISS",
            }
            for m in must_hit_ids
        },
    }


def score_skill(task_scores):
    """task_scores: list of per-task score dicts belonging to one skill."""
    wins = sum(1 for t in task_scores if t["pass"])
    regressions = sum(1 for t in task_scores if t["regression"])
    return {
        "tasks": len(task_scores),
        "wins": wins,
        "regressions": regressions,
        "cold_hits": sum(t["cold_hits"] for t in task_scores),
        "loaded_hits": sum(t["loaded_hits"] for t in task_scores),
        "n_must_hits": sum(t["n_must_hits"] for t in task_scores),
        "pass": wins >= 1 and regressions == 0,
    }


def score_run(run_meta, judge_outputs_by_pair, order_key):
    """Compute the full scores structure from persisted run artifacts.

    run_meta["tasks"] is the tasks snapshot {id: {skill, fixture,
    must_hit_ids, ...}}; excluded tasks are dropped from every denominator.
    """
    repeats = int(run_meta.get("repeats", 1))
    excluded = {e["task"] for e in run_meta.get("excluded_tasks", [])}
    tasks_meta = run_meta["tasks"]
    order = order_key["order"] if "order" in order_key else order_key
    adjudicated = isinstance(run_meta.get("adjudicator"), dict)

    task_scores = {}
    hit_rates = {}
    verdicts = {}
    panel_mode = False
    zero_agreement = []
    disagreement_per_task = {}
    repeat_hits = {}
    floor_excluded_pids = []
    failure_excluded_by_task = {}
    adj_totals = {"slot_marks": 0, "disputed": 0, "adjudicated": 0,
                  "by_slot": {"report_1": 0, "report_2": 0},
                  "by_arm": {"cold": 0, "loaded": 0}}
    for task_id in sorted(tasks_meta):
        if task_id in excluded:
            continue
        meta = tasks_meta[task_id]
        mh_ids = meta["must_hit_ids"]
        per_arm_votes = {m: {"cold": [], "loaded": []} for m in mh_ids}
        pair_verdicts = []
        task_panel = False
        task_marks = 0
        task_disagreed_ids = set()
        task_disagreed_marks = 0
        task_disputed_slots = 0
        task_adjudicated = 0
        for r in range(1, repeats + 1):
            pid = pair_id(task_id, r, repeats)
            judgments = judge_outputs_by_pair.get(pid)
            if not judgments:
                raise ScoringError(f"no judge output for {pid}")
            this_pair = None
            if isinstance(judgments, dict):
                panel_mode = task_panel = True
                per_judge = {k: v for k, v in judgments.items()
                             if not str(k).startswith("_")}
                if adjudicated:
                    # Three-judge path: disputed report-slot marks resolve
                    # by two-of-three majority and stay in denominators;
                    # only judge-failure exclusions can shrink them.
                    resolved, stats = panel_adjudicated(
                        per_judge, judgments.get("_adjudication"),
                        order[pid], mh_ids
                    )
                    task_marks += len(mh_ids)
                    task_disagreed_marks += len(stats["disagreed"])
                    task_disagreed_ids.update(stats["disagreed"])
                    task_disputed_slots += stats["n_disputed_slots"]
                    task_adjudicated += stats["n_adjudicated"]
                    adj_totals["slot_marks"] += stats["n_slot_marks"]
                    adj_totals["disputed"] += stats["n_disputed_slots"]
                    adj_totals["adjudicated"] += stats["n_adjudicated"]
                    for s in ("report_1", "report_2"):
                        adj_totals["by_slot"][s] += stats["by_slot"][s]
                    for a in ("cold", "loaded"):
                        adj_totals["by_arm"][a] += stats["by_arm"][a]
                    if stats["failed"]:
                        failure_excluded_by_task.setdefault(
                            task_id, set()
                        ).update(stats["failed"])
                    pair_verdicts.append(" | ".join(
                        f"{j}: {per_judge[j][0].get('comparative_verdict', '')}"
                        for j in sorted(per_judge)
                    ))
                    if stats["floor_excluded"]:
                        # Judge-failure floor: the whole paired comparison
                        # is excluded and reported.
                        floor_excluded_pids.append(pid)
                        continue
                    this_pair = resolved
                else:
                    # Two-judge panel: per must-hit mark, both judges must
                    # be identical for the mark to score; a disagreed
                    # must-hit leaves both arms of this comparison.
                    agreed, disagreed = panel_agreement(
                        per_judge, order[pid], mh_ids
                    )
                    task_marks += len(mh_ids)
                    task_disagreed_marks += len(disagreed)
                    task_disagreed_ids.update(disagreed)
                    pair_verdicts.append(" | ".join(
                        f"{j}: {per_judge[j][0].get('comparative_verdict', '')}"
                        for j in sorted(per_judge)
                    ))
                    this_pair = agreed
            else:
                merged = merge_judge_votes(judgments)
                ub = unblind(merged, order[pid])
                for m in mh_ids:
                    if m not in ub:
                        raise ScoringError(
                            f"{pid}: judge output missing expectation {m}"
                        )
                pair_verdicts.append(judgments[0].get("comparative_verdict", ""))
                this_pair = ub
            for m in mh_ids:
                if m in this_pair:
                    per_arm_votes[m]["cold"].append(this_pair[m]["cold"])
                    per_arm_votes[m]["loaded"].append(this_pair[m]["loaded"])
            if repeats > 1:
                # Repeat-level values, retained per comparison so endpoint
                # cells can aggregate to mean rates across repeats.
                repeat_hits.setdefault(task_id, {})[r] = {
                    "n_must_hits": len(this_pair),
                    "cold_hits": sum(1 for v in this_pair.values() if v["cold"]),
                    "loaded_hits": sum(1 for v in this_pair.values() if v["loaded"]),
                }
        if task_panel:
            disagreement_per_task[task_id] = {
                "n_marks": task_marks,
                "n_disagreed": task_disagreed_marks,
                "disagreed_must_hits": sorted(task_disagreed_ids),
            }
            if adjudicated:
                disagreement_per_task[task_id].update({
                    "n_disputed_slot_marks": task_disputed_slots,
                    "n_adjudicated": task_adjudicated,
                    "failure_excluded_must_hits": sorted(
                        failure_excluded_by_task.get(task_id, ())
                    ),
                })
        # For panel comparisons a disagreed must-hit contributes no vote;
        # a must-hit with no agreed vote in any repeat leaves the task's
        # denominator entirely (excluded from both arms).
        scoring_ids = [m for m in mh_ids if per_arm_votes[m]["cold"]]
        if not scoring_ids:
            zero_agreement.append(task_id)
            verdicts[task_id] = pair_verdicts
            continue
        arm_hits = {
            m: {"cold": majority(per_arm_votes[m]["cold"]),
                "loaded": majority(per_arm_votes[m]["loaded"])}
            for m in scoring_ids
        }
        score = score_task(arm_hits, scoring_ids)
        score["skill"] = meta["skill"]
        if task_panel:
            score["disagreed_must_hits"] = sorted(task_disagreed_ids)
        task_scores[task_id] = score
        verdicts[task_id] = pair_verdicts
        if repeats > 1:
            hit_rates[task_id] = {
                m: {
                    "cold": sum(v["cold"]) / len(v["cold"]),
                    "loaded": sum(v["loaded"]) / len(v["loaded"]),
                }
                for m, v in per_arm_votes.items() if v["cold"]
            }

    skills = {}
    for skill in sorted({s["skill"] for s in task_scores.values()}):
        skills[skill] = score_skill(
            [s for s in task_scores.values() if s["skill"] == skill]
        )

    n_expectations = sum(s["n_must_hits"] for s in task_scores.values())
    cold_total = sum(s["cold_hits"] for s in task_scores.values())
    loaded_total = sum(s["loaded_hits"] for s in task_scores.values())
    scores = {
        "preregistered": bool(run_meta.get("preregistered")),
        "repeats": repeats,
        "judge_repeats": int(run_meta.get("judge_repeats", 1)),
        "tasks": task_scores,
        "skills": skills,
        "comparative_verdicts": verdicts,
        "excluded_tasks": sorted(excluded | set(zero_agreement)),
        "aggregate": {
            "n_expectations": n_expectations,
            "cold_hits": cold_total,
            "loaded_hits": loaded_total,
            "cold_pct": round(100 * cold_total / n_expectations, 1) if n_expectations else None,
            "loaded_pct": round(100 * loaded_total / n_expectations, 1) if n_expectations else None,
        },
    }
    if panel_mode:
        # Published disagreement rate for the two-judge panel: only added
        # for panel runs so legacy single-judge runs replay byte-for-byte.
        n_marks = sum(d["n_marks"] for d in disagreement_per_task.values())
        n_disagreed = sum(
            d["n_disagreed"] for d in disagreement_per_task.values()
        )
        scores["judge_disagreement"] = {
            "unit": ADJUDICATED_UNIT if adjudicated else AGREEMENT_UNIT,
            "n_marks": n_marks,
            "n_disagreed": n_disagreed,
            "disagreement_rate_pct": (
                round(100 * n_disagreed / n_marks, 1) if n_marks else None
            ),
            "per_task": disagreement_per_task,
        }
        if adjudicated:
            adj_meta = run_meta.get("adjudicator") or {}
            scores["judge_disagreement"].update({
                "by_slot": adj_totals["by_slot"],
                "by_arm": adj_totals["by_arm"],
                "adjudication": {
                    "model": adj_meta.get("model"),
                    "effort": adj_meta.get("effort"),
                    "rule": ADJUDICATION_RULE,
                    "n_slot_marks": adj_totals["slot_marks"],
                    "n_disputed_slot_marks": adj_totals["disputed"],
                    "n_adjudicated": adj_totals["adjudicated"],
                    "n_unresolved": (adj_totals["disputed"]
                                     - adj_totals["adjudicated"]),
                    "adjudication_rate_pct": (
                        round(100 * adj_totals["adjudicated"]
                              / adj_totals["slot_marks"], 1)
                        if adj_totals["slot_marks"] else None
                    ),
                },
                "failure_floor": {
                    "rule": FAILURE_FLOOR_RULE,
                    "failure_excluded_must_hits": {
                        t: sorted(v)
                        for t, v in sorted(failure_excluded_by_task.items())
                    },
                    "floor_excluded_comparisons": sorted(floor_excluded_pids),
                    "tasks_excluded_no_scorable_marks": sorted(zero_agreement),
                },
            })
        else:
            scores["judge_disagreement"]["tasks_excluded_zero_agreement"] = (
                sorted(zero_agreement)
            )
    if hit_rates:
        scores["hit_rates"] = hit_rates
    if repeats > 1:
        # Repeat-level aggregates plus their mean: endpoint cells run at
        # --repeats N and their verdict-facing rates are the means over
        # repeats, with the repeat-level values retained here.
        per_repeat = {}
        for rr in range(1, repeats + 1):
            tasks_r = {
                tid: repeat_hits[tid][rr]
                for tid in sorted(task_scores)
                if tid in repeat_hits and rr in repeat_hits[tid]
            }
            n = sum(t["n_must_hits"] for t in tasks_r.values())
            cold = sum(t["cold_hits"] for t in tasks_r.values())
            loaded = sum(t["loaded_hits"] for t in tasks_r.values())
            per_repeat[f"r{rr}"] = {
                "tasks": tasks_r,
                "n_expectations": n,
                "cold_hits": cold,
                "loaded_hits": loaded,
                "cold_rate_pct": round(100 * cold / n, 1) if n else None,
                "loaded_rate_pct": round(100 * loaded / n, 1) if n else None,
                "delta_pp": round(100 * (loaded - cold) / n, 1) if n else None,
            }
        valid = [b for b in per_repeat.values() if b["n_expectations"]]
        mean = {
            key: (round(sum(b[key] for b in valid) / len(valid), 1)
                  if valid else None)
            for key in ("cold_rate_pct", "loaded_rate_pct", "delta_pp")
        }
        scores["repeats_detail"] = {
            "per_repeat": per_repeat,
            "mean_over_repeats": mean,
            "note": (
                "replicated cell: endpoint verdicts use the mean rates "
                "over repeats; repeat-level values are retained above, and "
                "every repeat ran in its own isolated workspace with no "
                "shared session state"
            ),
        }
    return scores
