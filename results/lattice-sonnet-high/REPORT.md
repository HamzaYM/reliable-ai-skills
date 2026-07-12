# A/B eval report: lattice-sonnet-high

- Consumer model: claude-sonnet-5
- Consumer effort: high
- Consumer models effective: claude-haiku-4-5-20251001, claude-opus-4-8[1m], claude-sonnet-5
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 3550087650140563827
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 1 consumer / 1 judge
- Wall clock: 60.5 s

## Aggregate

Cold 61/68 (89.7%) | Loaded 68/68 (100.0%) | Delta +7

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Judge panel disagreement: 1 of 68 must-hit marks (1.5%) carried a disputed report slot.

Adjudication: 1 of 136 report-slot marks disputed; 1 adjudicated by claude-fable-5 at --effort medium (0.7% of all slot marks) and kept in every denominator; 0 unresolved after retry (judge-failure exclusion). Disputed slots by report slot: report_1 1, report_2 0; by arm: cold 1, loaded 0.

Combination rule: per report-slot must-hit mark: both primary judges score every blinded comparison fully and independently; each report-slot mark they disagree on is scored once by the pinned adjudicator, which sees only the disputed expectation, the two blinded report slots, and the judging frame; the final mark is the two-of-three majority and disputed marks never leave any denominator.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | 1 | 3/3 | 3/3 | +0 | FAIL |
| architecture-and-contracts/architecture-contracts-as-law | 1 | 3/4 | 4/4 | +1 | PASS |
| auth-and-tenancy/multi-tenant-auth-reference | 1 | 4/5 | 5/5 | +1 | PASS |
| campaign-execution/multi-agent-batch-campaigns | 1 | 4/4 | 4/4 | +0 | FAIL |
| change-control/git-change-control-for-agents | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/budget-aware-model-allocation | 1 | 4/4 | 4/4 | +0 | FAIL |
| cost-and-safety-guardrails/config-and-secrets-hygiene | 1 | 3/4 | 4/4 | +1 | PASS |
| debugging-playbooks/failure-archaeology | 1 | 4/4 | 4/4 | +0 | FAIL |
| debugging-playbooks/systematic-debugging-playbook | 1 | 4/4 | 4/4 | +0 | FAIL |
| deploy-and-infra/environment-and-build-hazards | 1 | 3/3 | 3/3 | +0 | FAIL |
| deploy-and-infra/staging-to-prod-cutover-campaign | 1 | 4/4 | 4/4 | +0 | FAIL |
| docs-and-compliance/consent-and-regulated-data-reference | 1 | 3/4 | 4/4 | +1 | PASS |
| docs-and-compliance/docs-of-record-and-arbitration | 1 | 4/4 | 4/4 | +0 | FAIL |
| evals-and-scoring/llm-eval-harness-and-scoring-pipeline | 1 | 3/4 | 4/4 | +1 | PASS |
| tiered-review/tiered-consultancy-review | 1 | 4/5 | 5/5 | +1 | PASS |
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

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with accurate, well-grounded findings and concrete fixes; they are comparable. | claude-sonnet-5: Both reports independently hit all four expectations with essentially equivalent substance and proposed fixes; they are comparable in coverage, with Report 2 adding minor extra context (e.g. compliance.md, prompt files) without changing the core findings.

### arch-contracts-t1 (architecture-and-contracts/architecture-contracts-as-law)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Report 1 answered better: it hits all four expectations, including recommending dropping the hardcoded webhook count, whereas Report 2 only suggests changing 4 to 5 and misses expectation (d). | claude-sonnet-5: Both reports are very close and hit expectations a, b, and c equally well; Report 1 is stronger on (d) because it explicitly recommends dropping the hardcoded count in favor of the code as source of truth, while Report 2 merely updates the number from 4 to 5 without addressing the drift-prone hardcoding itself.

### bama-t1 (cost-and-safety-guardrails/budget-aware-model-allocation)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable — both reports hit all four expectations with correct numbers, backend routing, restraint on the default command, and snapshot-staleness caveat. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent substance; Report 2 is marginally more precise (14.6× framing, reset-timing analysis) but the two are comparable in overall quality and completeness.

