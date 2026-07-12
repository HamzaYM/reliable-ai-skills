# A/B eval report: lattice-sonnet-xhigh

- Consumer model: claude-sonnet-5
- Consumer effort: xhigh
- Consumer models effective: claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 13747165006172671680
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 1 consumer / 1 judge
- Wall clock: 1982.6 s

## Aggregate

Cold 59/68 (86.8%) | Loaded 66/68 (97.1%) | Delta +7

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 2 of 68 must-hit marks (2.9%) carried a disputed report slot.

Adjudication: 2 of 136 report-slot marks disputed; 2 adjudicated by claude-fable-5 at --effort medium (1.5% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 1, report_2 1; by arm: cold 2, loaded 0.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 3/3 | 2/3 | -1 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 2/4 | 4/4 | +2 | PASS |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 5/5 | 5/5 | +0 | FAIL |
| campaign-execution/multi-agent-batch-campaigns | 1 | 3/4 | 4/4 | +1 | PASS |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 3/4 | 3/4 | +0 | FAIL |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 3/4 | 4/4 | +1 | PASS |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/consent-and-regulated-data-reference | 1 | 3/4 | 4/4 | +1 | PASS |
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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports cover the router, audit, and salt issues equally well, but Report 2 answers the task better because it unambiguously prescribes failing closed on both rate-limiter bypass paths, whereas Report 1 hedges on the Redis fail-open (calling it a possibly intentional tradeoff and recommending logging over denial). | claude-sonnet-5: Both reports hit all four expectations with concrete, correct fixes; Report 2 is somewhat more rigorous (explicit code fixes, empirical verification claims, and a firmer fail-closed statement for the rate limiter), but the substantive findings are equivalent.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 2/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports nail the gateway boundary violations, the missing external_ref field, and the timing of the doc fix, but Report 1 is better overall because it correctly recommends removing the hardcoded webhook count in favor of pointing at the source of truth, whereas Report 2 just bumps "4" to "5" and re-enshrines the same drift-prone claim. | claude-sonnet-5: Report 1 fully satisfies all four expectations, including explicitly endorsing a going-forward same-commit doc policy and recommending dropping the hardcoded webhook count in favor of pointing at the source; Report 2 hits (a) and (b) but falls short on (c)'s going-forward endorsement and (d)'s recommendation to stop hardcoding the count, merely proposing to update "4" to "5".

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 3/4, loaded 3/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | MISS |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are near-identical on the core findings (9.36M-token run, 640K northpeak headroom, switch to ridgeline/secondary, don't run the default); Report 2 edges ahead by explicitly flagging the snapshot's ~3-hour staleness and the stubbed scoring function, though neither commits to re-checking live limits before launching. | claude-sonnet-5: Both reports are very close on the core token/backend analysis and recommendation, but Report 2 goes further by noting the snapshot's ~3-hour staleness explicitly and, notably, discovers that score_batch.py's scoring and transcript-fetch logic are unimplemented stubs — a significant additional finding neither expectation nor Report 1 surfaces, making Report 2 the stronger overall answer.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and equivalent on the retention-sweep audit-table violation, the missing scheduler entry, and the consent-version publishing plan, but Report 2 answered the task better overall because it alone caught the erase_user.py defect — that deleting the PII-free consent_receipts row destroys the durable proof of consent — which Report 1 incorrectly endorsed as correct behavior. | claude-sonnet-5: Report 2 correctly identifies that erase_user.py's deletion of consent_receipts destroys the durable proof-of-consent record (expectation c), a genuine defect that Report 1 misses entirely by treating the deletion as unremarkable; both reports are otherwise equally strong on the other three expectations.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports nail the default-on behavior, the fix, and the copy-paste provenance from compact_calendar_view_enabled, but only Report 1 identifies the missing environment/deploy-level master gate and recommends adding one, so Report 1 answered the task better overall. | claude-sonnet-5: Both reports are very similar in substance and hit a, b, and c equally well; Report 1 additionally identifies the missing environment/global-level gate and recommends adding one (expectation d), which Report 2 omits, making Report 1 more complete overall.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with equivalent evidence; they are comparable, with Report 2 marginally more precise on line-number citations and Report 1 adding a bit more breadth (missing frontend, image-quality concerns). | claude-sonnet-5: Both reports hit all four expectations with comparable evidence and rigor; report 2 includes slightly more precise line-number citations but the substance is equivalent.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with correct, file-grounded reasoning; they are essentially comparable, with Report 2 slightly ahead for noting that the existing test_uses_app_role check only covers the test connection and proposing a regression guard on the app's own DATABASE_URL. | claude-sonnet-5: Both reports independently identify the same root causes and fixes with comparable depth and accuracy; Report 1 adds slightly more historical git-commit sourcing while Report 2 adds a regression-test suggestion, but neither is substantively stronger against the expectations.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports correctly diagnose the None→0.0 substitution and its corruption of leaderboard means, but Report 2 answered the task better because it alone splits failure handling by axis criticality (renormalize over surviving axes for relevance/tone vs. refuse to emit a comparable composite for the accuracy gate), whereas Report 1 prescribes a uniform exclude-everything rule. | claude-sonnet-5: Both reports correctly diagnose the None→0.0 bug and its ranking consequences, but only Report 2 explicitly distinguishes handling for the gate axis (accuracy, exclude/flag) versus the optional axes (relevance/tone, defensible to renormalize over succeeded axes), which Report 1 treats uniformly (retry-then-exclude for all axes).

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports discover and cite the prior Edgerunner attempt (454a21f/597777b) and its revert (1712565) with the connection-exhaustion root cause, and both tie the recommendation to that history; Report 1 is sharper on ownership/decision-routing while Report 2 adds more codebase-specific risk detail (missing Postgres driver, unbounded join). | claude-sonnet-5: Both reports independently discovered the same prior Edgerunner attempt and revert via git history, cited the same commits, quoted the root cause, and tied their recommendation to involving whoever has context on the prior incident — the two are comparable in meeting all four expectations, with Report 2 slightly more explicit in tracing file-level deletions to the revert commit.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations and are closely comparable; Report 2 is marginally stronger on the explicit origin/main freshness check and the post-rebase confirmation that scoring/scorer.py disappears, while Report 1 adds a useful read-only merge-tree simulation. | claude-sonnet-5: Both reports hit all four expectations with substantively equivalent analysis; Report 2 is marginally more rigorous (explicit --is-ancestor check, explicit origin/main freshness confirmation) but the difference does not change coverage of the expectations.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 answered the task better: both cluster registry.py under one owner, stage the waves, and hold F-06 as a policy decision, but only Report 1 identifies the shared RESULTS_DB path in tests/conftest.py as a cross-engineer collision hazard needing a per-engineer override, while Report 2 explicitly dismisses it as irrelevant. | claude-sonnet-5: Report 1 covers all four expectations solidly, including the RESULTS_DB collision risk with a concrete mitigation (set a private RESULTS_DB path); Report 2 matches on a–c but explicitly dismisses the RESULTS_DB path as irrelevant ("never read... don't need"), missing expectation (d) entirely — so Report 1 answers the task more completely.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 3/3, loaded 2/3, threshold 2: FAIL (regression)

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | MISS |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 answered the task better: both caught the missing tenant filter and both correctly declined to treat the raw-SQL status interpolation as an exploitable injection, but only Report 1 found the second blocker — the now-required `filters` parameter breaking the untouched `nightly_export` caller in backend/app/exports.py. | claude-sonnet-5: Report 1 covers all three expectations (including the exports.py breaking-signature defect), while Report 2 misses the nightly_export/build_appointment_query signature-break defect entirely, making Report 1 the more complete and correct sign-off.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation and are essentially comparable; Report 2 is marginally stronger for explicitly separating owner-exemption from BYPASSRLS/superuser and flagging the unsigned-token vulnerability, while Report 1 is slightly more detailed on the timeline and test remediation. | claude-sonnet-5: Both reports independently hit all five expectations with essentially equivalent depth and correct citations; Report 2 additionally surfaces a bonus finding (unsigned token verification and missing CI) not required by the rubric, giving it a slight edge in thoroughness without any difference in expectation coverage.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and near-identical on the live-test, golden-diff, and stale-docs expectations; Report 1 edges ahead by additionally prescribing a concrete reproducibility check (regenerate twice and diff) for the golden file, which Report 2 only notes as diff noise without acting on. | claude-sonnet-5: Both reports are very similar in depth and correctness; Report 1 edges ahead by explicitly performing a concrete reproducibility check (regenerate twice, diff outputs) for the golden file, whereas Report 2 only names the set-ordering instability source without describing an actual verification action.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations, but Report 1 is stronger on remediation precision — it explicitly calls for removing the shadow-scoring sink and the legacy billing secret ARN rather than re-pointing them, and it states more directly that a real migration step is missing, whereas Report 2 hedges those into "point it at a prod sink" / "use a distinct prod secret" / "unverifiable." | claude-sonnet-5: Both reports are comparably thorough and hit all four expectations with correct file/line citations; Report 1 is marginally crisper on the migration-step call-to-action and the shadow-scoring removal directive, while Report 2 adds extra due-diligence detail (missing package.json, committed tfstate) but hedges slightly more on remediation specifics.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports hit all four expectations with the same root cause, commit attribution, rebuttal of the flakiness closure, and rejection of the model-rollback plan; Report 2 is slightly more granular on the config file's git history, while Report 1 is marginally tighter. | claude-sonnet-5: Both reports correctly identify the root cause, timeline, flakiness rebuttal, and reject the rollback plan with nearly identical rigor and evidence; they are comparable in substance, though neither proposed an isolated verification method (both focused mainly on rejecting the model-rollback plan) for expectation (d), satisfying it via the 'model swap cannot test the actual root cause' clause.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all five expectations with correct file citations; they are comparable, with Report 2 slightly ahead for reconciling the draft's technical narrative against the timeline and runbooks, while Report 1 adds useful cross-repo scoping. | claude-sonnet-5: Both reports hit all five core expectations equally well; Report 2 goes further with additional findings (responded-immediately timing detail, technical narrative reconciliation, and process/git-log evidence of skipped review), making it somewhat more thorough overall.

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
- Scrub substitutions: 67
- Workspace mutation warnings: aicg-t2-loaded, csh-t1-cold, git-cc-t2-cold, git-cc-t2-loaded, pmvg-t2-loaded, sysdbg-t2-cold, sysdbg-t2-loaded

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
