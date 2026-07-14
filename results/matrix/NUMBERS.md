# NUMBERS: consolidated source of truth for the effort-sweep study

Single-page consolidation of every published figure and cost for the
effort-sweep matrix. Every number here is computed by
`eval/make_numbers.py` or copied verbatim from a canonical source read
at generation time; none is hand-typed. `results/matrix/MATRIX.md`
remains the canonical scoring record. If a figure here and there ever
disagree, MATRIX.md wins and this file is stale; regenerate it.

Sources read: `results/matrix/matrix.json`, every `results/lattice-*/scores.json`
and its raw consumer/judge/adjudicator artifacts, and
`results/concordance/codex-concordance.json`.

Frozen suite hash: `b378c79644280bb93fb8ac71d0cadcfe301fd15b226dfaec852b619a2aa1c890`.

## Hypothesis verdicts (confirmatory: H1 and H2 only)

Pre-registered minimum effect: 3 percentage points. H1 is supported only
when cold(endpoint) - cold(low) >= 3 pp; H2 only when D(low) - D(endpoint)
>= 3 pp. Endpoints are complete-case, replicated means over 3 repeats.
Endpoint is low vs max for every model except Fable, which is low vs high
per the posted 2026-07-10 endpoint amendment.

### H1 (cold-arm endpoint gain)

| Model | Endpoint | cold(low) | cold(endpoint) | Difference (pp) | Bar | Verdict |
|---|---|---|---|---|---|---|
| claude-fable-5 | high | 94.1% | 97.6% | +3.5 | >= 3.0 | directionally supported under the pre-registered rule |
| claude-opus-4-8 | max | 87.3% | 91.2% | +3.9 | >= 3.0 | directionally supported under the pre-registered rule |
| claude-sonnet-5 | max | 84.8% | 89.7% | +4.9 | >= 3.0 | directionally supported under the pre-registered rule |

### H2 (delta shrinkage, low to endpoint)

| Model | Endpoint | D(low) pp | D(endpoint) pp | Shrinkage (pp) | Bar | Verdict |
|---|---|---|---|---|---|---|
| claude-fable-5 | high | +4.9 | +2.4 | +2.5 | >= 3.0 | not supported under the pre-registered rule |
| claude-opus-4-8 | max | +8.3 | +8.8 | -0.5 | >= 3.0 | not supported under the pre-registered rule |
| claude-sonnet-5 | max | +11.3 | +9.8 | +1.5 | >= 3.0 | not supported under the pre-registered rule |

Summary: H1 supported for all three models (Fable +3.5, Opus +3.9,
Sonnet +4.9, all clearing the 3-point bar). H2 not supported for any
model. Effort and skills read as complements, not substitutes.

## Retention ratio (endpoint delta / low delta, complete-case)

| Model | D(low) pp | D(endpoint) pp | Endpoint | R |
|---|---|---|---|---|
| claude-fable-5 | +4.9 | +2.4 | high | 0.490 |
| claude-opus-4-8 | +8.3 | +8.8 | max | 1.060 |
| claude-sonnet-5 | +11.3 | +9.8 | max | 0.867 |

Small-n, directional only.

## Full per-cell table (available-case)

Without-skills is the cold arm, with-skills is the loaded arm. Rates for
replicated endpoint cells are the mean over repeats (marked R3 mean);
single-run cells are point values. Runs = consumer runs per arm.

| Cell | Run dir | Without-skills % | With-skills % | Delta (pp) | Tasks (n) | Must-hit marks (n) | Runs/arm |
|---|---|---|---|---|---|---|---|
| claude-fable-5@low | `results/lattice-fable-low` | 94.1% (R3 mean) | 99.0% (R3 mean) | +4.9 (R3 mean) | 17 | 68 | 3 |
| claude-fable-5@medium | `results/lattice-fable-medium` | 92.6% | 100.0% | +7.4 | 17 | 68 | 1 |
| claude-fable-5@high | `results/lattice-fable-high` | 97.6% (R3 mean) | 100.0% (R3 mean) | +2.4 (R3 mean) | 17 | 68 | 3 |
| claude-fable-5@xhigh | `results/lattice-fable-xhigh` | 97.1% | 100.0% | +2.9 | 17 | 68 | 1 |
| claude-haiku-4-5-20251001@none | `results/lattice-haiku` | 64.7% | 91.2% | +26.5 | 17 | 68 | 1 |
| claude-opus-4-8@low | `results/lattice-opus-low` | 87.3% (R3 mean) | 95.6% (R3 mean) | +8.3 (R3 mean) | 17 | 68 | 3 |
| claude-opus-4-8@medium | `results/lattice-opus-medium` | 85.8% (R3 mean) | 97.6% (R3 mean) | +11.8 (R3 mean) | 17 | 68 | 3 |
| claude-opus-4-8@high | `results/lattice-opus-high` | 88.2% (R3 mean) | 98.0% (R3 mean) | +9.8 (R3 mean) | 17 | 68 | 3 |
| claude-opus-4-8@xhigh | `results/lattice-opus-xhigh` | 91.2% (R3 mean) | 99.0% (R3 mean) | +7.8 (R3 mean) | 17 | 68 | 3 |
| claude-opus-4-8@max | `results/lattice-opus-max` | 91.2% (R3 mean) | 100.0% (R3 mean) | +8.8 (R3 mean) | 17 | 68 | 3 |
| claude-sonnet-5@low | `results/lattice-sonnet-low` | 84.8% (R3 mean) | 96.1% (R3 mean) | +11.3 (R3 mean) | 17 | 68 | 3 |
| claude-sonnet-5@medium | `results/lattice-sonnet-medium` | 90.7% (R3 mean) | 99.0% (R3 mean) | +8.4 (R3 mean) | 17 | 68 | 3 |
| claude-sonnet-5@high | `results/lattice-sonnet-high` | 87.8% (R3 mean) | 99.0% (R3 mean) | +11.3 (R3 mean) | 17 | 68 | 3 |
| claude-sonnet-5@xhigh | `results/lattice-sonnet-xhigh` | 87.3% (R3 mean) | 98.5% (R3 mean) | +11.3 (R3 mean) | 17 | 68 | 3 |
| claude-sonnet-5@max | `results/lattice-sonnet-max` | 89.7% (R3 mean) | 99.5% (R3 mean) | +9.8 (R3 mean) | 17 | 68 | 3 |

