# A/B eval report: lattice-fable-low

- Consumer model: claude-fable-5
- Consumer effort: low
- Consumer models effective: claude-fable-5, claude-haiku-4-5-20251001, claude-opus-4-8[1m], claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 7696983902437800397
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 366.4 s

## Aggregate

Cold 65/68 (95.6%) | Loaded 68/68 (100.0%) | Delta +3

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 9 of 204 must-hit marks (4.4%) carried a disputed report slot.

Adjudication: 10 of 408 report-slot marks disputed; 10 adjudicated by claude-fable-5 at --effort medium (2.5% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 2, report_2 8; by arm: cold 7, loaded 3.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 64/68 (94.1%) | 66/68 (97.1%) | +2.9 |
| r2 | 65/68 (95.6%) | 68/68 (100.0%) | +4.4 |
| r3 | 63/68 (92.6%) | 68/68 (100.0%) | +7.4 |

Endpoint mean over repeats: cold 94.1% | loaded 99.0% | delta +4.9 pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 2/3 | 3/3 | +1 | PASS |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 4/4 | 4/4 | +0 | FAIL |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 5/5 | 5/5 | +0 | FAIL |
| campaign-execution/multi-agent-batch-campaigns | 1 | 3/4 | 4/4 | +1 | PASS |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/consent-and-regulated-data-reference | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/docs-of-record-and-arbitration | 1 | 4/4 | 4/4 | +0 | FAIL |
| evals-and-scoring/llm-eval-harness-and-scoring-pipeline | 1 | 3/4 | 4/4 | +1 | PASS |
| tiered-review/tiered-consultancy-review | 1 | 5/5 | 5/5 | +0 | FAIL |
| validation-gates/pre-merge-validation-gate | 1 | 4/4 | 4/4 | +0 | FAIL |

## Per-task must-hits

### aicg-t2 (cost-and-safety-guardrails/ai-cost-tracking-and-guardrails)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with correct file/function citations and concrete fixes; they are comparable in quality. | claude-sonnet-5: Both reports hit all four expectations with concrete, correct fixes; Report 2 is slightly crisper and more direct on the rate-limiter fail-closed fix, but overall the two are comparable in substance and coverage.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations; Report 2 is marginally stronger on the same-commit doc rule and source-of-truth framing, but they are effectively comparable. | claude-sonnet-5: Both reports hit all four expectations with near-identical substance; Report 2 adds a bit more supporting detail (README as authority, test coverage gap) but this doesn't change expectation coverage — the two are comparable in quality.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are near-identical and strong on a–c, but Report 1 additionally flags the snapshot's staleness and commits to re-checking live limits, making it slightly better. | claude-sonnet-5: Report 1 is slightly better: it explicitly notes the usage snapshot is ~3 hours stale and commits to re-checking live usage before launch (expectation d), which Report 2 omits entirely despite citing the same snapshot timestamp.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent substance and correct citations; they are comparable, with Report 1 marginally more detailed. | claude-sonnet-5: Both reports are substantively equivalent and hit all four expectations with accurate, well-cited evidence; Report 1 is slightly more explicit in flatly refusing the shared-table write ("do not do it") while Report 2 gives marginally more actionable test-harness detail (referencing tests/test_jobs.py), but neither is clearly superior overall.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations; Report 2 is marginally stronger on the global-gate point by confirming nothing exists in infra, but they are comparable. | claude-sonnet-5: Both reports hit all four expectations with substantively equivalent findings; Report 2 is slightly more concrete on point (d) (specific env var, infra file check) but the difference is marginal.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations; Report 1 is marginally stronger by flagging the AI-assistance footer for removal firmly rather than hedging as Report 2 does. | claude-sonnet-5: Report 1 answers the task better overall — it matches Report 2 on expectations (a), (b), and (c), but clearly flags the AI-assistance footer as something that must be removed (d), whereas Report 2 hedges and defers to the document owner instead of stating removal is required.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully satisfy all three expectations with correct file-level grounding; they are comparable, with Report 1 slightly more detailed on go-forward automation but Report 2 equally complete. | claude-sonnet-5: Both reports hit all three expectations with essentially equivalent substance; Report 2 adds a bit more nuance (GRANT/default-privileges ordering, SET LOCAL suggestion) but this is extra credit beyond what's required.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly equivalent, but Report 1 also arrives at the required distinction that relevance/tone failures can defensibly be scored over surviving axes while accuracy cannot, giving it the edge. | claude-sonnet-5: Both reports correctly diagnose the None→0.0 substitution bug and its corrupting effect on scores.csv/leaderboard.py, but only Report 1 explicitly draws the required distinction that a relevance/tone failure can defensibly be handled by renormalizing over the succeeded axes while an accuracy (gate) failure cannot be scored at all — Report 2 treats all axis failures uniformly ("On any axis failure, the pipeline should not write a numeric composite for that row"), making Report 1 the stronger, more complete answer.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully satisfy all four expectations with equivalent grounding in the git history and code; they are comparable. | claude-sonnet-5: Both reports are substantively equivalent, hitting the same three expectations (a, b, d) and missing the same one (c); Report 2 is slightly more precise (e.g., explicitly citing `git show 1712565` and noting reports.py's direct dependency on the module-level engine) but the difference is marginal.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both nail all four points; Report 2 is marginally more rigorous by checking freshness against origin/main with an explicit ancestry test. | claude-sonnet-5: Both reports hit all four expectations with comparable rigor; Report 2 is marginally more explicit about fetch freshness and ancestry verification, but the two are essentially equivalent in substance.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and comparable on grouping, ordering, and the F-06 escalation, but Report 1 answers the task better because it identifies the shared results-database collision in tests/conftest.py as a concrete parallelism hazard requiring a per-engineer RESULTS_DB override, whereas Report 2 treats it only as an optional path/writability preference. | claude-sonnet-5: Both reports are similar in structure and quality; Report 1 is stronger on expectation (d), explicitly identifying the shared RESULTS_DB default as a concurrency-corruption risk and requiring an override, while Report 2 only mentions RESULTS_DB as an optional setup step without connecting it to collision risk.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 2/3, loaded 3/3, threshold 2: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | MISS | HIT |
| c | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: The two reports are essentially comparable: both nail the cross-tenant leak and both correctly defuse the raw-SQL string as non-exploitable, and both miss the broken nightly_export caller in exports.py; Report 2 is marginally stronger only for its independent non-LLM verification step. | claude-sonnet-5: Both reports correctly identify the cross-tenant leak (a) and correctly avoid over-flagging the SQL string as exploitable injection (c); neither caught the exports.py/nightly_export breakage (b), making them comparable in substance, though report 2 adds slightly more rigor (direct grep verification, README invariant citation).

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all five expectations; Report 2 is marginally stronger on application-layer defense-in-depth and the blocking boot check, while Report 1 is more accurate about the offending commit touching all three config files (Report 2 wrongly calls it a one-line docker-compose diff) — overall comparable. | claude-sonnet-5: Both reports correctly diagnose the owner/FORCE RLS root cause and recommend the same three-part remediation; Report 1 more precisely attributes all three config files (.env.example, docker-compose.yml, infra/main.tf) to the ROTA-214 commit, while Report 2 inaccurately claims the commit's diff was only a one-line docker-compose.yml change, leaving infra/main.tf's role attributed ambiguously.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): b, d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with nearly identical substance; Report 1 is marginally stronger on reproducibility by explicitly prescribing multiple post-regeneration runs, but they are essentially comparable. | claude-sonnet-5: Report 1 is stronger: both match on (a), (b), and (c), but only Report 1 performs and states a concrete reproducibility check (rerunning the suite twice post-regeneration) for (d), while Report 2 only flags the nondeterminism risk without verifying reproducibility.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports HIT all four expectations; Report 1 is marginally more explicit about removing leftover values and running the first migration manually. | claude-sonnet-5: Report 1 is slightly stronger: it explicitly calls for running the first migration manually where Report 2 only flags the runbook as untrustworthy without an explicit action item; otherwise the two reports are comparable in depth and accuracy.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: The two reports are essentially equivalent — both correctly diagnose all four points with the same evidence; comparable. | claude-sonnet-5: Both reports independently reach the same correct diagnosis, root cause, timeline, and reject the flaky-model conclusion with equivalent evidence and quality; they are comparable, with Report 2 additionally verifying the fix by actually running the batch scorer.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge panel disagreed (excluded from both arms): e

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all five expectations; they are comparable, with Report 2 slightly more granular (splitting style rules and detection-gap remediation). | claude-sonnet-5: Both reports hit all five expectations with correct citations and figures; Report 2 is slightly more thorough (adds rule 2 violation, hedging/rule 4, outage duration, and weaker remediation) but on the graded expectations they are comparable.

