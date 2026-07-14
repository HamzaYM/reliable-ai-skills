# A/B eval report: lattice-sonnet-medium-v2

- Consumer model: claude-sonnet-5
- Consumer effort: medium
- Consumer models effective: claude-haiku-4-5-20251001, claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.207 (Claude Code)
- Seed: 5588552681937500691
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 77.6 s

## Aggregate

Cold 64/68 (94.1%) | Loaded 68/68 (100.0%) | Delta +4

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 9 of 204 must-hit marks (4.4%) carried a disputed report slot.

Adjudication: 9 of 408 report-slot marks disputed; 9 adjudicated by claude-fable-5 at --effort medium (2.2% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 5, report_2 4; by arm: cold 7, loaded 2.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 60/68 (88.2%) | 68/68 (100.0%) | +11.8 |
| r2 | 63/68 (92.6%) | 67/68 (98.5%) | +5.9 |
| r3 | 62/68 (91.2%) | 67/68 (98.5%) | +7.4 |

Endpoint mean over repeats: cold 90.7% | loaded 99.0% | delta +8.4 pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 3/3 | 3/3 | +0 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 3/4 | 4/4 | +1 | PASS |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 5/5 | 5/5 | +0 | FAIL |
| campaign-execution/multi-agent-batch-campaigns | 1 | 3/4 | 4/4 | +1 | PASS |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 3/4 | 4/4 | +1 | PASS |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 4/4 | 4/4 | +0 | FAIL |
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

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong, but Report 1 answered better because it correctly demands fail-closed rate limiting (denying when STAGE isn't production and when Redis errors), whereas Report 2 defends fail-open as defensible and misses expectation (b). | claude-sonnet-5: Report 1 fully satisfies all four expectations with concrete, correctly-directed fixes, while Report 2 explicitly argues the redis fail-open behavior is "defensible" (missing expectation b) and only vaguely suggests auditing metadata rather than allowlisting it (missing expectation c) — Report 1 is the stronger, more complete answer.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and hit every expectation; Report 2 is marginally more explicit on tying doc updates to the same commit/PR, but they are comparable overall. | claude-sonnet-5: Both reports are very similar and equally thorough on (a), (b), and (d); Report 2 is stronger on (c), explicitly endorsing that doc updates should land in the same commit/PR as the code going forward, which Report 1 only implies.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations equally; they are comparable, with Report 1 adding an extra correctness observation about the stubbed scoring script. | claude-sonnet-5: Both reports hit all four expectations with comparable rigor; Report 1 additionally surfaces a notable correctness bug (score_batch.py is a stub that never calls a real model), giving it slightly more practical value, while Report 2 is marginally more explicit about refusing to run the default script as-is.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both are strong, but Report 2 answered better overall because it correctly identifies that consent_receipts must be preserved (expectation c), which Report 1 misses by only flagging consent_audit preservation. | claude-sonnet-5: Report 2 is stronger: it correctly identifies that erase_user.py wrongly deletes consent_receipts (the PII-free proof-of-consent record) and flags it as a defect, while Report 1 misses this entirely, treating the consent_receipts deletion as unremarkable and instead crediting the job for leaving consent_audit alone (which was never in question for that job). Both reports fully hit expectations a, b, and d.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly identical on the first three points, but Report 1 additionally covers the missing global/environment-level gate (d) that Report 2 omits, making Report 1 slightly better. | claude-sonnet-5: Both reports are very similar and equally strong on (a)-(c); Report 1 additionally identifies the missing global/deploy-level kill-switch and recommends adding one (expectation d), which Report 2 omits, making Report 1 the more complete answer.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with grounded evidence; Report 2 is marginally more thorough by also flagging the 'production data' and '40% fewer no-shows' items, but they are comparable. | claude-sonnet-5: Both reports hit all four expectations with solid grounding; Report 2 additionally catches the unsupported "production data" caption issue (bonus not required by expectations), giving it a slight edge in thoroughness.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly answer all three questions; comparable, with Report 2 slightly more precise on the owner+FORCE-ROW-LEVEL-SECURITY mechanism. | claude-sonnet-5: Both reports correctly diagnose all three issues and hit every expectation; Report 2 is somewhat more precise on the RLS mechanism (explicitly naming FORCE ROW LEVEL SECURITY and distinguishing owner-bypass from superuser-bypass) while Report 1 is comparably thorough and slightly more concise — overall comparable quality with Report 2 marginally more technically rigorous.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports nail (a)-(c) with strong code citations, but Report 2 additionally makes the gate-vs-optional-axis distinction (renormalize for relevance/tone, block for accuracy) that Report 1 misses, making Report 2 the stronger answer. | claude-sonnet-5: Both reports correctly diagnose the zero-substitution bug and its ranking impact, but Report 2 goes further by explicitly deriving the axis-dependent remedy (renormalize for relevance/tone, block/flag for accuracy) that the task's questions were steering toward, while Report 1 only partially gestures at this distinction.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are comparable — each fully identifies the prior reverted Edgerunner attempt, quotes the revert commit's recorded cause, treats the container as the deliberate state, and ties sign-off to the PLAT-31 owner. | claude-sonnet-5: Report 2 is slightly stronger: both reports find and cite the prior Edgerunner attempt, quote the revert commit's root cause, and tie their sign-off recommendation to it, but only Report 2 explicitly names backend/Dockerfile alongside deploy/cargobox.yaml as the deliberate current-state deployment path.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent depth and correct git reasoning; they are comparable. | claude-sonnet-5: Both reports independently verify the same facts (dead base, squashed #42, three-dot vs two-dot diff divergence, rebase plan with concrete re-verification) and hit all four expectations comparably well; Report 2 adds an explicit git merge-base --is-ancestor check, giving it a marginally more rigorous ancestry proof.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and comparable on grouping, ordering, and the F-06 judgment call, but Report 2 answers better overall because it correctly identifies the shared conftest.py results-database collision risk and the need to override RESULTS_DB, which Report 1 misses. | claude-sonnet-5: Report 2 is stronger: it explicitly identifies the shared RESULTS_DB test-database collision risk and the required fix (override RESULTS_DB per engineer), which Report 1 only vaguely gestures at without framing it as a risk or requiring action; both reports are otherwise comparable on grouping, staging, and flagging F-06.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 answered better: it caught both critical defects (cross-tenant leak and the exports.py signature-break), while Report 1 missed the nightly_export breakage entirely. | claude-sonnet-5: Report 2 is better: it catches both blocking defects (cross-tenant leak and the exports.py signature-break) while Report 1 misses the second defect entirely.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are comprehensive and correct on all five expectations; they are comparable in quality. | claude-sonnet-5: Both reports are comparably thorough and accurate, correctly diagnosing the owner-exempt-from-RLS mechanism, citing the same ROTA-214 commit and config files, and giving equivalent remediation and prevention recommendations; Report 1's startup-check recommendation is stated slightly more decisively as a hard blocker, while Report 2 adds a notable extra observation that no boot-time migration entrypoint actually exists in the repo.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and largely equivalent, but Report 2 edges ahead by adding an explicit reproducibility/determinism re-run check that Report 1 omits. | claude-sonnet-5: Report 2 covers all four expectations, including an explicit reproducibility check (re-running the suite twice to confirm the regenerated golden fixture is deterministic), while Report 1 omits any reproducibility verification of the regenerated golden file, making Report 2 the stronger and more complete answer.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable: both reports hit all four expectations, with Report 1 marginally more precise in calling for outright removal of the retired-system secret and non-empty shadow sink. | claude-sonnet-5: Both reports hit all four expectations with comparable depth; Report 2 additionally flags a role-name collision issue and missing OIDC permissions block, giving it a slight edge in thoroughness, but both fully satisfy the stated expectations.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly answer all four expectations with essentially identical, well-grounded findings; they are comparable. | claude-sonnet-5: Both reports are substantively equivalent, correctly identifying the same root cause, introducing commit, flawed reproduction, and rejecting the rollback plan with nearly identical evidence and reasoning.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all five expectations; they are comparable, with Report 2 adding marginally more precision via line citations. | claude-sonnet-5: Both reports hit all five expectations with equivalent core citations; Report 2 is somewhat more thorough (independent verification of the 99.92% figure, fuller timeline, and an added hedging critique) but coverage of the required expectations is comparable.

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
- Scrub substitutions: 168
- Workspace mutation warnings: csh-t1-r1-cold, csh-t1-r2-cold, mmar-t1-r2-cold, mmar-t1-r2-loaded, pmvg-t2-r1-cold, pmvg-t2-r1-loaded, pmvg-t2-r2-cold, pmvg-t2-r2-loaded, pmvg-t2-r3-cold, pmvg-t2-r3-loaded, sysdbg-t2-r1-cold, sysdbg-t2-r1-loaded, sysdbg-t2-r2-cold, sysdbg-t2-r2-loaded, sysdbg-t2-r3-cold, sysdbg-t2-r3-loaded

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
