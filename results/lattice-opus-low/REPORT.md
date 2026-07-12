# A/B eval report: lattice-opus-low

- Consumer model: claude-opus-4-8
- Consumer effort: low
- Consumer models effective: claude-opus-4-8, claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 8405383882127895304
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 156.2 s

## Aggregate

Cold 59/68 (86.8%) | Loaded 65/68 (95.6%) | Delta +6

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 14 of 204 must-hit marks (6.9%) carried a disputed report slot.

Adjudication: 15 of 408 report-slot marks disputed; 15 adjudicated by claude-fable-5 at --effort medium (3.7% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 10, report_2 5; by arm: cold 7, loaded 8.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 60/68 (88.2%) | 66/68 (97.1%) | +8.8 |
| r2 | 56/68 (82.4%) | 65/68 (95.6%) | +13.2 |
| r3 | 62/68 (91.2%) | 64/68 (94.1%) | +2.9 |

Endpoint mean over repeats: cold 87.3% | loaded 95.6% | delta +8.3 pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 2/3 | 2/3 | +0 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 3/4 | 4/4 | +1 | PASS |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 4/5 | 4/5 | +0 | FAIL |
| campaign-execution/multi-agent-batch-campaigns | 1 | 3/4 | 3/4 | +0 | FAIL |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 3/4 | 4/4 | +1 | PASS |
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

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): b, c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent substance and correct fixes; Report 1 adds extra depth (TTL/lifetime-counter bug, uncaught secondary), making them comparable with a slight edge to Report 1. | claude-sonnet-5: Both reports are very close in substance across all four questions; Report 2 slightly edges out Report 1 by explicitly calling for an allowlist-based approach to metadata logging (expectation c), which Report 1 only vaguely addresses via "scrub metadata for PII."

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and comparable on the direct/gateway, external_ref, and webhook findings, but Report 2 edges ahead by explicitly endorsing landing doc fixes in the same commit as the code going forward (expectation c). | claude-sonnet-5: Report 2 fully addresses expectation (c) by explicitly endorsing immediate/same-commit doc fixes and same-commit doc updates going forward, while Report 1 hedges and never rejects deferral or states the same-commit practice; on (a), (b), and (d) both reports are equivalent, so Report 2 is the stronger overall report.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both nail the core token/backend analysis, but Report 2 is stronger because it also flags the snapshot's ~3-hour staleness and commits to re-checking live limits (expectation d), which Report 1 omits. | claude-sonnet-5: Report 2 matches all four expectations, including flagging the snapshot's staleness and the need to re-check live limits, while Report 1 misses that point entirely — Report 2 is the stronger answer.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent grounding; they are comparable, with Report 1 adding minor extra detail (delete-ordering coupling) but no scoring difference. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent depth and precision; they are comparable in quality, with Report 2 slightly more explicit about anonymization as an alternative and Report 1 slightly more explicit about the DELETE-ordering coupling bug (neither difference affects expectation coverage).

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit expectations a–c cleanly, but Report 1 also identifies the missing global/env-level gate (d) that Report 2 does not clearly address, making Report 1 slightly more complete. | claude-sonnet-5: Report 1 hits all four expectations, including the missing-global-gate point; Report 2 hits three of four but omits any recommendation for an environment/deploy-level kill switch alongside the per-tenant flag.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with the same grounded evidence; they are comparable, with Report 1 slightly more thorough and Report 2 slightly more concise. | claude-sonnet-5: Both reports hit all four expectations with solid, well-grounded evidence; Report 2 is slightly more direct/decisive in phrasing (e.g., footer removal, image reconciliation) while Report 1 adds a few extra caveats (draft commit message note) — overall comparable quality.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly satisfy all three expectations with near-identical substance; they are comparable. | claude-sonnet-5: Both reports independently identify the same root cause, fix, and wipe-related failure with nearly identical accuracy and detail; report 2 is marginally more thorough (e.g., explicitly notes cedar_owner is recreated via POSTGRES_USER and suggests folding bootstrap into the reset flow), but both fully satisfy all three expectations.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with correct code citations; they are comparable, with Report 1 marginally more explicit in operationalizing the gate-vs-optional axis distinction. | claude-sonnet-5: Both reports hit all four expectations with correct code citations and reasoning; Report 1 states the gate-vs-optional distinction slightly more explicitly and cleanly, but the two are comparable in substance.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation and are comparable; Report 2 is slightly more thorough in naming the removed serverless files, but the substance is equivalent. | claude-sonnet-5: Both reports correctly discover and cite the prior PLAT-31 Edgerunner attempt/revert and its connection-exhaustion root cause with commit-grounded evidence and tie their sign-off recommendation to it; Report 2 edges ahead by explicitly naming deploy/edgerunner.toml and backend/serverless_handler.py and framing the revert as a deliberate ("lost on purpose") choice, satisfying expectation (c) that Report 1 leaves implicit.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully satisfy all four expectations with equivalent evidence, commands, and reasoning; they are comparable. | claude-sonnet-5: Both reports independently reach identical, correct conclusions on all four points with concrete git evidence and commands; Report 2 adds a bit more depth on why a plain rebase would fail to auto-drop the squashed commits, but both fully satisfy every expectation.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 3/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | MISS |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports cover grouping, ordering, and the F-06/F-08 judgment calls equally well, but Report 2 answers better overall because it correctly flags the shared RESULTS_DB collision and mandates a distinct DB per engineer, which Report 1 dismisses as "harmless." | claude-sonnet-5: Tied overall (3 of 4 hits each): Report 1 correctly keeps F-11 in the early concurrent stage but only flags RESULTS_DB as 'harmless,' missing the required override instruction, while Report 2 explicitly defers F-11 to a later Wave 2 (missing the staging requirement) but correctly identifies and mandates a distinct RESULTS_DB per engineer.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 2/3, loaded 2/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | MISS | MISS |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports nail the cross-tenant leak (a) and correctly handle the raw-SQL string (c), and both miss the exports.py signature-mismatch (b); they are comparable, with Report 2 slightly more thorough. | claude-sonnet-5: Both reports correctly identify the tenant-isolation blocker (a) and correctly avoid flagging the SQL-injection string as an exploitable defect (c), but neither caught the nightly_export/exports.py signature-break in (b); Report 2 is somewhat more thorough overall (also flags the latent startswith bug) but the two are comparable against the stated expectations.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 4/5, loaded 4/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | MISS |
| c | HIT | HIT |
| d | HIT | HIT |
| e | MISS | HIT |

