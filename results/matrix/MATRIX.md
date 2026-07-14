# Matrix report: must-hit rates per skill x cell

A cell is one consumer model x effort run. Every number below is
recomputed from that run's raw judge outputs, and every denominator
is computed from the data. All cells are small-n: treat every rate
and delta as directional, not inferential.

Two bases are reported. Available-case uses every task valid in
that cell. Complete-case restricts every cell to the tasks valid
in ALL cells (paired exclusion extended across the matrix), so
only complete-case numbers are comparable across cells. Delta is
must-hit-weighted; eq-skill delta weights every skill equally;
headroom is the share of the cold arm's remaining headroom the
loaded arm recovered, (L - C) / (1 - C), undefined at cold
ceiling; ceiling counts tasks where an arm hit every must-hit.

Replicated endpoint cells (run at --repeats N) show BOLD mean
rates over repeats, marked (RN mean); single-run interior cells
are unmarked point values with no uncertainty display. Per-skill
PASS/FAIL verdicts are deliberately suppressed in lattice
outputs; skills appear as rates only, subordinated to the
per-cell run reports.

## Cells (available-case)

| Cell | Tasks | Cold | Loaded | Delta (pp) | Eq-skill delta (pp) | Headroom | Ceiling c/l | n |
|---|---|---|---|---|---|---|---|---|
| claude-fable-5@low | 17 | **94.1%** (R3 mean) | **99.0%** (R3 mean) | **+4.9** (R3 mean) | +4.9 | 100.0% | 14/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-fable-5@medium | 17 | 63/68 (92.6%) | 68/68 (100.0%) | +7.4 | +7.4 | 100.0% | 12/17 | n=17 tasks, single run per arm: directional only |
| claude-fable-5@high | 17 | **97.6%** (R3 mean) | **100.0%** (R3 mean) | **+2.4** (R3 mean) | +1.5 | 100.0% | 16/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-fable-5@xhigh | 17 | 66/68 (97.1%) | 68/68 (100.0%) | +2.9 | +2.9 | 100.0% | 15/17 | n=17 tasks, single run per arm: directional only |
| claude-haiku-4-5-20251001@none | 17 | 44/68 (64.7%) | 62/68 (91.2%) | +26.5 | +26.4 | 75.0% | 3/12 | n=17 tasks, single run per arm: directional only |
| claude-opus-4-8@low | 17 | **87.3%** (R3 mean) | **95.6%** (R3 mean) | **+8.3** (R3 mean) | +8.8 | 66.7% | 8/14 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-opus-4-8@medium | 17 | **85.8%** (R3 mean) | **97.6%** (R3 mean) | **+11.8** (R3 mean) | +13.4 | 90.0% | 7/16 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-opus-4-8@high | 17 | **88.2%** (R3 mean) | **98.0%** (R3 mean) | **+9.8** (R3 mean) | +8.5 | 85.7% | 11/16 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-opus-4-8@xhigh | 17 | **91.2%** (R3 mean) | **99.0%** (R3 mean) | **+7.8** (R3 mean) | +5.9 | 100.0% | 13/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-opus-4-8@max | 17 | **91.2%** (R3 mean) | **100.0%** (R3 mean) | **+8.8** (R3 mean) | +7.4 | 100.0% | 12/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-sonnet-5@low | 17 | **84.8%** (R3 mean) | **96.1%** (R3 mean) | **+11.3** (R3 mean) | +14.4 | 83.3% | 5/15 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-sonnet-5@medium | 17 | **90.7%** (R3 mean) | **99.0%** (R3 mean) | **+8.4** (R3 mean) | +5.9 | 100.0% | 13/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-sonnet-5@high | 17 | **87.8%** (R3 mean) | **99.0%** (R3 mean) | **+11.3** (R3 mean) | +11.2 | 100.0% | 9/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-sonnet-5@xhigh | 17 | **87.3%** (R3 mean) | **98.5%** (R3 mean) | **+11.3** (R3 mean) | +11.5 | 100.0% | 10/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-sonnet-5@max | 17 | **89.7%** (R3 mean) | **99.5%** (R3 mean) | **+9.8** (R3 mean) | +11.2 | 100.0% | 11/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |

