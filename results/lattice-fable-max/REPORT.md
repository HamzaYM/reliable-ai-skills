# A/B eval report: lattice-fable-max

- Consumer model: claude-fable-5
- Consumer effort: max
- Consumer models effective: claude-fable-5, claude-haiku-4-5-20251001, claude-opus-4-8[1m]
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.207 (Claude Code)
- Seed: 15602153937591721000
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 1282.7 s

## Aggregate

Cold 64/65 (98.5%) | Loaded 65/65 (100.0%) | Delta +1

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 5 of 195 must-hit marks (2.6%) carried a disputed report slot.

Adjudication: 5 of 390 report-slot marks disputed; 5 adjudicated by claude-fable-5 at --effort medium (1.3% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 5, report_2 0; by arm: cold 5, loaded 0.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 63/65 (96.9%) | 65/65 (100.0%) | +3.1 |
| r2 | 64/65 (98.5%) | 65/65 (100.0%) | +1.5 |
| r3 | 63/65 (96.9%) | 65/65 (100.0%) | +3.1 |

Endpoint mean over repeats: cold 97.4% | loaded 100.0% | delta +2.6 pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| architecture-and-contracts/architecture-contracts-as-law | 1 | 4/4 | 4/4 | +0 | FAIL |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 5/5 | 5/5 | +0 | FAIL |
| campaign-execution/multi-agent-batch-campaigns | 1 | 4/4 | 4/4 | +0 | FAIL |
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

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations thoroughly; comparable, with Report 2 marginally firmer on failing closed for the Redis backend path. | claude-sonnet-5: Both reports are thorough and nearly identical in substance across (a), (c), and (d); Report 2 is stronger on (b) because it explicitly commits to fail-closed (return False) on Redis backend failure, while Report 1 hedges by saying to 'decide fail-open vs. fail-closed explicitly' without recommending deny.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent accuracy and citations; they are comparable. | claude-sonnet-5: Both reports hit all four expectations with comparable rigor and citations; Report 2 is slightly more explicit in calling out errors.py as 'not a violation' and framing doc drift as a bug to fix immediately rather than schedule, but the difference is marginal.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports hit all four expectations with the same correct numbers and recommendation; Report 1 adds a stub-code caveat while Report 2 adds a split/offset caveat. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent numbers and reasoning; Report 2 is marginally stronger on operational caution (flags --limit's prefix-only behavior and overwrite risk when discussing not splitting the job), while Report 1 uniquely flags that score_batch.py may be a non-functional stub — a valuable but out-of-scope-for-these-expectations observation, so overall the two are comparable.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent depth, accuracy, and citations; they are comparable. | claude-sonnet-5: Both reports are comprehensive and hit all four expectations with strong evidentiary citations; Report 2 adds a useful extra note (recommending erase_user.py append an audit row) but both are essentially comparable in quality and completeness.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with strong repository grounding; they are comparable, with Report 1 marginally more detailed on hardening but Report 2 equally complete on the core findings. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent, well-cited answers; Report 2 adds slightly more rigor on edge-case value coercion (null/string handling) but the two are comparable in overall quality.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with strong repository-grounded evidence and are comparable in quality. | claude-sonnet-5: Both reports hit all four expectations with solid grounded evidence; Report 2 is slightly more organized in answer 4 (explicitly enumerates three items) but substantively the two reports are comparable in coverage and accuracy.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly answer all three questions with equivalent depth and specificity; they are comparable. | claude-sonnet-5: Both reports are thorough and correctly hit all three expectations with nearly equivalent depth and accuracy; Report 1 and Report 2 are comparable in quality.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports nail (a)-(c) with equal rigor, but Report 1 correctly distinguishes the gate axis from optional axes (renormalize for relevance/tone, quarantine for accuracy) while Report 2 explicitly rejects that distinction, making Report 1 the stronger answer overall. | claude-sonnet-5: Both reports cover the mechanics (a, b) and the accuracy-specific write-block (c) equally well, but only Report 1 arrives at the required distinction (d) that relevance/tone failures may be handled via renormalization while accuracy failures must not — Report 2 explicitly argues against differentiated handling, making Report 1 the stronger answer overall.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with commit-grounded evidence; Report 2 is somewhat more exhaustive but the two are comparable in answering the task. | claude-sonnet-5: Both reports fully satisfy all four expectations by grounding their analysis in the same prior-attempt commits (454a21f/597777b/1712565) and the same recorded connection-exhaustion cause; Report 2 goes further with additional code-level defects (missing Postgres driver, circular import, dead stopgap engine) but this extra depth is not required by the expectations, making the two reports comparable on the graded criteria.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports correctly and thoroughly hit all four expectations with near-identical, well-grounded reasoning; they are comparable. | claude-sonnet-5: Both reports hit all four expectations with equivalent rigor; Report 2 is marginally stronger on (d) with an explicit `git fetch origin`/origin-main freshness check, while Report 1 is otherwise just as thorough.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with strong repository-grounded detail; they are comparable, with Report 2 marginally crisper on the run_batch.py cluster. | claude-sonnet-5: Both reports independently identify the same core facts (registry.py cluster, staged ordering, F-06 as a policy decision, and the shared RESULTS_DB path) and hit all four expectations equally well; they are comparable in substance, with Report 1 slightly more detailed on integration/branching mechanics and Report 2 slightly more explicit about output-attribution risk from landing changes together.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are comprehensive and hit every expectation with correct mechanism and citations; they are comparable, with Report 1 slightly tighter on remediation ordering and Report 2 adding a startup check that generalizes across all bypass variants. | claude-sonnet-5: Both reports independently identify the same root cause, commit, remediation, and prevention measures with equivalent precision and citations; they are comparable in quality, with Report 2 offering slightly more thorough historical verification (git show, --stat) and additional adjacent findings.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with essentially identical reasoning; they are comparable, with Report 2 marginally cleaner on the explicit re-run-twice reproducibility check. | claude-sonnet-5: Report 2 covers all four expectations, including a concrete reproducibility check (re-running twice) and naming the set-ordering instability source; Report 1 misses expectation (d) despite noting nondeterministic key ordering, since it never actually verifies reproducibility across multiple runs.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with correct file/line citations; Report 1 is marginally more thorough (explicit migration chain and cleaner category-(d) removal), but they are essentially comparable. | claude-sonnet-5: Both reports independently verify and cite the same files/lines and reach identical conclusions on all four expectations; Report 1 is marginally more decisive on the legacy_billing_secret_arn trap (calls for outright deletion) while Report 2 hedges toward confirmation, but this does not affect any graded expectation.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with strong, repository-grounded evidence and are comparable in quality. | claude-sonnet-5: Both reports independently reach the same correct root cause, timeline, and reproducibility analysis with nearly identical rigor; Report 2 is marginally more precise on point (d) by explicitly naming a shadow-evaluation alternative rather than only critiquing the proposed plan.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all five expectations with accurate citations; they are comparable, with Report 1 slightly more detailed but Report 2 equally complete. | claude-sonnet-5: Both reports hit all five expectations with near-identical citations and quotes; they are comparable in substance, though Report 1 additionally flags the mitigation-narrative contradiction and role-name exposure with slightly more granularity.

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
| mt-auth-t1 | yes |
| pmvg-t2 | yes |
| s2p-cutover-t1 | yes |
| sysdbg-t2 | yes |
| tcr-t1 | yes |

## Run notes

- Excluded tasks: mmar-t1
- Exclusions by failing arm: loaded 1
- Scrub substitutions: 53
- Workspace mutation warnings: csh-t1-r2-cold, eval-harness-t1-r1-loaded, eval-harness-t1-r3-loaded, sysdbg-t2-r1-cold, sysdbg-t2-r3-cold

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
