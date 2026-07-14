# A/B eval report: lattice-sonnet-max

- Consumer model: claude-sonnet-5
- Consumer effort: max
- Consumer models effective: claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.207 (Claude Code)
- Seed: 12550176211171039998
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 1022.2 s

## Aggregate

Cold 60/68 (88.2%) | Loaded 68/68 (100.0%) | Delta +8

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 14 of 204 must-hit marks (6.9%) carried a disputed report slot.

Adjudication: 15 of 408 report-slot marks disputed; 15 adjudicated by claude-fable-5 at --effort medium (3.7% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 7, report_2 8; by arm: cold 8, loaded 7.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 61/68 (89.7%) | 68/68 (100.0%) | +10.3 |
| r2 | 61/68 (89.7%) | 68/68 (100.0%) | +10.3 |
| r3 | 61/68 (89.7%) | 67/68 (98.5%) | +8.8 |

Endpoint mean over repeats: cold 89.7% | loaded 99.5% | delta +9.8 pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 3/3 | 3/3 | +0 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 2/4 | 4/4 | +2 | PASS |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 3/5 | 5/5 | +2 | PASS |
| campaign-execution/multi-agent-batch-campaigns | 1 | 3/4 | 4/4 | +1 | PASS |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 3/4 | 4/4 | +1 | PASS |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 3/4 | 4/4 | +1 | PASS |
| docs-and-compliance/consent-and-regulated-data-reference | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/docs-of-record-and-arbitration | 1 | 4/4 | 4/4 | +0 | FAIL |
| evals-and-scoring/llm-eval-harness-and-scoring-pipeline | 1 | 4/4 | 4/4 | +0 | FAIL |
| tiered-review/tiered-consultancy-review | 1 | 5/5 | 5/5 | +0 | FAIL |
| validation-gates/pre-merge-validation-gate | 1 | 3/4 | 4/4 | +1 | PASS |

## Per-task must-hits

### aicg-t2 (cost-and-safety-guardrails/ai-cost-tracking-and-guardrails)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with correct findings and concrete fixes; they are comparable in substance. | claude-sonnet-5: Both reports hit all four expectations with comparable depth and correct concrete fixes; Report 1 adds empirical test verification (actually running the code) while Report 2 adds a bonus insight about per-applicant rate-limit keying defeating aggregate protection — overall they are essentially on par in quality.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 2/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and comparable on items 1–3, but Report 2 edges ahead by explicitly recommending dropping the hardcoded webhook count in favor of pointing at the code, which Report 1 misses. | claude-sonnet-5: Report 2 more fully satisfies the expectations, explicitly endorsing same-commit/PR doc updates going forward and recommending dropping the hardcoded webhook count in favor of pointing to source, while Report 1 covers those points only partially.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent grounding; comparable overall (Report 1 adds an out-of-scope stub-pipeline finding, Report 2 is slightly tighter on citations). | claude-sonnet-5: Both reports fully hit all four expectations with essentially equivalent numbers and reasoning; Report 1 additionally flags that score_one()/fetch_transcripts() are stubs producing fake zero scores, an extra finding beyond the stated expectations but relevant to the task's real-world stakes.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent evidence and accuracy; they are comparable. | claude-sonnet-5: Both reports hit all four expectations with strong, well-cited evidence; they are comparable in substance, with Report 2 offering slightly more nuance (e.g., noting erase_user.py's correctness relative to retention_sweep.py's bug, and flagging the missing __main__ entrypoint) but neither is decisively better on the graded expectations.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully nail expectations (a)-(c); Report 2 additionally identifies the missing environment-level gate and recommends adding one, making it the stronger answer overall. | claude-sonnet-5: Both reports hit a/b/c equally well, but only Report 2 identifies the missing environment-level gate and recommends ANDing it with the per-tenant flag (expectation d), giving it a fuller answer overall.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with grounded evidence; they are comparable, with Report 1 slightly more detailed but Report 2 equally accurate. | claude-sonnet-5: Both reports hit all four expectations with strong, well-grounded evidence; Report 1 is slightly more thorough (e.g., pixel-dimension checks, explicit "must be removed" list) but the two are substantively comparable in quality.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly hit all three expectations with equivalent grounding in the repo; they are comparable, with Report 1 slightly more explicit on role-separation structuring and Report 2 adding extra auth-gap observations. | claude-sonnet-5: Both reports independently identify the same root cause, fix, and reset-gap mechanism with comparable precision and file-level specificity; Report 2 adds minor extra findings (auth gap, connection-close hygiene) but both fully satisfy all three expectations equally well.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with strong code-grounded reasoning; they are comparable, with Report 1 slightly richer on the unimplemented-gate observation and Report 2 slightly cleaner on the renormalize-vs-gate distinction. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent substance; Report 2 states the distinction in (d) slightly more crisply with explicit parallel bullets, but Report 2 also fabricates quotes from a nonexistent "project documentation" source, which is a fabrication concern outside the scored expectations.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with well-grounded commit citations; comparable overall, with Report 1 marginally more detailed but neither materially stronger. | claude-sonnet-5: Both reports are very thorough and hit all four expectations with strong, specific citations to commits and code; Report 2 additionally catches that the prior stopgap fix never touched the actual query path (dead code), a sharper root-cause finding, making it marginally more rigorous, but both are comparable in overall quality and coverage.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with correct git analysis; Report 1 is marginally more thorough but they are comparable. | claude-sonnet-5: Both reports are thorough and hit all four expectations with nearly identical technical substance (same commands, same conflict discovery, same rebase plan); Report 1 is slightly more rigorous in isolating the true feature diff via git diff feat/weighted-scorer..feat/pairwise-metric, while Report 2 adds a two-dot vs three-dot diff distinction that's a nice bonus but not required.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports cover grouping, ordering, and the F-06 judgment call equally well, but Report 1 correctly identifies the shared RESULTS_DB path collision risk and the need to override it, which Report 2 dismisses as dead config — making Report 1 slightly stronger overall. | claude-sonnet-5: Report 1 covers all four expectations, including correctly flagging the RESULTS_DB collision risk and recommending an env-var override, whereas Report 2 explicitly dismisses that same finding as "dead config" and "not required," missing expectation (d); on (a)-(c) the two are comparable.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all three expectations with equivalent substance; Report 1 is marginally cleaner in keeping the raw-SQL interpolation explicitly non-blocking, while Report 2 backs its findings with execution-based confirmation — overall comparable. | claude-sonnet-5: Both reports correctly and thoroughly identify the tenant-scoping defect (a) and the exports.py breaking-signature regression (b); Report 1 passes expectation (c) by explicitly concluding the status interpolation is not exploitable, while Report 2 fails it by listing the SQL string interpolation as its own numbered defect ("c) Secondary but real") that should be fixed before sign-off, contrary to the expectation that such a defect not be reported as blocking.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 3/5, loaded 5/5, threshold 4: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |
| e | MISS | HIT |

Judge panel disagreed (excluded from both arms): e

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly diagnose the owner-exempt-from-RLS root cause, the ROTA-214 commit, and all four remediation/prevention expectations; they are comparable, with Report 2 slightly crisper on the blocking boot-time check. | claude-sonnet-5: Both reports are thorough and hit nearly identical marks on root cause, commit identification, and remediation, but Report 2 explicitly specifies a blocking boot-time startup check that refuses to start the app on misconfiguration, while Report 1 only proposes a periodic/pre-deploy check, making Report 2 marginally more complete against expectation (e).

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports hit all four expectations with grounded, near-equivalent reasoning; Report 2 gives an explicit re-run-twice reproducibility check while Report 1 names the set-ordering instability source, and both catch the undocumented rounding change. | claude-sonnet-5: Report 2 is stronger: it matches Report 1 on rejecting live-test enablement, diffing golden values, and re-measuring flaky/lint figures, but only Report 2 explicitly verifies golden-file reproducibility by re-running the comparison test multiple times, while Report 1 only flags a latent ordering-instability risk without performing the reproducibility check.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): b, c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and closely comparable, but Report 2 edges ahead by firmly stating the pipeline has no migration step and that the runbook's automatic-migration claim is unsupported, whereas Report 1 only hedged that claim as unverifiable. | claude-sonnet-5: Both reports are very close in substance and quality across all four expectations; report 2 is marginally more precise on remediation specifics (e.g., recommending omission over toggling, and explicitly naming the cross-environment privilege-boundary risk), but neither explicitly calls for running/confirming the first migration, so they tie overall.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are comprehensive and hit all four expectations with equivalent, correctly-grounded findings; they are comparable. | claude-sonnet-5: Both reports independently reach the same correct root cause, timeline, reproduction critique, and reject the flaky-model plan with comparable rigor; Report 2 adds slightly more design-flaw context (two unsynchronized sources of truth) but the two are substantively equivalent in coverage.

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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all five expectations with strong repo-grounded citations; they are comparable, with Report 1 slightly tighter and Report 2 adding more speculative extras. | claude-sonnet-5: Both reports hit all five expectations with solid citations; Report 2 goes further with additional verification (arithmetic sanity-check on the SLA figure, deeper cross-repo idempotency-bug investigation) making it marginally more thorough, but both fully satisfy the stated expectations.

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
- Scrub substitutions: 151
- Workspace mutation warnings: aicg-t2-r1-loaded, arch-contracts-t1-r2-loaded, csh-t1-r1-cold, csh-t1-r2-cold, csh-t1-r2-loaded, csh-t1-r3-loaded, eval-harness-t1-r2-loaded, git-cc-t2-r1-loaded, git-cc-t2-r2-loaded, git-cc-t2-r3-loaded, mabc-t2-r1-loaded, pmvg-t2-r1-cold, pmvg-t2-r1-loaded, pmvg-t2-r2-loaded, pmvg-t2-r3-loaded, sysdbg-t2-r1-cold, sysdbg-t2-r1-loaded, sysdbg-t2-r2-cold, sysdbg-t2-r2-loaded, sysdbg-t2-r3-cold, sysdbg-t2-r3-loaded

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