| Cell | Run | Preregistered |
|---|---|---|
| claude-fable-5@low | lattice-fable-low | yes |
| claude-fable-5@medium | lattice-fable-medium | yes |
| claude-fable-5@high | lattice-fable-high | yes |
| claude-fable-5@xhigh | lattice-fable-xhigh | yes |
| claude-haiku-4-5-20251001@none | lattice-haiku | yes |
| claude-opus-4-8@low | lattice-opus-low | yes |
| claude-opus-4-8@medium | lattice-opus-medium-v2 | yes |
| claude-opus-4-8@high | lattice-opus-high-v2 | yes |
| claude-opus-4-8@xhigh | lattice-opus-xhigh-v2 | yes |
| claude-opus-4-8@max | lattice-opus-max | yes |
| claude-sonnet-5@low | lattice-sonnet-low | yes |
| claude-sonnet-5@medium | lattice-sonnet-medium-v2 | yes |
| claude-sonnet-5@high | lattice-sonnet-high-v2 | yes |
| claude-sonnet-5@xhigh | lattice-sonnet-xhigh-v2 | yes |
| claude-sonnet-5@max | lattice-sonnet-max | yes |

## Complete-case aggregate (tasks valid in every cell)

Common complete-case task set (17): aicg-t2, arch-contracts-t1, bama-t1, consent-t2, csh-t1, dora-t2, env-hazards-t1, eval-harness-t1, farch-t1, git-cc-t2, mabc-t2, mmar-t1, mt-auth-t1, pmvg-t2, s2p-cutover-t1, sysdbg-t2, tcr-t1.

| Cell | Tasks | Cold | Loaded | Delta (pp) | Eq-skill delta (pp) | Headroom | Ceiling c/l | n |
|---|---|---|---|---|---|---|---|---|
| claude-fable-5@low | 17 | **94.1%** (R3 mean) | **99.0%** (R3 mean) | **+4.9** (R3 mean) | +4.9 | 100.0% | 14/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-fable-5@medium | 17 | 63/68 (92.6%) | 68/68 (100.0%) | +7.4 | +7.4 | 100.0% | 12/17 | n=17 tasks, single run per arm: directional only |
| claude-fable-5@high | 17 | **97.6%** (R3 mean) | **100.0%** (R3 mean) | **+2.4** (R3 mean) | +1.5 | 100.0% | 16/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-fable-5@xhigh | 17 | 66/68 (97.1%) | 68/68 (100.0%) | +2.9 | +2.9 | 100.0% | 15/17 | n=17 tasks, single run per arm: directional only |
| claude-haiku-4-5-20251001@none | 17 | 44/68 (64.7%) | 62/68 (91.2%) | +26.5 | +26.4 | 75.0% | 3/12 | n=17 tasks, single run per arm: directional only |
| claude-opus-4-8@low | 17 | **87.3%** (R3 mean) | **95.6%** (R3 mean) | **+8.3** (R3 mean) | +8.8 | 66.7% | 8/14 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-opus-4-8@medium | 17 | **85.8%** (R3 mean) | **97.6%** (R3 mean) | **+11.8** (R3 mean) | +13.4 | 90.0% | 7/16 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-opus-4-8@high | 17 | **88.2%** (R3 mean) | **98.0%** (R3 mean) | **+9.8** (R3 mean) | +8.5 | 85.7% | 11/16 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-opus-4-8@xhigh | 17 | **91.2%** (R3 mean) | **99.0%** (R3 mean) | **+7.8** (R3 mean) | +5.9 | 100.0% | 13/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-opus-4-8@max | 17 | **91.2%** (R3 mean) | **100.0%** (R3 mean) | **+8.8** (R3 mean) | +7.4 | 100.0% | 12/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-sonnet-5@low | 17 | **84.8%** (R3 mean) | **96.1%** (R3 mean) | **+11.3** (R3 mean) | +14.4 | 83.3% | 5/15 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-sonnet-5@medium | 17 | **90.7%** (R3 mean) | **99.0%** (R3 mean) | **+8.4** (R3 mean) | +5.9 | 100.0% | 13/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-sonnet-5@high | 17 | **87.8%** (R3 mean) | **99.0%** (R3 mean) | **+11.3** (R3 mean) | +11.2 | 100.0% | 9/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-sonnet-5@xhigh | 17 | **87.3%** (R3 mean) | **98.5%** (R3 mean) | **+11.3** (R3 mean) | +11.5 | 100.0% | 10/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| claude-sonnet-5@max | 17 | **89.7%** (R3 mean) | **99.5%** (R3 mean) | **+9.8** (R3 mean) | +11.2 | 100.0% | 11/17 | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |

## Retention (low vs max, complete-case)

Note: claude-fable-5's endpoint below is low vs high (not max) per the posted endpoint amendment. Every 'D(max)' figure below is that model's amended endpoint value, not a literal max-effort run.

- claude-fable-5: D(low) +4.9 pp, D(max) +2.4 pp, R = 0.490 (R = D(high)/D(low) on the complete-case must-hit-weighted delta; small-n, directional only)
- claude-opus-4-8: D(low) +8.3 pp, D(max) +8.8 pp, R = 1.060 (R = D(max)/D(low) on the complete-case must-hit-weighted delta; small-n, directional only)
- claude-sonnet-5: D(low) +11.3 pp, D(max) +9.8 pp, R = 0.867 (R = D(max)/D(low) on the complete-case must-hit-weighted delta; small-n, directional only)

## Hypothesis verdicts (confirmatory: H1 and H2 only)

Rule: pre-registered minimum effect 3 pp: H1 is supported only when cold(max) - cold(low) >= 3 pp; H2 only when D(low) - D(max) >= 3 pp; strict inequalities alone are never sufficient.

Scope: endpoint cells only (low+max, except low+high for any model in CONFIRMATORY_ENDPOINT_EFFORT_OVERRIDE, currently Fable per the 2026-07-10 endpoint amendment), complete-case, replicated means when the endpoint ran repeated; interior cells (medium, high, xhigh) cannot affect H1 or H2 under any circumstance; effort-invariant models are outside all effort-trend hypotheses.

### H1 (cold-arm endpoint gain)

| Model | cold(low) | cold(max) | Difference (pp) | Verdict |
|---|---|---|---|---|
| claude-fable-5 | 94.1% | 97.6% | +3.5 | directionally supported under the pre-registered rule |
| claude-opus-4-8 | 87.3% | 91.2% | +3.9 | directionally supported under the pre-registered rule |
| claude-sonnet-5 | 84.8% | 89.7% | +4.9 | directionally supported under the pre-registered rule |

Note: 'max' columns below are literal max-effort for every model except: claude-fable-5 = low vs high (posted endpoint amendment).

### H2 (delta shrinkage low to max)

| Model | D(low) pp | D(max) pp | Shrinkage (pp) | Verdict |
|---|---|---|---|---|
| claude-fable-5 | +4.9 | +2.4 | +2.5 | not supported under the pre-registered rule |
| claude-opus-4-8 | +8.3 | +8.8 | -0.5 | not supported under the pre-registered rule |
| claude-sonnet-5 | +11.3 | +9.8 | +1.5 | not supported under the pre-registered rule |

Note: 'max' columns below are literal max-effort for every model except: claude-fable-5 = low vs high (posted endpoint amendment).

H3 and H4 are EXPLORATORY (see the cross-model views); H1 and H2 above are the only confirmatory hypotheses.

