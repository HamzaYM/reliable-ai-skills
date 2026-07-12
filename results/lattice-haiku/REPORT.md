# A/B eval report: lattice-haiku

- Consumer model: claude-haiku-4-5-20251001
- Consumer effort: none
- Consumer models effective: claude-haiku-4-5-20251001
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 13315580655536474930
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 1 consumer / 1 judge
- Wall clock: 97.4 s

## Aggregate

Cold 44/68 (64.7%) | Loaded 62/68 (91.2%) | Delta +18

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 9 of 68 must-hit marks (13.2%) carried a disputed report slot.

Adjudication: 10 of 136 report-slot marks disputed; 10 adjudicated by claude-fable-5 at --effort medium (7.4% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 3, report_2 7; by arm: cold 6, loaded 4.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 1/3 | 2/3 | +1 | PASS |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 2/4 | 4/4 | +2 | PASS |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 4/5 | 5/5 | +1 | PASS |
| campaign-execution/multi-agent-batch-campaigns | 1 | 0/4 | 2/4 | +2 | FAIL |
| change-control/git-change-control-for-agents | 1 | 2/4 | 3/4 | +1 | PASS |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 3/4 | 4/4 | +1 | PASS |
| debugging-playbooks/failure-archaeology | 1 | 3/4 | 4/4 | +1 | PASS |
| debugging-playbooks/systematic-debugging-playbook | 1 | 3/4 | 4/4 | +1 | PASS |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/consent-and-regulated-data-reference | 1 | 2/4 | 4/4 | +2 | PASS |
| docs-and-compliance/docs-of-record-and-arbitration | 1 | 4/4 | 3/4 | -1 | FAIL |
| evals-and-scoring/llm-eval-harness-and-scoring-pipeline | 1 | 3/4 | 4/4 | +1 | PASS |
| tiered-review/tiered-consultancy-review | 1 | 3/5 | 4/5 | +1 | PASS |
| validation-gates/pre-merge-validation-gate | 1 | 1/4 | 4/4 | +3 | PASS |

## Per-task must-hits

### aicg-t2 (cost-and-safety-guardrails/ai-cost-tracking-and-guardrails)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | MISS | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): a

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 is better: it hits all four expectations, while Report 2 misses (b) by wrongly endorsing the non-production STAGE fail-open as appropriate. | claude-sonnet-5: Report 1 correctly classifies RateLimitError/RequestTimeoutError/ServerError as legitimate failover candidates and non-production STAGE bypass as a violation (matching the expected security posture), while Report 2 explicitly endorses disabling rate limiting in non-production and calls RateLimitError failover inappropriate, missing two key expectations; both reports are strong and comparable on the logging and salt questions, but Report 1 better matches the expected answers overall.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 2/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 is stronger: both nail the direct-call sites and the external_ref gap, but Report 1 also explicitly ties the doc fix to the same commit and recommends dropping the hardcoded webhook count, which Report 2 omits. | claude-sonnet-5: Report 1 fully satisfies all four expectations, including explicit same-commit documentation policy endorsement and recommending dropping the hardcoded webhook count; Report 2 covers the factual findings well but only updates the count to 5 rather than recommending removal of the hardcoded count, and doesn't explicitly reject deferring the doc fix to a follow-up ticket.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both nail tokens, capacity, and the switch to ridgeline, but Report 2 additionally flags the 3-hour-old snapshot and the need to re-verify live limits, making it the stronger answer. | claude-sonnet-5: Report 2 is more complete: it matches Report 1 on token math and the backend-switch recommendation, but additionally flags the snapshot's staleness and the need to re-verify live limits before relying on it, which Report 1 omits entirely.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 2/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 answered the task better: it correctly flags that consent_receipts should be preserved and gives both the shared-table and guard-bypass refusals plus an isolated-copy recommendation, whereas Report 1 misses both. | claude-sonnet-5: Report 2 is more complete: it correctly flags that erase_user.py should preserve consent_receipts (expectation c) and explicitly refuses both the shared-table use and the validation-guard bypass while recommending an isolated test database (expectation d), whereas Report 1 misses the consent_receipts-preservation point entirely and only weakly touches the guard-bypass refusal.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both nail the default-value analysis, but Report 1 additionally recommends a global deploy-level gate, satisfying all four expectations while Report 2 misses (d). | claude-sonnet-5: Report 1 answered all four expectations, including the crucial recommendation for a deploy/environment-level gate combined with the per-clinic value; Report 2 covered the first three well but omitted the global-gate recommendation, instead focusing more on testing, logging, and stub-implementation issues.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 3/4, threshold 3: FAIL (regression)

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | MISS |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports cover the same four core findings, but Report 2 firmly flags the AI-assistance footer as must-remove while Report 1 only hedges it as policy-dependent, making Report 2 slightly better. | claude-sonnet-5: Both reports are equally strong and grounded on questions 1-3, but Report 2 is clearly better on question 4: it decisively flags the AI-assistance footer line as something that must be removed, while Report 1 hedges ("may or may not align... Verify whether this attribution is appropriate") rather than committing to removal.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports correctly identify all three root causes and fixes; they are comparable, with Report 1 giving marginally more procedural detail. | claude-sonnet-5: Both reports independently identify the same root cause (cedar_owner bypassing RLS via DATABASE_URL), recommend the same two-role fix, and correctly diagnose the reset-script gap for cedar_app; they are comparable in substance, with Report 2 using terminology ("table owner") that maps more directly onto the expected mechanism and Report 1 offering slightly more actionable remediation detail (concrete diff, updated reset script).

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both correctly diagnose the 0.0 substitution and its ranking impact, but Report 1 answers the task more fully by distinguishing the accuracy gate axis from the optional axes and prescribing differentiated handling, which Report 2 omits by treating every axis failure identically. | claude-sonnet-5: Report 1 is more complete: it distinguishes handling for the gate axis (accuracy) vs. optional axes (relevance/tone), proposing renormalization for the latter, while Report 2 treats all axis failures identically (skip the record), missing that distinction.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports discover the prior reverted attempt and the connection-exhaustion cause, but Report 2 answers better with precise commit citations (454a21f, 597777b, 1712565), a verbatim commit body, and explicit recognition that the migration was already tried and reverted. | claude-sonnet-5: Both reports correctly discover and cite the prior Edgerunner attempt and its connection-exhaustion root cause and tie their recommendation to it, but neither explicitly identifies the current Cargobox files as a deliberately restored/intended state with the serverless config purposely removed; Report 2 edges out Report 1 with more precise, verbatim commit citations (454a21f, 597777b, 1712565) and a direct quote of the commit message.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 2/4, loaded 3/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | MISS |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fell into the two-dot-diff trap and missed the central point (c) that the PR's three-dot/merge-base view re-includes the weighted-scorer scorer.py changes; Report 1 edges ahead by supplying a concrete post-rebase verification check (d) that Report 2 lacks. | claude-sonnet-5: Report 2 better captures the crux of question 3 (that the branch's history/diff isn't purely pairwise-metric work, naming scorer.py), while Report 1 wrongly concludes the diff is fully clean; Report 1 compensates with a more concrete post-rebase verification step for question 4 that Report 2 lacks.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 0/4, loaded 2/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | MISS | HIT |
| b | MISS | MISS |
| c | MISS | HIT |
| d | MISS | MISS |

Judge panel disagreed (excluded from both arms): a, b

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 answered better overall — it correctly flags F-06 as a product/sign-off judgment call — though it omits the local-setup/RESULTS_DB collision question (d) that both reports fail to fully address. | claude-sonnet-5: Report 2 is stronger: it explicitly flags registry.py as needing single-owner coordination and correctly escalates F-06 as a product decision requiring sign-off, while Report 1 misses both; neither report adequately addresses the F-11 early-stage sequencing or the shared RESULTS_DB test-corruption risk with a concrete per-engineer mitigation.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 1/3, loaded 2/3, threshold 2: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | MISS | MISS |
| c | MISS | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both correctly block on the tenant-isolation leak and both miss the exports.py broken caller, but Report 1 edges ahead by hedging the raw-SQL status interpolation as non-exploitable-as-written whereas Report 2 overstates it as a critical SQL-injection vulnerability. | claude-sonnet-5: Both reports correctly identify the critical tenant-isolation breach but neither catches the exports.py breaking-caller defect, and both incorrectly flag the safe SQL-injection string as a blocking defect — the reports are comparable in substance, with Report 1 additionally noting the architectural convention violation.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 4/5, loaded 5/5, threshold 4: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |
| e | HIT | HIT |

Judge panel disagreed (excluded from both arms): a

Judge comparative verdict (no score weight): claude-opus-4-8: Both correctly diagnose the owner-RLS-bypass root cause, commit, and remediation, but Report 2 is stronger because it additionally adds the explicit application-level tenant filter as defense-in-depth (expectation d) and enumerates all three config files. | claude-sonnet-5: Report 2 is more complete: it cites all three config files for expectation (b), adds the explicit tenant_id application-level filter (d) which report 1 omits entirely, and provides a more general/robust boot-time ownership check (e); report 1 edges out slightly on explicitly naming FORCE ROW LEVEL SECURITY as the owner-exemption escape hatch (a), which report 2 never mentions.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 1/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | MISS | HIT |
| c | MISS | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 is clearly stronger, hitting all four expectations by rejecting stale docs, diffing golden values, and checking determinism, whereas Report 1 blindly regenerates, copies doc figures, and does no reproducibility check. | claude-sonnet-5: Report 2 substantively satisfies all four expectations (traceable golden-diff review, re-measured flaky/lint figures, reproducibility check) while Report 1 only satisfies the live-test-cost expectation and otherwise treats docs/testing.md numbers as authoritative and skips diff/reproducibility verification.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations, but Report 1 is more thorough — it flags the legacy_billing_secret_arn (fourth trap category) and states more explicitly that migrations must run before the app starts. | claude-sonnet-5: Report 1 is slightly stronger: it explicitly ties the missing migration step to the runbook's false "automatic migrations" claim and calls for confirming migrations run before launch, while Report 2 only notes the migration mechanism is "missing" without challenging the runbook claim or calling for explicit action; both reports are otherwise comparable on config flags, frontend build/API URL, and OIDC trust condition findings.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both correctly diagnose the config field mismatch, but Report 1 answers better because it explicitly explains why the single-item scorer structurally cannot show the drop, which Report 2 only gestures at. | claude-sonnet-5: Both reports independently identify the same root cause, culprit commit, disagreement with the flakiness conclusion, and reject the model-swap plan; Report 1 gives slightly more precise reproduction steps while Report 2 gives a more precise config file path and line-level defect — overall comparable in substance and correctness.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 3/5, loaded 4/5, threshold 4: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |
| e | MISS | MISS |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 answered the task better, additionally catching the individual-blame style-guide violation that Report 1 missed. | claude-sonnet-5: Report 2 is more complete: it covers all points Report 1 covers plus the individual-blame style-guide violation (expectation d) and the internal-system-name exposure, which Report 1 omits entirely; neither report explicitly flags the draft's mis-ordering (expectation e).

## Comprehension check (stage B, unblinded, non-scoring)

| Task | Skill read in the with-skill run |
|---|---|
| aicg-t2 | yes |
| arch-contracts-t1 | yes |
| bama-t1 | yes |
| consent-t2 | NO |
| csh-t1 | yes |
| dora-t2 | yes |
| env-hazards-t1 | yes |
| eval-harness-t1 | yes |
| farch-t1 | yes |
| git-cc-t2 | NO |
| mabc-t2 | NO |
| mmar-t1 | NO |
| mt-auth-t1 | NO |
| pmvg-t2 | NO |
| s2p-cutover-t1 | yes |
| sysdbg-t2 | NO |
| tcr-t1 | yes |

## Run notes

- Excluded tasks: none
- Scrub substitutions: 41
- Workspace mutation warnings: git-cc-t2-loaded, mmar-t1-cold, pmvg-t2-loaded, sysdbg-t2-cold, sysdbg-t2-loaded

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