Complete-case common task set (n=17): aicg-t2, arch-contracts-t1, bama-t1, consent-t2, csh-t1, dora-t2, env-hazards-t1, eval-harness-t1, farch-t1, git-cc-t2, mabc-t2, mmar-t1, mt-auth-t1, pmvg-t2, s2p-cutover-t1, sysdbg-t2, tcr-t1. Complete-case rates, which are
the only cross-cell-comparable basis, are in MATRIX.md.

## Matched low-to-high view (EXPLORATORY, additive)

All three effort-bearing models' shrinkage on one common low-to-high
basis, so the comparison is basis-matched. Exploratory and directional
only; changes no H1/H2/retention verdict. For Sonnet and Opus the high
cell is an interior single-run cell (descriptive only); Fable's high is
its replicated confirmatory endpoint.

| Model | D(low) pp | D(high) pp | Shrinkage (pp) | High cell |
|---|---|---|---|---|
| claude-fable-5 | +4.9 | +2.4 | +2.5 | replicated endpoint (R3 mean) |
| claude-opus-4-8 | +8.3 | +9.8 | -1.5 | replicated endpoint (R3 mean) |
| claude-sonnet-5 | +11.3 | +11.3 | +0.0 | replicated endpoint (R3 mean) |

## Judge panel disagreement and adjudication

Every comparison was scored by two blinded judges (a Sonnet-class and an
Opus-class judge); disagreements were decided by a pinned third judge,
Claude Fable 5. Adjudicated marks stay in every denominator.

- Overall: 122 of 2652 marks disagreed (4.6%); 135 of 5304 report-slot marks adjudicated (2.5%); 0 unresolved.

| Cell | Marks disagreed | Disagreement % | Slot marks adjudicated | Adjudication % | Unresolved |
|---|---|---|---|---|---|
| claude-fable-5@low | 9/204 | 4.4% | 10/408 | 2.5% | 0 |
| claude-fable-5@medium | 1/68 | 1.5% | 1/136 | 0.7% | 0 |
| claude-fable-5@high | 9/204 | 4.4% | 10/408 | 2.5% | 0 |
| claude-fable-5@xhigh | 3/68 | 4.4% | 3/136 | 2.2% | 0 |
| claude-haiku-4-5-20251001@none | 9/68 | 13.2% | 10/136 | 7.4% | 0 |
| claude-opus-4-8@low | 14/204 | 6.9% | 15/408 | 3.7% | 0 |
| claude-opus-4-8@medium | 9/204 | 4.4% | 11/408 | 2.7% | 0 |
| claude-opus-4-8@high | 9/204 | 4.4% | 11/408 | 2.7% | 0 |
| claude-opus-4-8@xhigh | 6/204 | 2.9% | 7/408 | 1.7% | 0 |
| claude-opus-4-8@max | 8/204 | 3.9% | 9/408 | 2.2% | 0 |
| claude-sonnet-5@low | 8/204 | 3.9% | 10/408 | 2.5% | 0 |
| claude-sonnet-5@medium | 9/204 | 4.4% | 9/408 | 2.2% | 0 |
| claude-sonnet-5@high | 9/204 | 4.4% | 9/408 | 2.2% | 0 |
| claude-sonnet-5@xhigh | 5/204 | 2.5% | 5/408 | 1.2% | 0 |
| claude-sonnet-5@max | 14/204 | 6.9% | 15/408 | 3.7% | 0 |

## Codex cross-vendor concordance (EXPLORATORY)

Cross-vendor robustness spot-check. Never touches any verdict, retention
ratio, or published number. Codex re-scored a deterministic sample of
50 comparisons (of 456 enumerated) and its
marks were compared against the panel-final majority marks.