## Cross-model views (complete-case)

### Matched effort (primary)

Models compared at the same explicit effort level. Effort-
invariant models (effort none) never appear here.

| Effort | Model | Cell | Delta (pp) | Eq-skill delta (pp) | Headroom | n |
|---|---|---|---|---|---|---|
| low | claude-fable-5 | claude-fable-5@low | +4.9 | +4.9 | 100.0% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| low | claude-opus-4-8 | claude-opus-4-8@low | +8.3 | +8.8 | 66.7% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| low | claude-sonnet-5 | claude-sonnet-5@low | +11.3 | +14.4 | 83.3% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| medium | claude-fable-5 | claude-fable-5@medium | +7.4 | +7.4 | 100.0% | n=17 tasks, single run per arm: directional only |
| medium | claude-opus-4-8 | claude-opus-4-8@medium | +11.8 | +13.4 | 90.0% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| medium | claude-sonnet-5 | claude-sonnet-5@medium | +8.4 | +5.9 | 100.0% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| high | claude-fable-5 | claude-fable-5@high | +2.4 | +1.5 | 100.0% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| high | claude-opus-4-8 | claude-opus-4-8@high | +9.8 | +8.5 | 85.7% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| high | claude-sonnet-5 | claude-sonnet-5@high | +11.3 | +11.2 | 100.0% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| xhigh | claude-fable-5 | claude-fable-5@xhigh | +2.9 | +2.9 | 100.0% | n=17 tasks, single run per arm: directional only |
| xhigh | claude-opus-4-8 | claude-opus-4-8@xhigh | +7.8 | +5.9 | 100.0% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| xhigh | claude-sonnet-5 | claude-sonnet-5@xhigh | +11.3 | +11.5 | 100.0% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| max | claude-opus-4-8 | claude-opus-4-8@max | +8.8 | +7.4 | 100.0% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |
| max | claude-sonnet-5 | claude-sonnet-5@max | +9.8 | +11.2 | 100.0% | n=17 tasks, 3 runs per arm: directional only (replicated endpoint mean over repeats) |

### Defaults as shipped (secondary, labeled)

Each model at its own shipped default effort. The levels differ
across models, so cross-model differences here conflate model
tier and effort level.

| Model | Effort | Cell | Delta (pp) | Eq-skill delta (pp) | Headroom | n |
|---|---|---|---|---|---|---|
| claude-haiku-4-5-20251001 | none | claude-haiku-4-5-20251001@none | +26.5 | +26.4 | 75.0% | n=17 tasks, single run per arm: directional only |

### H3 visibility tags (EXPLORATORY)

H3 (visibility-tag heterogeneity) is exploratory only: computed
over tagged task strata outside this matrix, with no confirmatory
verdict; no lattice number here feeds it.

### H4 shrinkage side by side (EXPLORATORY, directional only)

Per-model low-to-max delta shrinkage; exploratory, nothing
stronger than direction is claimed. Effort-invariant models are
excluded from all effort-trend views.

Note: claude-fable-5 is low vs high (not max) per the posted endpoint amendment -- NOT yet the amendment's matched low-to-high basis for every model (amendment section (c) is a disclosed, deferred follow-up); Sonnet/Opus below remain low-to-max

| Model | D(low) pp | D(max) pp | R |
|---|---|---|---|
| claude-fable-5 | +4.9 | +2.4 | 0.490 |
| claude-opus-4-8 | +8.3 | +8.8 | 1.060 |
| claude-sonnet-5 | +11.3 | +9.8 | 0.867 |

## H4 matched low-to-high view (EXPLORATORY, additive)

Matched cross-model shrinkage on one common low-to-high basis for
all three effort-bearing models, so the comparison is basis-
matched. This fulfills the deferred follow-up disclosed in the
posted amendment (effort-sweep-amendment-2026-07-10-fable-endpoint.md section (c)). Exploratory and directional only; it is
additive and changes no H1/H2/retention/H4 number or verdict above.
Fable's high is its replicated confirmatory endpoint; for Sonnet
and Opus, high is an interior cell (not their confirmatory
endpoint, which is max), descriptive only -- see the table's own
High cell column for whether each is single-run or replicated.

