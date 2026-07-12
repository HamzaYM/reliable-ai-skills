# A/B eval report: lattice-fable-xhigh

- Consumer model: claude-fable-5
- Consumer effort: xhigh
- Consumer models effective: claude-fable-5, claude-haiku-4-5-20251001, claude-opus-4-8, claude-opus-4-8[1m]
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 2557645624734192265
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 1 consumer / 1 judge
- Wall clock: 36.9 s

## Aggregate

Cold 66/68 (97.1%) | Loaded 68/68 (100.0%) | Delta +2

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 3 of 68 must-hit marks (4.4%) carried a disputed report slot.

Adjudication: 3 of 136 report-slot marks disputed; 3 adjudicated by claude-fable-5 at --effort medium (2.2% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 1, report_2 2; by arm: cold 3, loaded 0.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 3/3 | 3/3 | +0 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 3/4 | 4/4 | +1 | PASS |
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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully hit all four expectations with equivalent depth and correct fixes; they are comparable. | claude-sonnet-5: Both reports hit all four expectations with comparable depth and concrete fixes; Report 2 adds a few extra observations (grep-confirmed absence of imports, per-applicant vs vendor-level quota gap) but neither is clearly stronger on the graded expectations.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly identical on findings, but Report 1 edges ahead by explicitly endorsing the go-forward same-commit doc policy, which Report 2 omits. | claude-sonnet-5: Report 1 is slightly stronger: it explicitly rejects deferring the doc fix to a later cleanup and commits to a going-forward same-commit policy (expectation c), which Report 2 only partially addresses without the explicit rejection/forward-looking policy; otherwise the reports are comparable in depth and accuracy.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with essentially identical substance; comparable, with Report 1 adding a bonus catch about the score_one() stub. | claude-sonnet-5: Both reports hit all four expectations with nearly identical figures and conclusions; Report 1 adds a notable extra observation (score_one() is a stub returning placeholder scores) but this is outside the stated expectations, so the two are comparable in meeting the grading criteria.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with accurate citations; they are comparable, with Report 2 slightly more thorough on evidence (git history) and Report 1 slightly tighter on testability. | claude-sonnet-5: Both reports are comparably thorough and hit all four expectations with equivalent supporting evidence; Report 2 adds slightly more rigor (git history verification, explicit line-removal recommendation) but there is no material difference in expectation coverage.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with strong repository grounding; they are comparable. | claude-sonnet-5: Both reports hit all four expectations with equivalent substance; Report 1 is marginally more thorough (e.g., seed data evidence, UI/backend mismatch, fail-open bool coercion) but both fully satisfy the stated expectations.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with solid evidence; they are comparable, with Report 1 slightly more thorough (placeholder-image observation) though otherwise equivalent. | claude-sonnet-5: Both reports hit all four expectations with solid grounding; Report 1 additionally notes the images are placeholder text banners, while Report 2 offers a cleaner tabular reconciliation — overall comparable in substance.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly answer all three questions with the same root causes and fixes; they are comparable, with Report 1 slightly more detailed but no substantive difference in coverage. | claude-sonnet-5: Both reports are substantively equivalent and correctly hit all three expectations with accurate file-level detail; Report 1 is slightly more thorough (e.g., citing specific line numbers, seed tenant data, and additional defense-in-depth observations) but this does not change the expectation coverage.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports nail the core defect, but Report 1 answers the task more completely by distinguishing gate-vs-optional axis handling that Report 2 explicitly declines to make. | claude-sonnet-5: Report 1 explicitly distinguishes handling for the accuracy gate axis (must not emit any composite) versus relevance/tone (renormalized, flagged-partial is defensible), fully satisfying expectation (d); Report 2 explicitly argues against differentiated handling ("no axis failure should be coerced to a score, for any axis"), missing that distinction, making Report 1 the stronger answer overall.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with well-grounded citations; they are comparable, with Report 2 slightly more explicit on decision-makers and Report 1 slightly tighter on the settled-decision framing. | claude-sonnet-5: Both reports are thorough and hit the core historical findings (a, b) and sign-off recommendation (d) equally well; Report 1 more explicitly frames Cargobox as the deliberate chosen state post-revert and the serverless files as purposely removed (c), which Report 2 leaves implicit, giving Report 1 a slight edge.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly answer all four expectations; Report 1 is marginally more thorough, but they are comparable. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent substance; Report 1 is marginally more rigorous (adds git cherry evidence and per-file scope verification) but both are comparable in correctness and completeness.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent, well-grounded detail; they are comparable. | claude-sonnet-5: Both reports independently hit all four expectations with comparable depth; Report 1 adds slightly more integration-branch mechanics while Report 2 adds a verified numeric example of the pagination bug, but neither is clearly superior on the graded expectations.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge panel disagreed (excluded from both arms): c

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all three expectations; Report 2 is somewhat more thorough, but they are comparable on the graded expectations. | claude-sonnet-5: Both reports correctly identify the cross-tenant leak (a) and the nightly-export breakage (b), but Report 1 lists the latent SQL-injection string as a "blocking" defect despite acknowledging it's not exploitable via the endpoint, while Report 2 explicitly classifies it as non-blocking and correctly retracts exploitability — making Report 2 the stronger, more accurate report per the task's expectations.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are comprehensive and correct, hitting all five expectations with accurate mechanism, commit, and remediation; they are comparable in quality. | claude-sonnet-5: Both reports fully hit all five expectations with comparable depth and evidence; Report 2 is slightly more assertive/organized on remediation ordering and the boot-check, but the substantive content is equivalent.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge panel disagreed (excluded from both arms): d

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations and reach the same conclusions; Report 1 is marginally stronger on reproducibility (explicit re-runs plus verification across five processes), but overall they are comparable. | claude-sonnet-5: Both reports are very similar in substance and hit (a), (b), and (c) equally well, but Report 1 goes further on (d) by actually running the regeneration/comparison multiple times to confirm reproducibility, whereas Report 2 only names the instability source without a concrete repeat-run check.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with equivalent accuracy and file-level grounding; they are comparable, with Report 1 slightly more explicit on the legacy-billing secret while Report 2 more cleanly calls for its removal. | claude-sonnet-5: Both reports cover all four expectations thoroughly and correctly; Report 2 is marginally stronger on category (a) by explicitly calling for removal (not just disabling) of the legacy billing secret reference, but overall the two are comparable in substance and accuracy.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: The two reports are essentially equivalent in substance and both hit all four expectations; Report 1 is marginally stronger on the isolated-verification/shared-runner point. | claude-sonnet-5: Both reports are substantively equivalent, correctly identifying the root cause, regression commit, refuting the flakiness theory, and assessing the proposed next step; report 1 adds a slightly more explicit isolation argument against testing on the shared nightly runner.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 5/5, loaded 5/5, threshold 4: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation with strong repository citations; they are comparable in quality and completeness. | claude-sonnet-5: Both reports hit all five expectations with comparable specificity and citations; Report 2 is slightly more thorough overall (e.g., more explicit remediation critique) but both satisfy the core expectations equally.

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
- Scrub substitutions: 16
- Workspace mutation warnings: csh-t1-cold, eval-harness-t1-loaded, sysdbg-t2-cold, sysdbg-t2-loaded

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