## Comprehension check (stage B, unblinded, non-scoring)

| Task | Skill read in the with-skill run |
|---|---|
| aicg-t2 | yes |
| arch-contracts-t1 | yes |
| bama-t1 | yes |
| consent-t2 | yes |
| csh-t1 | yes |
| dora-t2 | yes |
| env-hazards-t1 | yes |
| eval-harness-t1 | yes |
| farch-t1 | yes |
| git-cc-t2 | yes |
| mabc-t2 | yes |
| mmar-t1 | yes |
| mt-auth-t1 | yes |
| pmvg-t2 | yes |
| s2p-cutover-t1 | yes |
| sysdbg-t2 | yes |
| tcr-t1 | yes |

## Run notes

- Excluded tasks: none
- Scrub substitutions: 16
- Workspace mutation warnings: git-cc-t2-r1-loaded, git-cc-t2-r2-loaded, pmvg-t2-r1-cold, pmvg-t2-r1-loaded, pmvg-t2-r2-cold, pmvg-t2-r2-loaded, pmvg-t2-r3-cold, pmvg-t2-r3-loaded, sysdbg-t2-r1-cold, sysdbg-t2-r1-loaded, sysdbg-t2-r2-cold, sysdbg-t2-r2-loaded, sysdbg-t2-r3-cold, sysdbg-t2-r3-loaded

