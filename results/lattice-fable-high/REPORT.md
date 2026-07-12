# A/B eval report: lattice-fable-high

- Consumer model: claude-fable-5
- Consumer effort: high
- Consumer models effective: claude-fable-5, claude-haiku-4-5-20251001, claude-opus-4-8, claude-opus-4-8[1m], claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 16998705916299329253
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 112.4 s

## Aggregate

Cold 67/68 (98.5%) | Loaded 68/68 (100.0%) | Delta +1

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 9 of 204 must-hit marks (4.4%) carried a disputed report slot.

Adjudication: 10 of 408 report-slot marks disputed; 10 adjudicated by claude-fable-5 at --effort medium (2.5% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 6, report_2 4; by arm: cold 8, loaded 2.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 66/68 (97.1%) | 68/68 (100.0%) | +2.9 |
| r2 | 66/68 (97.1%) | 68/68 (100.0%) | +2.9 |
| r3 | 67/68 (98.5%) | 68/68 (100.0%) | +1.5 |

Endpoint mean over repeats: cold 97.6% | loaded 100.0% | delta +2.4 pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 3/3 | 3/3 | +0 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 4/4 | 4/4 | +0 | FAIL |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 5/5 | 5/5 | +0 | FAIL |
| campaign-execution/multi-agent-batch-campaigns | 1 | 4/4 | 4/4 | +0 | FAIL |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/consent-and-regulated-data-reference | 1 | 4/4 | 4/4 | +0 | FAIL |
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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent specificity, fixes, and file/function citations; they are comparable. | claude-sonnet-5: Both reports independently identify all four core defects and prescribe essentially the same fixes with comparable rigor; Report 2 is slightly crisper on the rate-limiter fail-closed recommendation, but overall the two are comparable in coverage and correctness.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both are near-identical and correct on a, b, and d; Report 2 answers slightly better because it explicitly endorses the going-forward practice of updating docs in the same commit as the code, which Report 1 omits. | claude-sonnet-5: Both reports are nearly identical in substance and citations, but Report 2 more explicitly endorses landing doc fixes in the same commit as code going forward, satisfying expectation (c) fully while Report 1 only addresses the immediate timing without stating a forward-looking policy.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with essentially identical substance and correct citations; they are comparable, with Report 1 adding a slight edge via an explicit --limit smoke-test. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent substance; Report 2 additionally flags an unprompted risk (results.jsonl being overwritten) but that doesn't affect the graded expectations, making the two comparable in quality.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent depth and correct citations; they are comparable. | claude-sonnet-5: Both reports hit all four expectations with equivalent substance and correct file/line citations; Report 2 adds a few extra observations (e.g., orphan-user edge case, missing audit-of-erasure gap) but this doesn't change expectation coverage — the two are comparable in quality.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with precise citations and equivalent reasoning; they are comparable in quality. | claude-sonnet-5: Both reports hit all four expectations with comparable rigor; Report 2 adds slightly more precision (malformed-value handling, test specifics, grep verification of all consumers) but both are equally responsive to the task.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with the same grounded evidence; they are comparable, with Report 1 marginally firmer on removing the AI-assistance footer. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent evidence and rigor; they are comparable in quality.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are comprehensive and hit all three expectations with equivalent grounding; they are comparable. | claude-sonnet-5: Both reports are substantively equivalent and correctly satisfy all three expectations; Report 1 adds a git-history citation while Report 2 adds a bonus catch about a pooled-connection tenant-setting/leak bug in deps.py, but this does not change expectation coverage.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): c, d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly equivalent, but Report 1 answers better because it correctly distinguishes handling for the gate axis versus the optional axes (expectation d), whereas Report 2 explicitly argues they need no different handling. | claude-sonnet-5: Report 1 answers all four expectations, correctly distinguishing the gate axis (accuracy) from the optional axes and prescribing that a failed accuracy call must not be written as a completed score, while Report 2 explicitly rejects that distinction and treats all three axes identically, missing expectations (c) and (d).

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports hit all four expectations, correctly citing the prior reverted attempt and its recorded cause; Report 2 is marginally more thorough (naming the deleted files and adding alternatives), but neither answers the task meaningfully better. | claude-sonnet-5: Both reports hit all four expectations with comparably strong, commit-cited evidence; Report 2 goes slightly further diagnosing the broken shim and explicitly calling the serverless files 'deleted', but overall the two are substantively comparable in quality.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly answer all four questions with equivalent command-level evidence; they are comparable. | claude-sonnet-5: Both reports independently satisfy all four expectations with concrete, correctly-cited git evidence; Report 1 adds a cherry -v patch-equivalence check while Report 2 adds a reflog-based provenance check and a cleanup suggestion, making them comparable in quality.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with comparable substance and specificity; they are roughly equal, with Report 1 slightly more detailed on setup and Report 2 slightly cleaner on the isolated-checkout-plus-RESULTS_DB distinction. | claude-sonnet-5: Both reports hit all four expectations with comparable substance; Report 2 states the RESULTS_DB collision risk slightly more directly and separates checkout isolation from DB isolation more explicitly, and also catches the pre-existing failing test test_full_credit as an added coordination risk, but the core expectations are met equivalently by both.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all three expectations; Report 2 is somewhat more thorough on corroboration but the two are comparable on the graded expectations. | claude-sonnet-5: Both reports correctly identify the cross-tenant leak and the broken nightly export, and both correctly avoid over-flagging the interpolated status string as exploitable; Report 2 is more rigorous and thorough overall (adds a plausible serialization/500 defect, an adversarial-verification methodology, and cleanly separates the SQL-interpolation issue into non-blocking), while Report 1 is more concise but muddies the SQL-injection point by still listing it under 'Merge-blocking defects.'

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with accurate, well-cited diagnoses; they are essentially comparable, with Report 1 adding a bonus auth-token finding. | claude-sonnet-5: Both reports are substantively equivalent, hitting all five expectations with nearly identical citations and reasoning; Report 1 additionally flags an unrelated auth-token forgery vulnerability, but this does not affect coverage of the stated expectations.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and hit all four expectations; Report 1 is marginally more thorough on reproducibility (explicit re-run-twice check plus verified nondeterminism), but they are essentially comparable. | claude-sonnet-5: Both reports hit (a), (b), and (c) with comparable depth, but Report 1 additionally satisfies (d) with a concrete multi-run reproducibility check plus the instability-source diagnosis, while Report 2 only names the instability source without describing an actual reproducibility verification, making Report 1 the stronger overall answer.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with correct file/line citations and equivalent fixes; they are comparable, with Report 1 marginally more explicit on removing the shadow sink and confirming migrations. | claude-sonnet-5: Both reports are highly thorough and hit all four expectations with nearly identical evidence and file/line citations; report 1 is marginally more decisive on the legacy secret ARN (explicitly calling for removal) while report 2 is marginally more nuanced on the shadow-scoring sink, but overall the two are comparable in quality and completeness.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are essentially equivalent, hitting all four expectations with the same root cause, commit, and reasoning; Report 1 is marginally stronger for explicitly proposing a shadow/parallel evaluation as the isolated verification path. | claude-sonnet-5: Both reports independently reach the same correct diagnosis and hit all four expectations equally well; Report 1 is marginally stronger on (d) by explicitly proposing a shadow/parallel evaluation as the isolated verification method, while Report 2 only argues the model-swap can't test the root cause.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all five expectations with correct citations and near-identical substance; they are comparable. | claude-sonnet-5: Both reports hit all five expectations with proper file citations; Report 1 surfaces additional findings (unsupported rerouting claim, process-flow ADR) while Report 2 more concisely ties contradictions together (e.g., noting the draft's own rollback line contradicts its rerouting claim) — overall comparable quality with a slight edge to Report 1 for breadth.

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
- Scrub substitutions: 37
- Workspace mutation warnings: csh-t1-r1-cold, csh-t1-r3-cold, mabc-t2-r1-loaded, mmar-t1-r2-cold, pmvg-t2-r1-loaded, pmvg-t2-r2-loaded, pmvg-t2-r3-cold, pmvg-t2-r3-loaded, sysdbg-t2-r1-loaded, sysdbg-t2-r2-cold, sysdbg-t2-r2-loaded, sysdbg-t2-r3-cold, sysdbg-t2-r3-loaded

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