Judge panel disagreed (excluded from both arms): a, c, d, e

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly identical on causes/fixes, but Report 2 additionally specifies a blocking boot-time role check, edging it ahead. | claude-sonnet-5: Both reports are nearly identical in analysis and quality, but Report 2 explicitly includes the required startup/boot-time blocking check (expectation e), which Report 1 only frames as a CI/infra guardrail, making Report 2 the more complete answer.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports hit all four expectations; Report 2 is marginally stronger by explicitly re-running the comparison twice for reproducibility, while Report 1 only notes the nondeterminism source. | claude-sonnet-5: Both reports are very similar in substance and hit a,b,c equally well, but Report 2 explicitly verifies reproducibility by re-running the comparison twice while Report 1 only notes the nondeterminism risk without performing a concrete reproducibility check, making Report 2 the stronger overall answer.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports hit all four expectations; Report 2 is marginally stronger on the remove-vs-disable nuance for the shadow sink and legacy secret. | claude-sonnet-5: Both reports hit all four expectations with concrete file/line citations; Report 2 is marginally stronger on category (c)/(d) trap handling (explicitly demands removal, not just value changes) and gives a more direct, actionable recommendation for the frontend build fix, but the difference is minor.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are essentially equivalent, correctly hitting all four expectations with the same root cause, commit, and reasoning; Report 2 adds a slightly stronger isolated-verification framing but the difference is negligible. | claude-sonnet-5: Both reports independently reach identical, correct conclusions on all four points with comparable evidence and rigor; report 2 adds slightly more detail (annotated code snippet, regression-test suggestion) but substantively they are equivalent.

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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all five expectations with equivalent substance and citations; they are comparable. | claude-sonnet-5: Both reports hit all five expectations with comparable accuracy and citations; report 2 is slightly more precise (adds recovery time, distinguishes rules 1-4 explicitly) but the substance is equivalent.

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
- Scrub substitutions: 53
- Workspace mutation warnings: git-cc-t2-r1-loaded, git-cc-t2-r2-loaded, git-cc-t2-r3-loaded, mabc-t2-r3-cold, sysdbg-t2-r2-cold, sysdbg-t2-r2-loaded, sysdbg-t2-r3-loaded

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
