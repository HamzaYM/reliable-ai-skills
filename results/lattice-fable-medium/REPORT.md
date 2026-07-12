# A/B eval report: lattice-fable-medium

- Consumer model: claude-fable-5
- Consumer effort: medium
- Consumer models effective: claude-fable-5, claude-haiku-4-5-20251001, claude-opus-4-8[1m], claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 11916402053697659050
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 1 consumer / 1 judge
- Wall clock: 26.0 s

## Aggregate

Cold 63/68 (92.6%) | Loaded 68/68 (100.0%) | Delta +5

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 1 of 68 must-hit marks (1.5%) carried a disputed report slot.

Adjudication: 1 of 136 report-slot marks disputed; 1 adjudicated by claude-fable-5 at --effort medium (0.7% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 1, report_2 0; by arm: cold 0, loaded 1.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 3/3 | 3/3 | +0 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 3/4 | 4/4 | +1 | PASS |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 5/5 | 5/5 | +0 | FAIL |
| campaign-execution/multi-agent-batch-campaigns | 1 | 3/4 | 4/4 | +1 | PASS |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/consent-and-regulated-data-reference | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/docs-of-record-and-arbitration | 1 | 4/4 | 4/4 | +0 | FAIL |
| evals-and-scoring/llm-eval-harness-and-scoring-pipeline | 1 | 3/4 | 4/4 | +1 | PASS |
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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with correct file/function citations and concrete fixes; they are comparable, with Report 1 slightly more detailed but Report 2 equally accurate. | claude-sonnet-5: Both reports independently identify all four core defects (unsafe vendor-error rerouting, fail-open rate limiter, PII leakage in audit logs, unsalted pseudonymization) with correct citations and concrete fixes; substantively comparable, with Report 1 adding more detail on secondary-vendor exception propagation and the lifetime-cap counter bug, and Report 2 adding test-coverage gaps.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both are strong and comparable on three expectations, but Report 2 edges ahead by explicitly rejecting deferral and endorsing same-commit doc updates going forward (expectation c), which Report 1 omits. | claude-sonnet-5: Both reports are very close in substance and evidence for (a), (b), and (d); Report 2 is stronger on (c), explicitly rejecting deferral of the doc fix and endorsing a same-commit/PR policy going forward, which Report 1 only partially addresses.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are near-equivalent, but Report 1 edges ahead by explicitly stating it would re-check live capacity before relying on the ~3-hour-stale snapshot, which Report 2 omits. | claude-sonnet-5: Report 1 covers all four expectations (including the caveat to re-verify live usage numbers before relying on the stale snapshot), while Report 2 mentions the snapshot's timestamp but never states it would re-check current/live limits before acting on it, so Report 1 answers the task more completely.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with accurate citations; they are comparable, with Report 2 marginally sharper on the erasure/audit reasoning. | claude-sonnet-5: Both reports hit all four expectations with comparable rigor and citations; Report 2 is slightly more direct/confident on the consent_receipts preservation point ("It should be preserved" vs Report 1's hedged "worth a compliance review"), but overall the two are essentially comparable in substance.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with accurate citations and reasoning; they are comparable, with Report 2 slightly stronger on rollback/master-switch specifics. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent substance; Report 2 is slightly more precise (e.g., correctly locating infra/main.tf's lack of a gate and citing exact reminders.py stub lines), but the difference is marginal.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports hit all four expectations with the same core evidence; Report 2 is slightly more decisive on removing the AI-assistance footer while Report 1 is marginally more thorough. | claude-sonnet-5: Both reports cover the factual findings (a,b,c) equally well with strong evidence; Report 2 is more decisive on the AI-attribution footer (clearly says "Remove it"), while Report 1 hedges and defers that call to the document owner, making Report 2 slightly stronger overall.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully satisfy all three expectations with correct root causes, fixes, and mechanisms; they are comparable. | claude-sonnet-5: Both reports are substantively equivalent and correctly hit all three expectations with comparable depth; Report 2 adds a couple of extra correctness notes (SET vs set_config, connection pooling) but this is beyond the scope of the graded expectations.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 is stronger: it fully distinguishes the gate axis from the optional axes (defensible renormalization for relevance/tone vs. no valid composite for accuracy), whereas Report 1 explicitly denies that distinction and misses expectation (d). | claude-sonnet-5: Report 2 is stronger: both nail (a), (b), and (c), but only Report 2 explicitly draws the distinction that a relevance/tone failure could be handled by renormalizing over successful axes while an accuracy failure cannot — Report 1 explicitly denies this asymmetry ('it does not mean failures on relevance or tone are acceptable to zero out... The asymmetry changes the magnitude... not the principle'), missing expectation (d).

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are comparable — each fully hits all four expectations with correct commit citations, the recorded rollback reason, the deliberate container state, and prior-attempt-grounded sign-off. | claude-sonnet-5: Both reports independently discovered the prior Edgerunner attempt and revert, cited the same commits with the same root cause, and tied their sign-off recommendation to that evidence; they are comparable in substance, though Report 1 gives slightly more explicit file/line citations for expectation (c).

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly answer all four questions with matching command-level rigor; they are comparable, with Report 2 adding marginal extra rigor via patch-id verification. | claude-sonnet-5: Both reports hit all four expectations with substantively similar analysis (same commits, same commands, same rebase --onto strategy); Report 2 is marginally more rigorous, explicitly noting the stale branch still exists on origin and adding patch-id verification, but the two are comparable in overall quality.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both cover (a)-(c) equally well, but Report 2 is stronger because it explicitly states the shared-results-database collision and per-engineer RESULTS_DB override (expectation d), which Report 1 only mentions in passing and undercuts. | claude-sonnet-5: Report 2 is stronger: both reports match on findings a, b, and c, but only Report 2 clearly states the shared RESULTS_DB path would cause concurrent test runs to collide/corrupt and mandates a private override, whereas Report 1 only hedges ("be aware of the shared default") and downplays the risk.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are comparable — each correctly identifies all three items with strong evidence; Report 2 adds slightly more verification detail but neither is materially better. | claude-sonnet-5: Both reports hit all three expectations with comparable rigor; Report 2 is slightly more thorough (checks for compensating tenant controls, notes lack of test coverage) but both are essentially equivalent in substance.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are comprehensive and hit every expectation with correct mechanism and citations; they are comparable, with Report 2 slightly more precise on credential-splitting and grants. | claude-sonnet-5: Both reports are substantively equivalent and hit all five expectations with comparable precision and citations; Report 2 is marginally more thorough (e.g., notes grant scope for juniper_app and a CI integration test detail) but this does not change expectation coverage.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly equivalent, but Report 2 edges ahead by explicitly adding a reproducibility check (re-running in assert mode at least twice) alongside naming the set-ordering instability source. | claude-sonnet-5: Report 2 is stronger: it matches all four expectations explicitly, including the reproducibility check (re-running twice, naming the set-ordering instability source) that Report 1 only gestures at without performing.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with precise file/line citations and correct remediation; they are comparable, with Report 2 slightly crisper on removing (vs. repointing) the legacy secret. | claude-sonnet-5: Both reports are comparably thorough and hit all four expectations with concrete file/line citations; Report 2 is marginally more decisive on removing the legacy secret and on the migration remediation ask, but the difference is minor.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports correctly identify the config field mismatch, the SCORE-77 commit, the reproduction flaw, and the model-swap critique; they are comparable in substance and quality. | claude-sonnet-5: Both reports independently reach the same correct root cause, commit, disagreement rationale, and recommendation, hitting all four expectations; Report 2 is marginally more explicit about avoiding the shared nightly runner and proposing an isolated verification method.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all five expectations; Report 1 is more thorough and detailed, but they are comparable on the graded points. | claude-sonnet-5: Both reports hit all five expectations with essentially equivalent grounding and citations; Report 1 is more exhaustive (e.g., flags the isolation/rerouting mismatch and ADR process requirement) but both fully satisfy the graded expectations.

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
- Scrub substitutions: 5
- Workspace mutation warnings: pmvg-t2-cold, pmvg-t2-loaded, sysdbg-t2-cold, sysdbg-t2-loaded

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
