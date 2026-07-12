# A/B eval report: lattice-sonnet-low

- Consumer model: claude-sonnet-5
- Consumer effort: low
- Consumer models effective: claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 16502713398184676395
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 121.2 s

## Aggregate

Cold 56/68 (82.4%) | Loaded 66/68 (97.1%) | Delta +10

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 8 of 204 must-hit marks (3.9%) carried a disputed report slot.

Adjudication: 10 of 408 report-slot marks disputed; 10 adjudicated by claude-fable-5 at --effort medium (2.5% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 6, report_2 4; by arm: cold 7, loaded 3.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 58/68 (85.3%) | 66/68 (97.1%) | +11.8 |
| r2 | 59/68 (86.8%) | 66/68 (97.1%) | +10.3 |
| r3 | 56/68 (82.4%) | 64/68 (94.1%) | +11.8 |

Endpoint mean over repeats: cold 84.8% | loaded 96.1% | delta +11.3 pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 2/3 | 2/3 | +0 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 3/4 | 4/4 | +1 | PASS |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 4/5 | 5/5 | +1 | PASS |
| campaign-execution/multi-agent-batch-campaigns | 1 | 3/4 | 4/4 | +1 | PASS |
| change-control/git-change-control-for-agents | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 3/4 | 4/4 | +1 | PASS |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 3/4 | 3/4 | +0 | FAIL |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 3/4 | 4/4 | +1 | PASS |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 3/4 | 4/4 | +1 | PASS |
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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four core expectations; Report 2 is marginally stronger for decisively prescribing fail-closed on the Redis path, while Report 1 hedges there, but they are broadly comparable. | claude-sonnet-5: Report 2 is stronger overall — it commits to explicit, unhedged fixes for every issue (notably fail-closed on Redis error), whereas Report 1 hedges on the rate-limiter fail-open behavior instead of recommending denial.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports cover (a), (b), and (c) equally well, but Report 1 additionally recommends dropping the hardcoded webhook count in favor of pointing at the code, making it slightly stronger. | claude-sonnet-5: Both reports are very close on findings (a), (b), and (c), but Report 1 fully satisfies (d) by recommending dropping the hardcoded count in favor of pointing at the source code, while Report 2 merely proposes updating the count to a new fixed number (5), missing that part of the expectation.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 3/4, loaded 3/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | MISS |

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both correctly diagnose the northpeak shortfall and reroute to ridgeline/secondary, and both omit the snapshot-staleness/re-check caveat (d). | claude-sonnet-5: Both reports are substantively equivalent in content and coverage — both correctly compute the ~9.36M token requirement, identify northpeak's 640K shortfall, recommend switching to ridgeline/secondary, and decline to run the default script unmodified; neither notes the snapshot's staleness (generated_at) or recommends re-checking live limits.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 answered the task better overall, chiefly because it firmly concluded consent_receipts should be preserved as durable proof, whereas Report 1 hedged and misdirected the preservation point to consent_audit. | claude-sonnet-5: Report 2 answered more completely and precisely, especially on Q3 where it unambiguously identifies that erase_user.py's deletion of consent_receipts destroys durable proof of consent and should be reverted, whereas Report 1 hedges and never commits to that conclusion.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and comparable on (a)-(c), but Report 2 additionally catches the missing global/environment-level gate (d), making it the more complete answer. | claude-sonnet-5: Report 2 covers all four expectations, including the missing global/deploy-level gate (d), while Report 1 misses that point entirely; Report 2 also catches an extra UI/backend consistency bug not required but reinforcing its analysis.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both hit all four expectations; Report 2 grounds findings more explicitly in the captures.json manifest, while Report 1 states the AI-footer removal more firmly. | claude-sonnet-5: Both reports hit (a), (b), and (c) with solid evidence; Report 1 clearly hits (d) by stating the AI-assistance footer must be removed, while Report 2 explicitly declines to recommend removal and defers to the owner instead, making Report 1 the stronger overall answer.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports correctly identify all three root causes and fixes with specific files; they are comparable, with Report 1 slightly cleaner on the two-role separation but Report 2 adding a useful FORCE RLS belt-and-suspenders note. | claude-sonnet-5: Both reports correctly identify the same root cause, fix, and wipe/rebuild explanation with equivalent specificity; Report 2 adds an extra (optional) FORCE ROW LEVEL SECURITY suggestion but this doesn't change the substance—overall the two are comparable in quality and completeness.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with accurate code citations; they are comparable, with Report 1 marginally more explicit on renormalization strategy and Report 2 adding the observation that the accuracy gate isn't implemented at all. | claude-sonnet-5: Both reports hit all four expectations with solid code citations and correct README-grounded reasoning; Report 1 is slightly more explicit and concrete in distinguishing gate-vs-optional axis handling (answer 4 spells out renormalization for relevance/tone vs. hard block for accuracy), while Report 2 is comparably thorough but slightly more hedged ("probably deserve distinct handling").

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports correctly discover the prior reverted Edgerunner attempt, cite the same commits, state the connection-exhaustion root cause, and tie sign-off to the prior attempt; they hit all four expectations. | claude-sonnet-5: Both reports are very similar in substance and quality, correctly identifying the prior Edgerunner attempt, root cause, and recommendation to involve the prior decision-owner; neither explicitly frames the container config as a deliberate reversion versus never-set-up.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 is clearly better: it uses the correct three-dot PR diff to expose that scoring/scorer.py leftover weighted-scorer content is still present, whereas Report 2's two-dot diff wrongly concludes the diff is already clean and misses that scope problem entirely. | claude-sonnet-5: Report 1 correctly identifies that scoring/scorer.py re-appears in the main-diff as duplicated weighted-scorer content (matching expectation c), while Report 2 incorrectly concludes the diff is already clean and entirely pairwise work, missing that key finding — making Report 1 the stronger, more accurate report overall.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and hit (a), (c), and (d); Report 1 edges ahead by correctly placing the missing-test finding F-11 in the early concurrent stage, whereas Report 2 defers all new tests to a final wave and misses (b). | claude-sonnet-5: Report 1 fully satisfies all four expectations, while Report 2 misses (b) by explicitly sequencing F-11 after the fixes rather than concurrently in an early stage (and even contradicts itself by placing F-06 in its first parallel wave despite flagging it as a judgment call in Q3); Report 1 is the stronger, more internally-consistent answer.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 2/3, loaded 2/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | MISS | MISS |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 answered better: it caught both the cross-tenant leak and the exports.py runtime break, while Report 1 missed the export breakage entirely. | claude-sonnet-5: Report 2 is more complete: it catches the same cross-tenant leak and correctly handles the SQL-injection non-issue like Report 1, but additionally identifies the nightly_export breakage in exports.py that Report 1 misses entirely.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 4/5, loaded 5/5, threshold 4: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |
| e | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports correctly diagnose the owner-RLS-exemption root cause, commit, and fix; Report 1 is slightly stronger by also adding the explicit app-level tenant filter (expectation d) that Report 2 omits. | claude-sonnet-5: Report 1 hits all five expectations, including the explicit app-level tenant_id filter as a second isolation layer (d), which Report 2 omits entirely — Report 1 is more complete.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly identical in substance, but Report 2 additionally includes a concrete determinism/reproducibility re-run check before committing, giving it a slight edge. | claude-sonnet-5: Both reports are strong and nearly identical in depth on questions 1-3, but Report 2 explicitly verifies golden-file reproducibility by re-running the test suite multiple times, while Report 1 only diffs the regenerated output once without checking run-to-run stability — making Report 2 the more complete answer.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 is better: it covers all four expectations including the explicit call to confirm the first migration, whereas Report 2 misses the migration-confirmation point and weakens the sink/legacy-secret fixes to 'repoint' rather than remove. | claude-sonnet-5: Both reports cover the same ground thoroughly and nearly tie, but Report 1 explicitly and unambiguously calls for confirming/running the first migration before launch rather than assuming deploy handled it, while Report 2 only notes the claim is unverifiable without making an explicit call to action — giving Report 1 a slight edge.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports correctly identify the config/fixture mismatch, the SCORE-77 commit, the flaky-closure flaw, and reject the model-rollback plan; they are comparable, with Report 2 slightly more precise (line numbers, CI-check suggestion). | claude-sonnet-5: Both reports independently identify the same root cause, commit, reproduction flaw, and recommendation with essentially equivalent rigor; Report 2 adds a bit more depth (classifier determinism, CI-check suggestion) but both fully satisfy all four expectations.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all five expectations with correct citations; they are comparable, with Report 1 adding minor extra process/runbook context and Report 2 being more concise. | claude-sonnet-5: Both reports cover all five expectations with comparable citations and specifics; Report 2 is slightly more explicit about the remediation/impact-ordering issue and folds the SLA-breach disclosure critique in more directly, but the two are essentially equivalent in substance.

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
- Scrub substitutions: 163
- Workspace mutation warnings: git-cc-t2-r1-loaded, git-cc-t2-r2-loaded, git-cc-t2-r3-cold, pmvg-t2-r2-cold, pmvg-t2-r2-loaded, sysdbg-t2-r1-cold, sysdbg-t2-r1-loaded, sysdbg-t2-r2-cold, sysdbg-t2-r3-cold, sysdbg-t2-r3-loaded

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