### consent-t2 (docs-and-compliance/consent-and-regulated-data-reference)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | MISS | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and comparable, but Report 1 edges ahead by correctly flagging the consent_receipts deletion in erase_user.py as the preservation issue, which Report 2 misses. | claude-sonnet-5: Report 1 correctly identifies that erase_user.py wrongly deletes the PII-free consent_receipts proof-of-consent record (which should be preserved), while Report 2 misses this and instead only notes that consent_audit (which erase_user.py never touches) should be preserved — otherwise the two reports are equally thorough and accurate, making Report 1 the stronger overall answer.

### csh-t1 (cost-and-safety-guardrails/config-and-secrets-hygiene)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports nail the default-behavior findings, but Report 2 additionally and clearly recommends a global env-level gate ANDed with the per-tenant flag, making it the stronger answer overall. | claude-sonnet-5: Both reports are nearly identical in substance and both hit a, b, and c equally well; Report 2 additionally and explicitly recommends adding a global/env-level kill switch ANDed with the per-tenant flag (expectation d), which Report 1 only gestures at without recommending, making Report 2 the more complete answer.

### dora-t2 (docs-and-compliance/docs-of-record-and-arbitration)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with grounded evidence; they are comparable, with Report 1 slightly more decisive on removing the AI-assistance footer. | claude-sonnet-5: Both reports are substantively equivalent, hitting all four expectations with nearly identical evidence and grounding; report 2 hedges slightly more on the AI-assistance line (suggesting a decision rather than outright removal) while report 1 is more direct, but overall the two are comparable in thoroughness and accuracy.

### env-hazards-t1 (deploy-and-infra/environment-and-build-hazards)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly answer all three questions with equivalent grounding; they are comparable. | claude-sonnet-5: Both reports independently identify the same root causes and fixes with equal precision and correct evidence; they are comparable in quality, with Report 2 slightly more explicit that switching roles alone suffices and Report 1 slightly more detailed on git-history provenance.

### eval-harness-t1 (evals-and-scoring/llm-eval-harness-and-scoring-pipeline)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and comparable, but Report 1 additionally distinguishes that renormalizing over surviving axes is defensible for relevance/tone while forbidden for accuracy, edging it ahead. | claude-sonnet-5: Both reports are strong and nearly identical on questions 1-3, but Report 1 explicitly distinguishes handling for gate (accuracy) vs. non-gate (relevance/tone) axis failures — renormalize-and-flag for the latter, exclude entirely for the former — while Report 2 treats all axis failures uniformly (never emit a composite, retry/mark incomplete) without carving out the renormalization-is-defensible case for optional axes, making Report 1 the more complete answer.

### farch-t1 (debugging-playbooks/failure-archaeology)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully satisfy all four expectations with strong commit-grounded evidence; they are comparable, with Report 2 marginally more explicit about the deliberate revert and cost-owner involvement. | claude-sonnet-5: Both reports hit all four expectations with solid commit citations and grounded recommendations; Report 2 is marginally more precise on expectation (c) by explicitly stating the serverless files were "deleted in the revert," but the difference is minor and both are comparable in overall quality.

### git-cc-t2 (change-control/git-change-control-for-agents)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with correct, well-cited git analysis; they are comparable, with Report 1 and Report 2 essentially equivalent in substance. | claude-sonnet-5: Both reports independently reach the same correct conclusions on all four expectations, with Report 1 being marginally more rigorous (explicit git fetch/origin freshness step and explicit re-check that scoring/scorer.py shows zero diff), while Report 2 is slightly less explicit about origin freshness but adds useful extra observations (dead-code flag, stale branch cleanup suggestion); overall comparable quality, Report 1 slightly more thorough on the freshness verification.