- Model: gpt-5.6-terra, reasoning effort `high`.
- Overall concordance: 97.2% (383/394 marks).
- Unscorable comparisons: 0 (never guessed).

| Scope | Marks | Agree | Concordance |
|---|---:|---:|---:|
| Overall | 394 | 383 | 97.2% |
| Model column: fable | 128 | 123 | 96.1% |
| Model column: haiku | 16 | 16 | 100.0% |
| Model column: opus | 128 | 125 | 97.7% |
| Model column: sonnet | 122 | 119 | 97.5% |
| Panel-disputed marks | 6 | 5 | 83.3% |

## Shipped-record cost

The true shipped-record cost: `total_cost_usd` summed across every
artifact in the 16 shipped cells, counted exactly once regardless of
which cell or machine produced it. Consumer, judge, and adjudication
costs are broken out per cell. Duplicated artifacts (the opus-medium
batch1 re-adjudication ships byte-identical copies of a subset of
`lattice-opus-medium`) are deduplicated by content hash and attributed
to their canonical cell, so the columns sum exactly to the grand total.

Operational overhead (gates, aborted passes, the never-completed
Fable-max open cell) lives in the private ledger and is not part of this
shipped record.

| Shipped cell | Consumer $ | Judge $ | Adjudication $ | Cell total $ |
|---|---:|---:|---:|---:|
| `results/lattice-fable-low` | 100.07 | 12.66 | 3.37 | 116.10 |
| `results/lattice-fable-medium` | 38.53 | 4.87 | 0.28 | 43.68 |
| `results/lattice-fable-high` | 138.12 | 14.89 | 3.56 | 156.57 |
| `results/lattice-fable-xhigh` | 51.49 | 5.17 | 0.98 | 57.64 |
| `results/lattice-haiku` | 7.17 | 6.52 | 3.69 | 17.38 |
| `results/lattice-opus-low` | 64.35 | 14.44 | 4.77 | 83.56 |
| `results/lattice-opus-medium` | 56.14 | 15.75 | 5.37 | 77.26 |
| `results/lattice-opus-high` | 55.67 | 15.47 | 4.59 | 75.73 |
| `results/lattice-opus-xhigh` | 75.81 | 15.79 | 3.98 | 95.58 |
| `results/lattice-opus-max` | 96.52 | 15.70 | 2.96 | 115.18 |
| `results/lattice-sonnet-low` | 47.23 | 15.28 | 3.92 | 66.43 |
| `results/lattice-sonnet-medium` | 43.02 | 15.69 | 2.57 | 61.28 |
| `results/lattice-sonnet-high` | 54.00 | 17.61 | 5.77 | 77.38 |
| `results/lattice-sonnet-xhigh` | 71.43 | 16.95 | 2.65 | 91.03 |
| `results/lattice-sonnet-max` | 123.47 | 18.59 | 6.30 | 148.36 |
| `results/lattice-opus-medium-batch1-adjudicate` | 11.03 | 2.34 | 0.41 | 13.78 |
| **Grand total (deduplicated)** | **1,034.05** | **207.72** | **55.17** | **1,296.94** |

Grand total shipped-record cost: **$1,296.94** across 16 shipped
cells (results/matrix/matrix.json enumerates 15; the 16th is the opus-medium
batch1 re-adjudication).

Dedup sanity: gross artifact cost across all 16 cell directories is
$1,296.94; $0.00 of that is the batch1 re-adjudication's
byte-identical duplicate of opus-medium artifacts, removed once; the
deduplicated shipped record is $1,296.94 (= 1,296.94 - 0.00).

## Provenance and disclosures

- Posted endpoint amendment: `effort-sweep-amendment-2026-07-10-fable-
  endpoint.md`. For Fable only, H1 and H2 are evaluated on low vs high,
  not low vs max, on operational grounds (Fable-max never fit the pool
  before the stopping deadline); Sonnet and Opus stay low vs max. The
  amendment is referenced from MATRIX.md and from
  `matrix.json` (`h4_matched_low_high.note`, section (c)).
- Blinding exception (disclosed, not papered over): the July judges were
  order-blinded, not content-blinded. A post-run audit found exactly one
  committed judge input of 456 where a sibling skill's name survived the
  scrub (Haiku cell, task aicg-t2, report 1), because the ban list was
  scoped to the task's own skill. It sits outside every confirmatory
  hypothesis; no H1 or H2 number moves. Disclosed in `README.md`
  (methodology honesty notes).
- Concordance selection wording: the pre-registration named the sample
  selection only loosely as "hash-parity"; the implemented deterministic
  digest-sort rule is disclosed verbatim in
  `results/concordance/CONCORDANCE.md` and `codex-concordance.json`
  (`selection_rule`) rather than claimed as literal pre-registered wording.
- Sanitization: nine committed files had absolute local paths redacted by
  mechanical byte-level replacement before first public release, with the
  owner's approval; no mark, score, or model output was altered. Full
  record in `results/SANITIZATION.md`.
- Denominator correction: an early /51 denominator was corrected to 50
  after a recount of the recovered per-task judge data; every number here
  uses the corrected denominator (`README.md`).

