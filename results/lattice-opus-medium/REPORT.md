# A/B eval report: lattice-opus-medium-v2

- Consumer model: claude-opus-4-8
- Consumer effort: medium
- Consumer models effective: claude-haiku-4-5-20251001, claude-opus-4-8
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.207 (Claude Code)
- Seed: 12435064653901011027
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 127.1 s

## Aggregate

Cold 58/68 (85.3%) | Loaded 67/68 (98.5%) | Delta +9

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 9 of 204 must-hit marks (4.4%) carried a disputed report slot.

Adjudication: 11 of 408 report-slot marks disputed; 11 adjudicated by claude-fable-5 at --effort medium (2.7% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 4, report_2 7; by arm: cold 8, loaded 3.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 56/68 (82.4%) | 66/68 (97.1%) | +14.7 |
| r2 | 61/68 (89.7%) | 66/68 (97.1%) | +7.4 |
| r3 | 58/68 (85.3%) | 67/68 (98.5%) | +13.2 |

Endpoint mean over repeats: cold 85.8% | loaded 97.6% | delta +11.8 pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 2/3 | 3/3 | +1 | PASS |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 3/4 | 4/4 | +1 | PASS |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 4/5 | 5/5 | +1 | PASS |
| campaign-execution/multi-agent-batch-campaigns | 1 | 3/4 | 3/4 | +0 | FAIL |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 3/4 | 4/4 | +1 | PASS |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 3/4 | 4/4 | +1 | PASS |
| docs-and-compliance/consent-and-regulated-data-reference | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/docs-of-record-and-arbitration | 1 | 4/4 | 4/4 | +0 | FAIL |
| evals-and-scoring/llm-eval-harness-and-scoring-pipeline | 1 | 3/4 | 4/4 | +1 | PASS |
| tiered-review/tiered-consultancy-review | 1 | 5/5 | 5/5 | +0 | FAIL |
| validation-gates/pre-merge-validation-gate | 1 | 3/4 | 4/4 | +1 | PASS |

## Per-task must-hits

### aicg-t2 (cost-and-safety-guardrails/ai-cost-tracking-and-guardrails)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | MISS | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and cover most expectations; Report 1 edges ahead because it firmly states the RateLimiter should fail closed (deny) when Redis is unavailable, whereas Report 2 hedges that as a policy call. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent substance and correct fixes; comparable in quality, with Report 2 slightly more thorough on batch-level failure isolation.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and cover (a), (b), (c) equally well, but Report 2 is better overall because it correctly recommends dropping the hardcoded webhook count in favor of pointing at the code, whereas Report 1 proposes re-hardcoding it as "5". | claude-sonnet-5: Both reports are strong and nearly identical on expectations a, b, and c, but Report 2 clearly wins on expectation d by explicitly recommending dropping the hardcoded webhook-type count in favor of pointing at the source code, while Report 1 merely corrects the count from 4 to 5 without addressing the drift problem.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with essentially identical analysis and citations; they are comparable. | claude-sonnet-5: Both reports are substantively equivalent, hitting all four expectations with nearly identical numbers, reasoning, and recommendations; report 1 adds a bonus note on model-comparability (nimbus-large vs atlas-mini) while report 2 adds a bonus note on read-only constraints, but neither difference affects expectation coverage.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable: both reports hit all four expectations with grounded citations; Report 1 is slightly cleaner in naming consent_receipts as the direct Q3 preserve answer, while Report 2 adds useful extra detail but frames consent_audit as its primary preserve answer. | claude-sonnet-5: Both reports hit all four expectations with solid, well-cited answers; Report 1's answer to (c) is slightly more confident/direct than Report 2's hedged "policy call" framing, but overall the two are comparable in substance and rigor.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent substance and citations; they are comparable, with Report 2 slightly more thorough on the stub/data caveats and Report 1 on tests. | claude-sonnet-5: Both reports hit all four expectations with nearly equivalent substance; report 2 adds the extra observation that the UI and backend defaults disagree, giving slightly more actionable detail, but overall the two are comparable in quality.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with equivalent grounding and evidence; they are comparable. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent evidence and rigor; Report 1 is slightly more decisive on the AI-attribution footer (unhedged "should be removed") while Report 2 adds a minor unnecessary hedge, but the substance is comparable overall.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports correctly and thoroughly nail all three expectations with equivalent grounding; they are comparable. | claude-sonnet-5: Both reports independently and correctly identify the same root cause, fix, and wipe/rebuild explanation with equivalent depth and file-level specificity; they are comparable in quality.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and largely equivalent on the core bug, but Report 1 edges ahead by explicitly proposing renormalization over surviving axes for relevance/tone versus exclusion for accuracy, satisfying the gate-vs-optional distinction that Report 2 leaves incomplete. | claude-sonnet-5: Both reports hit a, b, and c with essentially equivalent code citations and reasoning; Report 1 is stronger because it explicitly proposes renormalizing over surviving axes for a relevance/tone failure while disqualifying accuracy failures outright (expectation d), whereas Report 2 applies the same skip-or-flag treatment to any axis failure without distinguishing the gate axis from the optional ones in its recommended handling.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 is decisively better: it discovers the prior PLAT-31 Edgerunner attempt and its revert from git history and grounds every answer in it, while Report 2 gives a solid code-level analysis but never finds the prior attempt, missing all four expectations. | claude-sonnet-5: Report 1 discovered the critical prior-attempt-and-revert history via git log and grounded all four answers in it; Report 2 never consulted git history and treated the migration as never-attempted, missing all four expectations.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully satisfy all four expectations with correct commands and reasoning; they are comparable, with Report 1 marginally more exhaustive on patch-equivalence checks. | claude-sonnet-5: Both reports independently derive and state all four expectations with concrete git evidence (merge-base, ancestry checks, file-level diff attribution, and a correct --onto rebase plan with a post-rebase freshness check); they are comparable in substance, with Report 1 slightly more granular in per-file commit attribution and Report 2 slightly cleaner in framing the squash-vs-content distinction.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 3/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | MISS |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Both cover a–c equivalently, but Report 1 fully nails the shared results-DB collision risk (d) that Report 2 only mentions as optional, making Report 1 the stronger plan. | claude-sonnet-5: Report 1 covers all four expectations explicitly (including the RESULTS_DB collision risk and required override), while Report 2 misses expectation (d), downplaying the RESULTS_DB issue as optional and 'not exercised by the current test' rather than flagging it as a concrete collision risk requiring an env override.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 2/3, loaded 3/3, threshold 2: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | MISS | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both nail the cross-tenant leak and correctly decline to blame SQL injection, but Report 2 additionally catches the exports.py signature-break regression, making it the stronger review. | claude-sonnet-5: Report 2 is more complete: it catches both blocking defects (the cross-tenant leak and the exports.py signature-break regression), while Report 1 only catches the tenant-isolation leak and misses the nightly_export breakage entirely.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 4/5, loaded 5/5, threshold 4: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 is substantially better: it is grounded in the actual juniper repo and correctly identifies the ROTA-214 commit and owner-exemption mechanism, whereas Report 1 describes a mismatched "cedar" codebase, wrongly attributes the mechanism partly to superuser, and gets the exploit-timeline commit wrong. | claude-sonnet-5: Report 2 correctly diagnoses the owner-exemption mechanism without conflating it with superuser bypass, and correctly identifies the specific ROTA-214 commit and role-name change that introduced the leak, both of which Report 1 misses (Report 1 investigates an apparently different/renamed repo state and never finds the ROTA-214 commit); Report 1 wins only on including an app-level tenant_id filter as a second isolation layer, which Report 2 omits.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly equivalent, but Report 2 edges ahead by explicitly adding a reproducibility/determinism check (re-running the golden comparison twice), which Report 1 omits. | claude-sonnet-5: Both reports are strong and nearly equivalent on the first three expectations, but Report 2 explicitly performs a reproducibility check (re-running the golden comparison twice to confirm determinism), which Report 1 omits, making Report 2 slightly more complete overall.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): b, c

Judge comparative verdict (no score weight): claude-opus-4-8: Both cover (a), (b), and (d) equally well, but Report 2 answered better overall because it clearly states the pipeline has no migration step and the runbook is wrong, whereas Report 1 only hedges that migrations are "unverifiable" due to the missing deploy script. | claude-sonnet-5: Report 2 is stronger overall: it matches Report 1 on config flags, frontend build/API URL, and OIDC trust, but additionally explicitly identifies the missing migration step and calls for a manual first migration pass, which Report 1 only vaguely gestures at via "unverifiable."

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are essentially equivalent — each fully hits all four expectations with correct root cause, commit attribution, reproduction critique, and next-step assessment; comparable overall. | claude-sonnet-5: Both reports independently reach the same correct diagnosis, culprit commit, and rebuttal of the flaky-model theory with essentially equivalent evidence; Report 2 is marginally stronger on expectation (d) by explicitly stating it verified the fix restores 0.91 via an offline re-run, but both fully satisfy all four expectations.

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

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable: both reports hit all five expectations with correct file citations; Report 2 is slightly more precise on the SLA-breach entitlement framing. | claude-sonnet-5: Both reports are substantively similar and hit expectations a-d with proper citations; neither explicitly notes that the draft's sole remediation commitment is confined to a single closing sentence, though Report 2 is somewhat more thorough overall (e.g., flagging the inaccurate 'traffic rerouted' claim and both internal-name exposures).

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
- Scrub substitutions: 40
- Workspace mutation warnings: git-cc-t2-loaded, mabc-t2-r1-cold, mmar-t1-r1-loaded, pmvg-t2-cold, pmvg-t2-loaded, pmvg-t2-r1-cold, pmvg-t2-r1-loaded, pmvg-t2-r2-cold, pmvg-t2-r2-loaded, sysdbg-t2-cold, sysdbg-t2-loaded, sysdbg-t2-r1-cold, sysdbg-t2-r1-loaded, sysdbg-t2-r2-cold, sysdbg-t2-r2-loaded

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
