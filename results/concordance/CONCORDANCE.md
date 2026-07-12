# Codex cross-vendor concordance sample

**EXPLORATORY ONLY.** This cross-vendor spot-check never touches any verdict, retention ratio, or published number. It is a pre-registered robustness check (section 3 of the effort-sweep pre-registration).

- Overall concordance: **97.2%** (383/394 marks) over n=50 comparisons.
- Unscorable comparisons: **0** (Codex output unparseable after one retry; never guessed).
- Re-scored on Codex: models gpt-5.6-terra, reasoning effort `high`.

A *mark* is one (comparison, expectation, arm) binary HIT/MISS. Concordance is the fraction of marks where Codex agrees with the panel-final (majority-resolved) mark that scores.json scored.

## Method

- **Selection (deterministic):** digest = SHA256(SUITE_HASH + cell + filename), UTF-8 with no separator; sort all committed judge-input comparisons across the 15 scored cells by digest hex ascending; take the first 50. SUITE_HASH=b378c79644280bb93fb8ac71d0cadcfe301fd15b226dfaec852b619a2aa1c890. No parity pre-filter. Wording disclosure: the pre-registration named this selection only loosely as "hash-parity" without a full construction; the digest-sort rule above is the implemented deterministic interpretation, disclosed verbatim here rather than claimed as literal pre-registered wording. Rerunning the selection reproduces the identical 50.
- **Judge instrument:** committed judge-input 'prompt' field (the frozen panel instrument + blinded content) plus a strict JSON output-format appendix. Codex saw the identical blinded reports (report_1 / report_2) the panel saw; slots were unblinded to arms with the committed order key only for scoring.
- **Panel-final marks** were reconstructed from the committed judge-outputs with the harness's own `panel_adjudicated` scoring (two-of-three majority, adjudicator on disputes); this reproduces scores.json's per-expectation marks exactly (verified, 0 mismatches on all non-replicated cells).
- **Parsing:** strict JSON extraction, one retry on parse failure; a still-unparseable comparison is recorded `unscorable` and excluded from denominators, never guessed.

## Results

| Scope | Marks | Agree | Concordance |
|---|---:|---:|---:|
| Overall | 394 | 383 | 97.2% |
| Model column: fable | 128 | 123 | 96.1% |
| Model column: haiku | 16 | 16 | 100.0% |
| Model column: opus | 128 | 125 | 97.7% |
| Model column: sonnet | 122 | 119 | 97.5% |
| Panel-disputed marks | 6 | 5 | 83.3% |

**Dispute overlap.** of the marks the two Claude primary judges split on internally, how often Codex sides with the panel-final majority: 5/6 (83.3%).

Raw per-comparison marks, Codex model id + effort, and timestamps are in `codex-concordance.json`.
