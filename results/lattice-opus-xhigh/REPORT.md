# A/B eval report: lattice-opus-xhigh-v2

- Consumer model: claude-opus-4-8
- Consumer effort: xhigh
- Consumer models effective: claude-haiku-4-5-20251001, claude-opus-4-8, claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.207 (Claude Code)
- Seed: 11942927258849618434
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 83.7 s

## Aggregate

Cold 64/68 (94.1%) | Loaded 68/68 (100.0%) | Delta +4

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 6 of 204 must-hit marks (2.9%) carried a disputed report slot.

Adjudication: 7 of 408 report-slot marks disputed; 7 adjudicated by claude-fable-5 at --effort medium (1.7% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 5, report_2 2; by arm: cold 4, loaded 3.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 61/68 (89.7%) | 67/68 (98.5%) | +8.8 |
| r2 | 64/68 (94.1%) | 68/68 (100.0%) | +5.9 |
| r3 | 61/68 (89.7%) | 67/68 (98.5%) | +8.8 |

Endpoint mean over repeats: cold 91.2% | loaded 99.0% | delta +7.8 pp.

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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with correct findings and concrete fixes; they are comparable in substance and quality. | claude-sonnet-5: Both reports hit all four expectations with comparable depth and concrete fixes; Report 2 ties findings more explicitly to stated project guardrails, but substantively they are on par.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with accurate, well-cited findings; they are comparable in quality. | claude-sonnet-5: Both reports hit all four expectations with substantively equivalent, well-cited answers; Report 2 adds a slightly sharper distinction in (c) between the code-owed doc fix and the code-owed invariant fix, but overall the two are comparable in coverage and quality.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly identical on questions 1-3, but Report 1 additionally flags the snapshot as stale and commits to re-checking live limits, making it the more complete answer. | claude-sonnet-5: Both reports are accurate and thorough and hit (a), (b), and (c) equally well; Report 1 additionally flags the snapshot's staleness and explicitly commits to re-checking live limits before relying on it (expectation d), which Report 2 omits (it only notes generated_at for reset-timing math, not as a call to re-verify), making Report 1 the more complete answer.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with correct citations; Report 1 is slightly crisper on the consent_receipts defect while Report 2 hedges it as a policy question, but they are comparable overall. | claude-sonnet-5: Both reports hit all four expectations with solid schema/file citations; Report 1 is more decisive on the erase_user.py consent_receipts issue (calling it a clear defect with a concrete fix) while Report 2 hedges it as a policy question for legal, but both state the core substance, making the two reports comparable in coverage.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and equivalent on (a)-(c), but Report 2 additionally identifies the missing global/environment-level gate and recommends adding one, making it the better answer overall. | claude-sonnet-5: Both reports are strong and nearly identical on (a)-(c), but only Report 2 identifies the missing global/deploy-level gate and recommends adding one, giving it the edge overall.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with equivalent evidence and grounding; they are comparable. | claude-sonnet-5: Both reports are thorough and hit all four expectations with solid evidence; Report 2 is slightly more concise while Report 1 adds a few extra flagged items (production-data privacy concern, unsubstantiated stat) — overall comparable quality.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and accurately answer all three questions with the same root cause, fix, and wipe explanation; they are comparable, with Report 2 slightly more explicit about docker-entrypoint-initdb.d. | claude-sonnet-5: Both reports are comparable in substance and correctly hit all three expectations with nearly identical depth and accuracy; Report 2 adds a small extra (WITH CHECK clause suggestion) while Report 1 adds a small extra (SET LOCAL pooled-connection hardening), but neither is required by the expectations.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports correctly diagnose the 0.0-substitution bug and its ranking impact, but Report 1 additionally distinguishes handling of the gate (accuracy) axis from the optional axes, which Report 2 does not. | claude-sonnet-5: Report 1 is more complete: it explicitly proposes a branched remedy (renormalize for relevance/tone failures vs. withhold/flag for accuracy failures), satisfying expectation (d), while Report 2 treats all axis failures uniformly (omit or mark) and never argues that a relevance/tone failure could defensibly still yield a computed score.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with well-grounded commit citations and equivalent recommendations; they are comparable. | claude-sonnet-5: Both reports are very similar in substance — both correctly discover and cite the prior PLAT-31 Edgerunner attempt and revert, correctly attribute the connection-exhaustion root cause to the commit history, and tie their sign-off recommendation to that discovery; neither explicitly cites backend/Dockerfile or frames the container setup as the deliberately-chosen current state, so both miss (c) equally — overall the reports are comparable in quality and completeness.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with correct git evidence and are essentially comparable; Report 2 adds slightly more nuance (functional dependency of pairwise on overlap()), but neither is materially better. | claude-sonnet-5: Both reports are thorough and hit all four expectations with nearly equivalent depth and evidence; Report 2 adds slightly more nuance (e.g., functional dependency of pairwise_preference on overlap()) but the two are comparable in overall quality.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Both cover file-contention grouping, ordering, and F-06/F-08 triage equally well, but only Report 1 correctly identifies the shared RESULTS_DB collision risk, making it slightly stronger overall. | claude-sonnet-5: Report 1 correctly identifies and mitigates the RESULTS_DB collision risk (d) but fails to place F-11 in an early concurrent stage (b); Report 2 does the opposite, nailing the staged ordering but treating RESULTS_DB as inert and missing the collision risk — overall comparable, each missing one of four expectations.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all three expectations with essentially equivalent substance and correctness; they are comparable. | claude-sonnet-5: Both reports hit all three expectations with substantively equivalent, well-corroborated findings; Report 2 adds minor extra detail (tenant enumeration, missing response_model) but this doesn't change expectation coverage.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are excellent and nearly identical on the core diagnosis; Report 1 edges ahead by also recommending an explicit application-layer tenant filter as a second isolation layer, which Report 2 omits. | claude-sonnet-5: Report 1 covers all five expectations including the application-layer tenant-filter defense-in-depth recommendation, while Report 2 misses that point despite otherwise matching on root cause, commit attribution, primary fix, and startup check.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 answered the task better: it matches Report 1 on live-test gating, golden diff-tracing, and stale-doc re-measurement, but additionally catches and defends the regeneration reproducibility issue (set-ordered nondeterminism) that Report 1 misses. | claude-sonnet-5: Report 2 matches Report 1 on the first three expectations but additionally discovers and documents the golden-file reproducibility issue (nondeterministic set ordering) with a concrete twice-run verification, which Report 1 omits entirely — making Report 2 the stronger, more complete answer.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are thorough and hit all four expectations; Report 2 is marginally stronger on explicit fix recommendations (prod build, remove-entirely for the sink and legacy secret), but they are essentially comparable. | claude-sonnet-5: Both reports hit all four expectations with comparable depth and specificity; Report 2 is slightly more rigorous on config hygiene (recommending full omission vs. toggling) and explicitly frames the OIDC issue as a trust-scope violation, but the substantive findings are equivalent.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are essentially equivalent, correctly identifying all four points; Report 2 slightly more explicitly names the shared-runner caution, but they are comparable. | claude-sonnet-5: Both reports are essentially equivalent in substance, correctly identifying the config/schema mismatch, the SCORE-77 commit, the score_one.py reproduction flaw, and dismissing the model-rollback plan; Report 2 slightly more explicitly invokes the shared-environment caution for expectation (d).

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

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 is stronger: it fully nails the SLA-breach point by citing April's 99.77% in uptime-2026.csv against the 99.9% monthly SLA, which Report 1 missed. | claude-sonnet-5: Report 2 covers all five expectations, including the April SLA breach with both required file citations (metrics/uptime-2026.csv and docs/sla-commitments.md); Report 1 only estimates a "likely" breach without citing the actual uptime CSV data, missing expectation (c).

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
- Scrub substitutions: 55
- Workspace mutation warnings: csh-t1-cold, csh-t1-r1-cold, csh-t1-r2-cold, csh-t1-r2-loaded, eval-harness-t1-loaded, eval-harness-t1-r1-loaded, eval-harness-t1-r2-cold, mabc-t2-cold, mabc-t2-r1-cold, mabc-t2-r1-loaded, mabc-t2-r2-cold, pmvg-t2-cold, pmvg-t2-loaded, pmvg-t2-r1-cold, pmvg-t2-r1-loaded, pmvg-t2-r2-cold, pmvg-t2-r2-loaded, sysdbg-t2-cold, sysdbg-t2-loaded, sysdbg-t2-r1-cold, sysdbg-t2-r1-loaded, sysdbg-t2-r2-cold, sysdbg-t2-r2-loaded

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