## Limitations

1. Single-run variance. Unless repeats > 1, each arm was sampled once per
   task; per-task results near ties are not statistically meaningful. Treat
   the aggregate delta and only large per-task swings as signal.
2. Vocabulary echo limits blinding. Judges never see condition labels,
   skill names, paths, or tool logs, and inputs are verifier-checked, but a
   skill that works changes answer content. Blinding removes provenance,
   not the measured effect. Judge inputs are committed for audit.
3. Same-vendor judging. Every comparison is graded by a two-judge
   panel (one Sonnet-class and one Opus-class judge, exact IDs pinned,
   both at medium effort) behind the identical blinding stack; each
   report-slot mark they disagree on is scored once by a pinned
   adjudicator on a minimal input, the final mark is the two-of-three
   majority, disputed marks never leave any denominator, and
   disagreement plus adjudication rates are published. All three judges
   are still Claude models: the residual same-vendor risk is mitigated,
   not removed, by the pre-registered exploratory Codex concordance
   sample re-scored on the committed judge inputs, which are public
   precisely so third parties can extend the cross-vendor audit.
4. Explicit loading, not triggering. These results say nothing about
   whether the description gets the file read autonomously in real
   sessions.
5. Synthetic fixtures. Trap states reconstruct real failure classes in
   small repos; deltas may be conservative or optimistic, direction
   unknown.
6. Read-only is enforced by construction (disposable workspaces,
   per-staging template verification, and post-run snapshot diffs over
   the working tree and git refs), not sandboxing.
