# A/B eval report: lattice-opus-high-v2

- Consumer model: claude-opus-4-8
- Consumer effort: high
- Consumer models effective: claude-haiku-4-5-20251001, claude-opus-4-8
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.207 (Claude Code)
- Seed: 18338661954751828545
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 89.5 s

## Aggregate

Cold 61/68 (89.7%) | Loaded 67/68 (98.5%) | Delta +6

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 9 of 204 must-hit marks (4.4%) carried a disputed report slot.

Adjudication: 11 of 408 report-slot marks disputed; 11 adjudicated by claude-fable-5 at --effort medium (2.7% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 7, report_2 4; by arm: cold 7, loaded 4.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 59/68 (86.8%) | 67/68 (98.5%) | +11.8 |
| r2 | 60/68 (88.2%) | 66/68 (97.1%) | +8.8 |
| r3 | 61/68 (89.7%) | 67/68 (98.5%) | +8.8 |

Endpoint mean over repeats: cold 88.2% | loaded 98.0% | delta +9.8 pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 3/3 | 3/3 | +0 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 4/4 | 4/4 | +0 | FAIL |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 4/5 | 5/5 | +1 | PASS |
| campaign-execution/multi-agent-batch-campaigns | 1 | 2/4 | 4/4 | +2 | PASS |
| change-control/git-change-control-for-agents | 1 | 4/4 | 3/4 | -1 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 4/4 | 4/4 | +0 | FAIL |
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

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with concrete file/function citations and fixes; they are comparable, with Report 2 marginally crisper on the fail-closed prescriptions. | claude-sonnet-5: Both reports fully and equivalently identify all four core defects with concrete fixes; Report 1 adds extra context (compliance/region-locking, lifetime-cap counter issue, batch error-isolation gap) while Report 2 adds test-coverage gaps and cites project-doc guardrails more explicitly — overall comparable in substance.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with accurate, well-cited findings; they are comparable, with Report 2 adding commit-level provenance and Report 1 slightly crisper on rejecting deferral. | claude-sonnet-5: Both reports hit all four expectations accurately and thoroughly, citing correct file paths and line numbers; Report 2 adds extra supporting detail via git commit history but both are functionally comparable in substance and correctness.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with correct numbers and citations; comparable, with Report 2 adding a model-change caveat and Report 1 adding reset-timing analysis. | claude-sonnet-5: Both reports independently hit all four expectations with essentially equivalent numbers and reasoning; Report 2 adds a bonus caveat about the model change (nimbus-large vs atlas-mini) not required by the expectations, but overall the two are comparable in substance.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 answered better: it matches Report 2 on (a), (b), and (d) but correctly identifies that consent_receipts should be preserved as proof of consent (c), whereas Report 2 concludes deleting it is acceptable and misses that requirement. | claude-sonnet-5: Report 1 correctly identifies that erase_user.py wrongly deletes consent_receipts (the PII-free proof-of-consent that should be preserved), matching expectation (c) precisely; Report 2 instead argues consent_receipts deletion is defensible and misdirects preservation praise toward consent_audit (which the erase job doesn't even touch), missing (c). Both reports are equally strong and correct on (a), (b), and (d).

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 2 is slightly better: both nail the default/copy-paste findings, but only Report 2 flags the missing global/env-level gate (expectation d). | claude-sonnet-5: Both reports are strong and nearly identical in substance for questions 1-3, but Report 2 additionally identifies the missing global/environment-level kill switch and recommends adding one, which Report 1 omits.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with equivalent, well-grounded evidence; they are comparable. | claude-sonnet-5: Both reports hit all four expectations with nearly equivalent evidence and rigor; they are comparable in substance, with report 2 slightly more concise and report 1 slightly more exploratory in caveats.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly answer all three questions with the same root causes, fixes, and specific files; they are comparable. | claude-sonnet-5: Both reports correctly and thoroughly identify the same root causes and fixes for all three expectations; Report 2 adds slightly more explicit detail (e.g., docker-entrypoint-initdb.d absence, repo disambiguation) but both are comparable in substance and completeness.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): c, d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations; Report 1 is slightly more thorough (explicit renormalization and CSV-schema fixes), but they are comparable in substance. | claude-sonnet-5: Report 1 is stronger: it explicitly proposes different handling for the two cases—renormalize-and-keep for a failed relevance/tone (non-load-bearing) versus never-emit-a-comparable-composite for a failed accuracy (gate) axis—fully satisfying expectation (d), while Report 2 argues accuracy failures are worse but converges both cases on the same retry-or-mark-incomplete remedy without distinguishing handling.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully satisfy all four expectations with strong grounding in the git history; they are comparable, with Report 2 slightly crisper on stakeholder roles. | claude-sonnet-5: Both reports independently discovered the same prior PLAT-31 attempt/revert, cited the same commits and root cause, and gave equivalent sign-off recommendations — the two are comparable in substance, with Report 2 slightly more explicit about the connection-pooler prerequisite and Report 1 slightly more explicit about the "deliberate revert" framing.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 3/4, threshold 3: FAIL (regression)

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | MISS |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: The reports are comparable: both correctly identify main as base, the weighted-scorer origin and its #42 landing, and the range-rebase fix, and both make the same omission on expectation (c) by claiming the net file diff is clean rather than reporting scorer.py re-appearing. | claude-sonnet-5: Both reports are nearly equivalent in substance and structure (same commands, same conclusions on base branch, ancestry, and rebase plan); neither explicitly reports scoring/scorer.py re-appearing in the main-diff, both instead claiming the diff is clean — a shared miss on expectation (c).

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 2/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | MISS | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): b

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 answered better: it matches Report 2 on registry ownership and F-06 escalation, but additionally states the F-11-early concurrent staging and the shared RESULTS_DB corruption risk that Report 2 only mentions in passing. | claude-sonnet-5: Report 1 hits all four expectations cleanly (including the shared-file registry.py handling, the early-concurrent placement of F-11, F-06 escalation, and the RESULTS_DB collision risk with a concrete mitigation), while Report 2 misses on keeping F-11 concurrent in the early stage (it sequences F-11 into a later "Wave 2") and only vaguely flags RESULTS_DB as something testers "may need," without stating the collision/corruption risk or that a separate checkout alone is insufficient.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 is stronger: it catches the exports.py signature-break regression that Report 2 misses, while both nail the cross-tenant leak and correctly handle the SQL-injection string. | claude-sonnet-5: Report 1 is more complete — it catches both the cross-tenant leak (a) and the exports.py runtime-breaking signature mismatch (b), while Report 2 only catches (a) and mentions build_appointment_query is used by nightly_export without noting the broken call signature; both correctly avoid over-flagging the SQL string as exploitable injection (c).

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 4/5, loaded 5/5, threshold 4: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly equivalent on root cause, commit, and remediation; Report 1 edges ahead by also recommending an explicit application-layer tenant filter as an independent second isolation layer, which Report 2 omits. | claude-sonnet-5: Report 1 covers all five expectations including the app-level tenant-filter defense-in-depth recommendation, while Report 2 misses that one point (d) and otherwise matches Report 1 closely.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations and reach the same conclusions; Report 2 is marginally stronger on reproducibility by explicitly re-running "at least twice," making them essentially comparable. | claude-sonnet-5: Both reports are strong and nearly identical in substance on points a-c, but Report 2 explicitly performs and states a reproducibility check (re-running twice to confirm determinism) alongside naming the set-ordering instability source, while Report 1 only flags the instability risk without describing a verification action — making Report 2 more complete overall.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with precise file/line citations; they are comparable, with Report 1 marginally sharper on the shadow-sink removal semantics and Report 2 adding extra pipeline gaps. | claude-sonnet-5: Both reports hit all four expectations with comparable depth; Report 1 is slightly more decisive on the legacy_billing_secret_arn removal while Report 2 hedges on it, but this doesn't change the category-level outcome since expectation (a) only requires two of four categories from each.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are essentially equivalent, hitting all four expectations with the same root cause, commit, and reasoning; they are comparable. | claude-sonnet-5: Both reports independently and correctly nail all four expectations with nearly identical technical substance; Report 2 is marginally sharper on point (d) by explicitly invoking the 'shared environment' framing, but the difference is minor.

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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports HIT all five expectations with correct citations; they are comparable, with Report 2 slightly more thorough on additional issues. | claude-sonnet-5: Both reports hit all five expectations with essentially equivalent citations; Report 2 is somewhat more thorough overall (e.g., catching the unsupported 'traffic rerouted' claim and the narrow remediation scope) but this doesn't affect coverage of the graded expectations, so the two are comparable on the scored criteria.

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
- Scrub substitutions: 38
- Workspace mutation warnings: csh-t1-cold, eval-harness-t1-r1-cold, mabc-t2-cold, mabc-t2-r1-cold, mmar-t1-loaded, mmar-t1-r1-loaded, pmvg-t2-cold, pmvg-t2-loaded, pmvg-t2-r1-cold, pmvg-t2-r1-loaded, pmvg-t2-r2-cold, pmvg-t2-r2-loaded, sysdbg-t2-cold, sysdbg-t2-loaded, sysdbg-t2-r1-cold, sysdbg-t2-r1-loaded, sysdbg-t2-r2-cold, sysdbg-t2-r2-loaded

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