### mabc-t2 (campaign-execution/multi-agent-batch-campaigns)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all four expectations with comparable substance; Report 1 adds extra ground-truth depth (a currently-red test) but neither is materially better on the graded criteria. | claude-sonnet-5: Both reports hit all four expectations with essentially equivalent substance; Report 1 additionally surfaces a bonus finding (a pre-existing failing test) not required by the rubric, but on the stated expectations the two are comparable in quality and completeness.

### mmar-t1 (adversarial-review/multi-model-adversarial-review)

Cold 3/3, loaded 3/3, threshold 2: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit all three expectations with the same core findings; they are comparable, with Report 1 slightly more thorough in confirmation detail. | claude-sonnet-5: Both reports are substantively equivalent, correctly identifying the cross-tenant data leak and the exports.py breaking change while correctly declining to treat the status interpolation as exploitable SQL injection.

### mt-auth-t1 (auth-and-tenancy/multi-tenant-auth-reference)

Cold 4/5, loaded 5/5, threshold 4: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |
| e | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are excellent and nearly identical on the core diagnosis; Report 2 is marginally stronger because it also adds the explicit application-layer tenant filter (expectation d) that Report 1 omits. | claude-sonnet-5: Both reports correctly diagnose the RLS-owner-exemption root cause, cite the same commit and files, and recommend equivalent fixes and boot-time checks; Report 2 is more complete because it also adds the explicit application-level tenant_id filter as a second isolation layer, which Report 1 omits.

### pmvg-t2 (validation-gates/pre-merge-validation-gate)

Cold 3/4, loaded 4/4, threshold 3: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | MISS | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports are strong and nearly equivalent, but Report 2 edges ahead by explicitly adding a reproducibility check tied to the discoverable set-ordering instability in the regen script. | claude-sonnet-5: Report 2 covers all four expectations, including the reproducibility/determinism check with the CATEGORIES-set ordering root cause, which Report 1 omits entirely.

### s2p-cutover-t1 (deploy-and-infra/staging-to-prod-cutover-campaign)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Comparable: both reports hit all four expectations with correct file/line citations; Report 2 is marginally more decisive on removal recommendations and adds a resource-name collision observation. | claude-sonnet-5: Both reports hit all four expectations with very similar depth and evidence; Report 2 is marginally more thorough on category (a) (covers all four trap categories with explicit removal language for each) and adds an extra unconfirmed resource-name-collision risk, but the two are comparable in overall answer quality.

### sysdbg-t2 (debugging-playbooks/systematic-debugging-playbook)

Cold 4/4, loaded 4/4, threshold 3: FAIL

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports fully and correctly hit all four expectations with strong repository-grounded evidence; they are comparable. | claude-sonnet-5: Both reports are substantively equivalent, correctly identifying the same root cause, fix site, introducing commit, flaw in the earlier reproduction, and flaw in the proposed model-revert plan; Report 2 adds a concrete numeric re-scoring verification (~0.909) and full commit hash, giving it a slight edge in rigor, but neither is meaningfully more complete against the expectations.

### tcr-t1 (tiered-review/tiered-consultancy-review)

Cold 4/5, loaded 5/5, threshold 4: PASS

| Expectation | Cold | Loaded |
|---|---|---|
| a | HIT | HIT |
| b | HIT | HIT |
| c | HIT | HIT |
| d | HIT | HIT |
| e | MISS | HIT |

Judge panel disagreed (excluded from both arms): e

Judge comparative verdict (no score weight): claude-opus-4-8: Both reports hit every expectation; Report 2 is marginally stronger with a cleaner, more explicit treatment of the mis-ordering/structure point. | claude-sonnet-5: Both reports hit (a)-(d) equally well with proper citations; Report 2 additionally identifies the structural/ordering problem (opens with self-praise, buries remediation, violates lead-with-impact rule) explicitly per (e), while Report 1 only critiques tone without addressing the ordering issue, making Report 2 the more complete answer.

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
- Scrub substitutions: 54
- Workspace mutation warnings: mabc-t2-loaded, mmar-t1-loaded, pmvg-t2-cold, pmvg-t2-loaded, sysdbg-t2-cold, sysdbg-t2-loaded

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
