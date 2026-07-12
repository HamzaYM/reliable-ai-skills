# A/B eval report: lattice-opus-max

- Consumer model: claude-opus-4-8
- Consumer effort: max
- Consumer models effective: claude-haiku-4-5-20251001, claude-opus-4-8, claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 7775070654475700752
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 71.0 s

## Aggregate

Cold 63/68 (92.6%) | Loaded 68/68 (100.0%) | Delta +5

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 8 of 204 must-hit marks (3.9%) carried a disputed report slot.

Adjudication: 9 of 408 report-slot marks disputed; 9 adjudicated by claude-fable-5 at --effort medium (2.2% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 4, report_2 5; by arm: cold 8, loaded 1.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 64/68 (94.1%) | 68/68 (100.0%) | +5.9 |
| r2 | 59/68 (86.8%) | 68/68 (100.0%) | +13.2 |
| r3 | 63/68 (92.6%) | 68/68 (100.0%) | +7.4 |

Endpoint mean over repeats: cold 91.2% | loaded 100.0% | delta +8.8 pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 3/3 | 3/3 | +0 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 4/4 | 4/4 | +0 | FAIL |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 5/5 | 5/5 | +0 | FAIL |
| campaign-execution/multi-agent-batch-campaigns | 1 | 3/4 | 4/4 | +1 | PASS |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 3/4 | 4/4 | +1 | PASS |
| docs-and-compliance/consent-and-regulated-data-reference | 1 | 3/4 | 4/4 | +1 | PASS |
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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with correct file/function citations and concrete fixes; they are comparable, with Report 1 slightly more exhaustive on secondary issues and Report 2 more concise with cleaner fix code. | claude-sonnet-5: Both reports hit all four expectations with concrete, well-cited fixes; Report 2 is marginally sharper on expectation (b), explicitly rejecting env-name gating and committing to a fail-closed fix, while Report 1 hedges with 'fail-closed or emit an alert' rather than committing to deny.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are comprehensive and hit all four expectations with correct, well-cited findings; they are comparable. | claude-sonnet-5: Both reports hit all four expectations with comparable rigor and citation quality; Report 2 states the same-commit doc-update policy slightly more explicitly and generally, but the difference is marginal.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both nail the core token/backend analysis, but Report 2 additionally flags the ~3-hour-stale snapshot and re-checking live limits, so it answers the task more completely. | claude-sonnet-5: Report 2 covers everything Report 1 does plus explicitly flags the usage_snapshot's staleness (generated_at vs. current time) and recommends re-checking live limits before relying on it, which Report 1 omits entirely.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both are strong and comparable, but Report 1 answers better because it firmly states the consent_receipts row should be preserved (expectation c), whereas Report 2 hedges and pivots to consent_audit. | claude-sonnet-5: Report 1 fully satisfies all four expectations, including correctly identifying consent_receipts as the record that should be preserved after erasure; Report 2 misses expectation (c) by explicitly declining to commit to consent_receipts as a must-preserve table, treating it as a mere judgment call instead.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with accurate citations; they are comparable, with Report 1 marginally more detailed but not materially better. | claude-sonnet-5: Both reports hit all four expectations with nearly identical substance and citations; Report 1 additionally verifies claims empirically and adds more gating details (UI mismatch, stub messaging client), while Report 2 adds idempotency/dedup concerns — comparable quality overall.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with equivalent, well-grounded evidence; they are comparable. | claude-sonnet-5: Both reports hit all four expectations with comparable rigor and evidence; Report 2 is slightly more precise on code citations (line numbers) and gives a more actionable fix recommendation for the scheduling image, but the substance is equivalent.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully satisfy all three expectations with correct root causes, the two-role fix, and the bootstrap explanation; they are comparable, with Report 1 and Report 2 essentially equivalent in substance. | claude-sonnet-5: Both reports correctly and thoroughly identify all three root causes with equivalent depth and file-level evidence; Report 2 adds a useful extra note about the bootstrap script's non-idempotency, but both fully satisfy all expectations.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and cover a-c equally, but Report 1 answered better overall by explicitly distinguishing gate-vs-optional axis failure handling (expectation d), which Report 2 collapses into a uniform withhold-all rule. | claude-sonnet-5: Both reports hit all four expectations with correct code citations and equivalent substance; Report 2 is marginally stronger, empirically validating the bimodal deflation pattern against the actual scores.csv and noting the gate threshold isn't actually implemented in code, but the difference is minor.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with well-cited commit history; they are comparable, with Report 2 slightly more thorough on packaging/driver gaps. | claude-sonnet-5: Both reports hit all four expectations with strong commit-level evidence; Report 2 is slightly more thorough (e.g., noting the ASGI mismatch in serverless_handler.py and the driver gap), but on the graded expectations they are essentially comparable.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with correct commands and reasoning; they are comparable, with Report 1 slightly more exhaustive but no substantive difference in coverage. | claude-sonnet-5: Both reports independently reach the same correct conclusions (target main, trace to feat/weighted-scorer/#42, diagnose scorer.py contamination, rebase --onto with freshness verification) and hit all four expectations; Report 1 is marginally more thorough (e.g., explicitly notes the origin ref for feat/weighted-scorer still exists) but the substantive content is comparable.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong on grouping, ordering, and F-06, but Report 2 additionally nails the shared RESULTS_DB test-database collision risk that Report 1 only mentions weakly, making Report 2 the better answer overall. | claude-sonnet-5: Report 2 more clearly and completely addresses the shared RESULTS_DB collision risk (expectation d) with explicit corruption/interference framing and a per-engineer override requirement, while both reports are comparable on the other three expectations.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all three expectations with correct, well-grounded reasoning; they are comparable, with Report 2 marginally more thorough but no difference in scored outcomes. | claude-sonnet-5: Both reports hit all three expectations with essentially equivalent substance; Report 2 is somewhat more thorough (notes the vacuous test coverage and additional non-blocking issues) but this doesn't affect the graded expectations, making the two comparable.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with correct mechanism and citations; Report 2 is marginally richer (notes tenants table lacks RLS, quotes the stub test) but they are comparable. | claude-sonnet-5: Both reports independently hit all five expectations with essentially equivalent accuracy and citations; Report 2 is marginally more thorough (flags the unprotected `tenants` table and additional secondary findings) but this doesn't change expectation coverage — the two are comparable in quality.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with strong repository grounding; they are comparable, with Report 2's per-check table and Report 1's explicit hand-recomputation being roughly equivalent strengths. | claude-sonnet-5: Both reports hit all four expectations with substantively similar depth; Report 2 states the reproducibility check slightly more explicitly ('confirm it's stable across repeated runs') while Report 1 demonstrates it via PYTHONHASHSEED variation, making the two reports comparable overall.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): b, c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations and are closely comparable; Report 2 is marginally stronger on the migration gap and on explicitly calling for removal of the legacy secret. | claude-sonnet-5: Report 2 is stronger: it hits all four expectations explicitly (including an explicit recommendation to build a prod-specific frontend artifact), while Report 1 misses the explicit recommendation piece of expectation (b), only describing the problem without stating the fix.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports correctly and thoroughly hit all four expectations; they are comparable, with Report 1 slightly more complete on the isolation/verification guidance. | claude-sonnet-5: Both reports independently reach the same correct diagnosis, root cause, culprit commit, and rejection of the flakiness explanation with near-identical supporting evidence; they are comparable in substance, with Report 1 slightly more explicit about a 'no flip on shared/production job' policy and Report 2 slightly tighter and more concise.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with correct citations and near-identical substance; they are comparable. | claude-sonnet-5: Both reports hit all five expectations with near-identical evidence and citations; Report 1 additionally catches an unsupported "untested" claim and a reroute-vs-rollback inconsistency, while Report 2 adds a date-check and a supporting remediation-thinness note — overall comparable in coverage, with Report 1 slightly more thorough in enumerating style-guide violations.

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
- Scrub substitutions: 90
- Workspace mutation warnings: csh-t1-r1-cold, csh-t1-r1-loaded, csh-t1-r2-cold, csh-t1-r2-loaded, csh-t1-r3-cold, csh-t1-r3-loaded, eval-harness-t1-r1-cold, eval-harness-t1-r1-loaded, eval-harness-t1-r2-loaded, eval-harness-t1-r3-loaded, mabc-t2-r1-loaded, mabc-t2-r2-cold, mabc-t2-r3-cold, mmar-t1-r3-loaded, pmvg-t2-r1-cold, pmvg-t2-r1-loaded, pmvg-t2-r2-loaded, pmvg-t2-r3-cold, pmvg-t2-r3-loaded, sysdbg-t2-r1-cold, sysdbg-t2-r1-loaded, sysdbg-t2-r2-cold, sysdbg-t2-r2-loaded, sysdbg-t2-r3-cold, sysdbg-t2-r3-loaded

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
