# A/B eval report: lattice-sonnet-medium

- Consumer model: claude-sonnet-5
- Consumer effort: medium
- Consumer models effective: claude-haiku-4-5-20251001, claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 11662986013449714629
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 1 consumer / 1 judge
- Wall clock: 72.8 s

## Aggregate

Cold 58/68 (85.3%) | Loaded 67/68 (98.5%) | Delta +9

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 3 of 68 must-hit marks (4.4%) carried a disputed report slot.

Adjudication: 4 of 136 report-slot marks disputed; 4 adjudicated by claude-fable-5 at --effort medium (2.9% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 2, report_2 2; by arm: cold 3, loaded 1.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 2/3 | 3/3 | +1 | PASS |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 2/4 | 4/4 | +2 | PASS |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 4/5 | 5/5 | +1 | PASS |
| campaign-execution/multi-agent-batch-campaigns | 1 | 3/4 | 4/4 | +1 | PASS |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 3/4 | 4/4 | +1 | PASS |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/consent-and-regulated-data-reference | 1 | 3/4 | 4/4 | +1 | PASS |
| docs-and-compliance/docs-of-record-and-arbitration | 1 | 4/4 | 4/4 | +0 | FAIL |
| evals-and-scoring/llm-eval-harness-and-scoring-pipeline | 1 | 4/4 | 4/4 | +0 | FAIL |
| tiered-review/tiered-consultancy-review | 1 | 4/5 | 4/5 | +0 | FAIL |
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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are thorough and hit all four expectations with correct findings and concrete fixes; they are comparable in quality. | claude-sonnet-5: Both reports are highly thorough and hit all four expectations with concrete, correct fixes; Report 2 additionally ties findings to an internal 'project documentation' guardrail framework, but substantively the two are comparable in coverage and correctness.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 2/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully nail (a) and (b), but Report 2 additionally satisfies (c) and (d) by endorsing same-commit doc updates and recommending dropping the hardcoded webhook count, making it the stronger review. | claude-sonnet-5: Both reports are strong and nearly identical on findings (a)-(c), but Report 2 fulfills expectation (d) by explicitly recommending dropping the hardcoded count in favor of pointing to the source code, while Report 1 merely updates the count from 4 to 5 without addressing future drift.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both answer the core capacity/routing question equally well, but Report 1 answers the task better overall by also flagging the ~3-hour-stale snapshot and the need to re-check live limits, which Report 2 omits. | claude-sonnet-5: Report 1 covers all four expectations, including flagging the usage snapshot's staleness and the need to recheck live limits; Report 2 matches on (a)-(c) but never questions the snapshot's freshness, instead raising an unrelated caveat about ridgeline's undocumented pricing/rate-limits.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and comparable on (a), (b), and (d), but Report 1 answered better overall because it correctly flagged that erasing consent_receipts destroys proof-of-consent (expectation c), which Report 2 missed by declaring erase_user.py correct. | claude-sonnet-5: Report 1 correctly identifies that erase_user.py's deletion of consent_receipts is the actual defect, fully satisfying expectation (c), while Report 2 mistakenly praises erase_user.py for "getting this right" and never flags the deleted consent_receipts as a preservation problem, missing (c); both reports are otherwise comparable and strong on (a), (b), and (d).

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports nail (a), (b), and (c); Report 1 additionally recommends a global/env-level gate (d) that Report 2 misses, making Report 1 slightly more complete. | claude-sonnet-5: Report 1 covers all four expectations including the missing global/env-level gate point (d), while Report 2 omits that point entirely, making Report 1 more complete overall.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with solid evidence; they are comparable, with Report 1 marginally more thorough (extra 40%/SMS and production-data caveats). | claude-sonnet-5: Both reports hit all four expectations with solid evidence; Report 2 additionally flags the false 'production data' caption and unimplemented-but-existing SMS wiring nuance, making it marginally more thorough, but the two are comparable in quality overall.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly answer all three questions with equivalent grounding; they are comparable, with Report 1 marginally more detailed on the reset workflow but no substantive difference. | claude-sonnet-5: Both reports are substantively equivalent and correctly hit all three expectations with nearly identical mechanisms and fixes; Report 1 adds a bit more (e.g., git blame showing the leak is not a regression), while Report 2 adds a slightly clearer note that cedar_app is currently unused by the app — neither difference affects expectation coverage.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with correct code citations and reasoning; they are comparable, with Report 1 slightly more explicit on renormalization and Report 2 adding the observation that the gate logic is unimplemented. | claude-sonnet-5: Both reports hit all four expectations with solid code citations and clear reasoning; Report 1 states the gate-vs-optional distinction (d) somewhat more crisply and decisively, while Report 2 adds a useful (if tangential) observation that the README's gating logic isn't actually implemented in code — overall comparable quality.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports discover the prior reverted attempt, cite the commits and the exact connection-exhaustion cause, and tie the sign-off recommendation to that evidence — they are comparable, with Report 2 adding a slightly stronger revert-commit quote and Report 1 slightly stronger on not proceeding unilaterally. | claude-sonnet-5: Both reports strongly hit a, b, and d with concrete commit citations and PLAT-31-grounded sign-off recommendations, and both miss (c) by not explicitly framing the current container deployment as a deliberate, intentional state versus the removed serverless config; report 2 is slightly more precise on evidence (quoting the actual revert message) but the two are comparable overall.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with accurate, well-cited git reasoning; they are comparable, with Report 2 adding a test-suite and force-push caveat and Report 1 adding merge-conflict analysis. | claude-sonnet-5: Both reports hit all four expectations with comparable depth; Report 2 is marginally more rigorous (blob-hash verification, explicit merge-base freshness check, test-suite and force-push considerations), but Report 1 is equally correct and complete.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both cover (a)-(c) equally well; Report 2 edges ahead by explicitly tying the fixed conftest RESULTS_DB path to parallel-run collision and prescribing an override, satisfying (d) where Report 1 hedges. | claude-sonnet-5: Report 2 is stronger overall: both reports match on grouping/ordering and flagging F-06 as a policy decision, but Report 2 clearly recommends overriding RESULTS_DB to prevent parallel test collisions while Report 1 hedges that the DB "isn't currently read by any test," undercutting that expectation.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 2/3, loaded 3/3, threshold 2: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | MISS | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 answered better: it caught both the cross-tenant leak and the exports.py nightly_export runtime break, while Report 2 caught only the leak and missed the exports.py regression. | claude-sonnet-5: Report 1 is stronger overall: it hits all three expectations, including the exports.py breaking-change defect that Report 2 misses entirely.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 4/5, loaded 5/5, threshold 4: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | MISS | HIT |

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports nail the root cause, commit, and query/policy fixes; Report 1 is slightly stronger because it also recommends a blocking boot-time role-privilege assertion (expectation e), which Report 2 omits. | claude-sonnet-5: Report 1 fully covers all five expectations (including explicitly tying the ROTA-214 commit to all three config files and adding a boot-time role-privilege check), while Report 2 misses the multi-file commit attribution and omits any startup/boot-time enforcement check, relying only on CI/lint/review gates.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly equivalent, but Report 1 edges ahead by including a concrete multi-run reproducibility check for the regenerated golden file, which Report 2 omits. | claude-sonnet-5: Report 1 is stronger: it explicitly verifies golden-file reproducibility by re-running the comparison test twice, a concrete check report 2 never performs (report 2 mentions the dict/set-ordering instability source but dismisses it and only re-runs pytest once).

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with precise file/line citations; Report 1 is marginally more complete (explicit prod-build fix and OIDC id-token gap), but they are comparable. | claude-sonnet-5: Both reports hit all four expectations with substantively equivalent findings; Report 1 is slightly more precise/actionable (explicit removal calls for the legacy secret and explicit corrected tfvars line for the OIDC fix), while Report 2 leaves the legacy-secret fix as a replacement rather than removal and states the OIDC fix implicitly rather than explicitly.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with essentially equivalent, correct analysis; they are comparable. | claude-sonnet-5: Both reports are nearly identical in substance and hit all four expectations with comparable evidence and rigor; report 2 adds a slightly stronger point about the risk of reverting the migration commit, but neither explicitly proposes an isolated shadow-run/offline verification method for expectation (d).

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 4/5, loaded 4/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | MISS | MISS |

Judge comparative verdict (no score weight): claude-opus-4-8: The two reports are comparable: both correctly hit expectations (a)–(d) with proper citations and both miss the structural mis-ordering/restructuring point (e). | claude-sonnet-5: Both reports cover the same core factual findings (a-d) essentially equally well with accurate citations; neither explicitly flags the draft's mis-ordering (leading with self-congratulation, remediation deferred to the final sentence) as required by expectation (e).

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
- Scrub substitutions: 66
- Workspace mutation warnings: csh-t1-loaded, mabc-t2-cold, mabc-t2-loaded, pmvg-t2-cold, pmvg-t2-loaded, sysdbg-t2-cold, sysdbg-t2-loaded

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