| Model | D(low) pp | D(high) pp | Shrinkage (pp) | High cell |
|---|---|---|---|---|
| claude-fable-5 | +4.9 | +2.4 | +2.5 | replicated confirmatory endpoint (R3 mean) |
| claude-opus-4-8 | +8.3 | +9.8 | -1.5 | interior, R3 mean (descriptive only) |
| claude-sonnet-5 | +11.3 | +11.3 | +0.0 | interior, R3 mean (descriptive only) |

## Judge panel disagreement and adjudication

- claude-fable-5@low: 9 of 204 marks disagreed (4.4%); 10 of 408 report-slot marks adjudicated (2.5%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-fable-5@medium: 1 of 68 marks disagreed (1.5%); 1 of 136 report-slot marks adjudicated (0.7%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-fable-5@high: 9 of 204 marks disagreed (4.4%); 10 of 408 report-slot marks adjudicated (2.5%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-fable-5@xhigh: 3 of 68 marks disagreed (4.4%); 3 of 136 report-slot marks adjudicated (2.2%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-haiku-4-5-20251001@none: 9 of 68 marks disagreed (13.2%); 10 of 136 report-slot marks adjudicated (7.4%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-opus-4-8@low: 14 of 204 marks disagreed (6.9%); 15 of 408 report-slot marks adjudicated (3.7%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-opus-4-8@medium: 9 of 204 marks disagreed (4.4%); 11 of 408 report-slot marks adjudicated (2.7%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-opus-4-8@high: 9 of 204 marks disagreed (4.4%); 11 of 408 report-slot marks adjudicated (2.7%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-opus-4-8@xhigh: 6 of 204 marks disagreed (2.9%); 7 of 408 report-slot marks adjudicated (1.7%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-opus-4-8@max: 8 of 204 marks disagreed (3.9%); 9 of 408 report-slot marks adjudicated (2.2%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-sonnet-5@low: 8 of 204 marks disagreed (3.9%); 10 of 408 report-slot marks adjudicated (2.5%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-sonnet-5@medium: 9 of 204 marks disagreed (4.4%); 9 of 408 report-slot marks adjudicated (2.2%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-sonnet-5@high: 9 of 204 marks disagreed (4.4%); 9 of 408 report-slot marks adjudicated (2.2%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-sonnet-5@xhigh: 5 of 204 marks disagreed (2.5%); 5 of 408 report-slot marks adjudicated (1.2%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- claude-sonnet-5@max: 14 of 204 marks disagreed (6.9%); 15 of 408 report-slot marks adjudicated (3.7%), kept in every denominator; 0 unresolved (judge-failure exclusion)
- Overall: 122 of 2652 marks disagreed (4.6%); 135 of 5304 report-slot marks adjudicated (2.5%), 0 unresolved

## Invalidation rates by model x effort x arm

Natural completion: the run finished but was invalid (for
example a missing Answers section or a cross-model fallback).
Harness censored: the harness cut the run off (timeout or the
pinned output ceiling). Judging rows count task exclusions from
judge or adjudicator failures.

| Cell | Arm | Invalid / planned tasks | Rate | Natural completion | Harness censored |
|---|---|---|---|---|---|
| claude-fable-5@low | cold | 0/17 | 0.0% | 0 | 0 |
| claude-fable-5@low | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-fable-5@medium | cold | 0/17 | 0.0% | 0 | 0 |
| claude-fable-5@medium | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-fable-5@high | cold | 0/17 | 0.0% | 0 | 0 |
| claude-fable-5@high | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-fable-5@xhigh | cold | 0/17 | 0.0% | 0 | 0 |
| claude-fable-5@xhigh | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-haiku-4-5-20251001@none | cold | 0/17 | 0.0% | 0 | 0 |
| claude-haiku-4-5-20251001@none | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-opus-4-8@low | cold | 0/17 | 0.0% | 0 | 0 |
| claude-opus-4-8@low | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-opus-4-8@medium | cold | 0/17 | 0.0% | 0 | 0 |
| claude-opus-4-8@medium | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-opus-4-8@high | cold | 0/17 | 0.0% | 0 | 0 |
| claude-opus-4-8@high | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-opus-4-8@xhigh | cold | 0/17 | 0.0% | 0 | 0 |
| claude-opus-4-8@xhigh | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-opus-4-8@max | cold | 0/17 | 0.0% | 0 | 0 |
| claude-opus-4-8@max | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-sonnet-5@low | cold | 0/17 | 0.0% | 0 | 0 |
| claude-sonnet-5@low | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-sonnet-5@medium | cold | 0/17 | 0.0% | 0 | 0 |
| claude-sonnet-5@medium | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-sonnet-5@high | cold | 0/17 | 0.0% | 0 | 0 |
| claude-sonnet-5@high | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-sonnet-5@xhigh | cold | 0/17 | 0.0% | 0 | 0 |
| claude-sonnet-5@xhigh | loaded | 0/17 | 0.0% | 0 | 0 |
| claude-sonnet-5@max | cold | 0/17 | 0.0% | 0 | 0 |
| claude-sonnet-5@max | loaded | 0/17 | 0.0% | 0 | 0 |

## Task-cluster bootstrap (descriptive, non-inferential)

task-cluster bootstrap: descriptive sensitivity only, non-inferential; whole tasks (clusters) resampled with replacement, must-hit-weighted delta per resample. Seed 20260710, 1000 iterations, complete-case basis.

| Cell | Delta p2.5 | Delta p50 | Delta p97.5 | Resamples |
|---|---|---|---|---|
| claude-fable-5@low | +0.0 | +4.4 | +9.4 | 1000 |
| claude-fable-5@medium | +2.8 | +7.4 | +13.2 | 1000 |
| claude-fable-5@high | +0.0 | +1.4 | +4.5 | 1000 |
| claude-fable-5@xhigh | +0.0 | +2.9 | +7.6 | 1000 |
| claude-haiku-4-5-20251001@none | +15.7 | +26.5 | +36.4 | 1000 |
| claude-opus-4-8@low | +2.9 | +8.8 | +14.7 | 1000 |
| claude-opus-4-8@medium | +7.4 | +13.2 | +19.7 | 1000 |
| claude-opus-4-8@high | +1.4 | +8.8 | +17.4 | 1000 |
| claude-opus-4-8@xhigh | +1.4 | +5.9 | +11.8 | 1000 |
| claude-opus-4-8@max | +1.5 | +7.2 | +13.0 | 1000 |
| claude-sonnet-5@low | +9.0 | +14.7 | +20.0 | 1000 |
| claude-sonnet-5@medium | +1.4 | +5.8 | +10.6 | 1000 |
| claude-sonnet-5@high | +6.1 | +11.8 | +17.3 | 1000 |
| claude-sonnet-5@xhigh | +4.8 | +11.6 | +18.8 | 1000 |
| claude-sonnet-5@max | +4.5 | +11.8 | +19.7 | 1000 |

## Per skill x cell

Cell format: cold hits/n (rate), loaded hits/n (rate), delta in
percentage points, then that cell's n label. Per-skill PASS/FAIL
is deliberately suppressed in lattice outputs; this table
reports rates only.

| Skill | claude-fable-5@low | claude-fable-5@medium | claude-fable-5@high | claude-fable-5@xhigh | claude-haiku-4-5-20251001@none | claude-opus-4-8@low | claude-opus-4-8@medium | claude-opus-4-8@high | claude-opus-4-8@xhigh | claude-opus-4-8@max | claude-sonnet-5@low | claude-sonnet-5@medium | claude-sonnet-5@high | claude-sonnet-5@xhigh | claude-sonnet-5@max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| adversarial-review/multi-model-adversarial-review | cold 2/3 (66.7%), loaded 3/3 (100.0%), delta +33.3 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 1/3 (33.3%), loaded 2/3 (66.7%), delta +33.3 pp [n=1 task, single run per arm: directional only] | cold 2/3 (66.7%), loaded 2/3 (66.7%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 2/3 (66.7%), loaded 3/3 (100.0%), delta +33.3 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 2/3 (66.7%), loaded 2/3 (66.7%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| architecture-and-contracts/architecture-contracts-as-law | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 2/4 (50.0%), loaded 4/4 (100.0%), delta +50.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 2/4 (50.0%), loaded 4/4 (100.0%), delta +50.0 pp [n=1 task, 3 runs per arm: directional only] | cold 2/4 (50.0%), loaded 4/4 (100.0%), delta +50.0 pp [n=1 task, 3 runs per arm: directional only] |
| auth-and-tenancy/multi-tenant-auth-reference | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/5 (80.0%), loaded 5/5 (100.0%), delta +20.0 pp [n=1 task, single run per arm: directional only] | cold 4/5 (80.0%), loaded 4/5 (80.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/5 (80.0%), loaded 5/5 (100.0%), delta +20.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/5 (80.0%), loaded 5/5 (100.0%), delta +20.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/5 (80.0%), loaded 5/5 (100.0%), delta +20.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/5 (80.0%), loaded 5/5 (100.0%), delta +20.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/5 (80.0%), loaded 5/5 (100.0%), delta +20.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/5 (60.0%), loaded 5/5 (100.0%), delta +40.0 pp [n=1 task, 3 runs per arm: directional only] |
| campaign-execution/multi-agent-batch-campaigns | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 0/4 (0.0%), loaded 2/4 (50.0%), delta +50.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 3/4 (75.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 3/4 (75.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 2/4 (50.0%), loaded 4/4 (100.0%), delta +50.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] |
| change-control/git-change-control-for-agents | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 2/4 (50.0%), loaded 3/4 (75.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 3/4 (75.0%), delta -25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| cost-and-safety-guardrails/ai-cost-tracking-and-guardrails | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| cost-and-safety-guardrails/budget-aware-model-allocation | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 3/4 (75.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| cost-and-safety-guardrails/config-and-secrets-hygiene | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] |
| debugging-playbooks/failure-archaeology | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| debugging-playbooks/systematic-debugging-playbook | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| deploy-and-infra/environment-and-build-hazards | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/3 (100.0%), loaded 3/3 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| deploy-and-infra/staging-to-prod-cutover-campaign | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] |
| docs-and-compliance/consent-and-regulated-data-reference | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 2/4 (50.0%), loaded 4/4 (100.0%), delta +50.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| docs-and-compliance/docs-of-record-and-arbitration | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 3/4 (75.0%), delta -25.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| evals-and-scoring/llm-eval-harness-and-scoring-pipeline | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| tiered-review/tiered-consultancy-review | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 3/5 (60.0%), loaded 4/5 (80.0%), delta +20.0 pp [n=1 task, single run per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/5 (80.0%), loaded 5/5 (100.0%), delta +20.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 5/5 (100.0%), loaded 5/5 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] |
| validation-gates/pre-merge-validation-gate | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, single run per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, single run per arm: directional only] | cold 1/4 (25.0%), loaded 4/4 (100.0%), delta +75.0 pp [n=1 task, single run per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 4/4 (100.0%), loaded 4/4 (100.0%), delta +0.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] | cold 3/4 (75.0%), loaded 4/4 (100.0%), delta +25.0 pp [n=1 task, 3 runs per arm: directional only] |

## Notes

- No excluded tasks in any cell.
