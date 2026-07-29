# Results sanitization record

Date: 2026-07-11. Applied once, before the repository's first public release, with the owner's explicit approval.

## What was changed and why

Nine files in the committed results tree contained absolute filesystem paths from the machines the evaluation ran on. They leaked local environment details (including a home-directory username from the second run machine) and carried no evaluative content. They were redacted with mechanical, byte-level string replacement. No mark, judgment, score, task content, or model output other than the path strings themselves was altered.

| File | Replacement | Occurrences |
|---|---|---|
| lattice-fable-low/run-state.json | `<absolute local checkout path>/eval/tasks/golden-suite.jsonl` -> `eval/tasks/golden-suite.jsonl` (relativized) | 1 |
| lattice-fable-max/run-state.json | same | 1 |
| lattice-haiku/run-state.json | same | 1 |
| lattice-sonnet-low/run-state.json | same | 1 |
| lattice-sonnet-max/run-state.json | same | 1 |
| lattice-sonnet-low/consumer/mmar-t1-r2-cold.json | `/private/tmp/` -> `<LOCAL-TMP>/` | 4 |
| lattice-sonnet-low/consumer/mmar-t1-r3-loaded.json | `/private/tmp/` -> `<LOCAL-TMP>/` | 4 |
| lattice-opus-max/consumer/mabc-t2-r2-cold.json | `/Users/<machine-2 user>` -> `<HOME>` | 3 |
| lattice-opus-max/judge-inputs/mabc-t2-r2.json | `/Users/<machine-2 user>` -> `<HOME>` | 1 |

## Integrity notes

- One affected file (`lattice-opus-max/judge-inputs/mabc-t2-r2.json`) is a blinded judge input that the judge panel scored before this redaction. The redaction is therefore post-scoring; the recorded marks were produced against the pre-redaction text, which differs only in the four path bytes shown above. The redaction cannot affect, and did not touch, any must-hit judgment.
- The five `run-state.json` edits relativize a metadata field (`task_file`) recording where the frozen task suite lived on the run machine. The suite file itself (`eval/tasks/golden-suite.jsonl`) ships in this repository and its frozen SHA-256 is recorded in the pre-registration; the identity of the suite is hash-anchored, not path-anchored.
- Pre-redaction originals are retained in a local, non-published archive by the author.
- Verification after redaction: every file still parses as JSON, and a recursive scan of all published result cells finds zero remaining absolute path strings.

## Addendum (2026-07-14): missed leak in lattice-fable-max/run-meta.json

The "zero remaining absolute path strings" claim above was wrong. `lattice-fable-max/run-meta.json` contained 19 occurrences (across 13 `reason` fields) of a real local machine temp-file path — `/var/folders/h4/fy5gk_r13dx9lp7b4vl3y0q80000gp/T/cmux-claude-node-options/restore-node-options.XXXXXX.cjs` — embedded in CLI-failure log text (`mktemp: mkstemp failed on ...: File exists`) captured verbatim from the harness's stderr when the model's tool invocation crashed. It is a machine-specific temp path, not personally identifying, and every literal occurrence is identical (the `XXXXXX` is mktemp's own placeholder, not an expanded random suffix). `lattice-fable-max` is excluded from every scored and published number in this repository, but the file itself is published, so the path was still a leak and the completeness claim was still false.

Fixed with the same mechanical, byte-level string replacement used throughout this record: every occurrence of the path was replaced with `<LOCAL-TMP-PATH>`. No other text in the file — task names, arm outcomes, exit codes, or any other content — was touched.

| File | Replacement | Occurrences |
|---|---|---|
| lattice-fable-max/run-meta.json | `/var/folders/h4/fy5gk_r13dx9lp7b4vl3y0q80000gp/T/cmux-claude-node-options/restore-node-options.XXXXXX.cjs` -> `<LOCAL-TMP-PATH>` | 19 |

Verification after this redaction: `run-meta.json` (22,045 bytes before, 20,354 bytes after) still parses as JSON, and a repeat scan of this file finds zero remaining occurrences of the path. The original "recursive scan... finds zero remaining absolute path strings" line above is superseded by this addendum for this file; it was not re-verified against the full results tree beyond this file as part of this fix.

## Addendum (2026-07-26): lattice-fable-max ships its completed run

The statements above that treat `lattice-fable-max` as unscored no longer hold. The cell failed on its first attempt on 2026-07-10, then re-ran and finished on 2026-07-12, covering 16 of the 17 tasks. `mmar-t1` was excluded as invalid, not as a quality failure; the completed run's `run-meta.json` records the reason verbatim as `mmar-t1-r2-loaded: timed out after 600s; mmar-t1-r3-loaded: timed out after 600s`. On 2026-07-26 I copied the completed run's artifacts into this directory over the failed attempt's, so the cell now carries scored data: cold 97.4%, loaded 100.0%, delta +2.6 points, each the mean over three repeats, recomputed here from the shipped `scores.json` and matching the cell's `REPORT.md`. It stays outside the confirmatory 15; Fable's pre-registered endpoint pair is low vs high.

What was copied: `consumer/` (100 files), `judge-inputs/` (48), `judge-outputs/` (101), `order-key.json`, `run-meta.json`, `scores.json`, `scrub-manifest.json`, `comprehension.json`, and `REPORT.md`. One file was deliberately not copied. On the run machine, `run-state.json` recorded `task_file` as an absolute path under a home directory, the same leak the first table covers; the file published here already carries the relativized value from the 2026-07-11 pass and is byte-identical to the source in every other field, so keeping it in place is the redaction.

| File | Replacement | Occurrences |
|---|---|---|
| lattice-fable-max/run-state.json | `<absolute local checkout path>/eval/tasks/golden-suite.jsonl` -> `eval/tasks/golden-suite.jsonl` (relativized in the 2026-07-11 pass, carried forward rather than overwritten from source) | 1 |

`mmar-t1` ships four consumer artifacts and no judge artifacts. Its three cold arms and its repeat-1 loaded arm completed and ship as they ran; `mmar-t1-r2-loaded` and `mmar-t1-r3-loaded` do not exist, because those two arms timed out. The task has no judge input, no judge output, and no mark in any denominator. Those four artifacts ship as evidence of what ran and are excluded from the cell's cost: the addendum cost published in [`results/matrix/NUMBERS.md`](matrix/NUMBERS.md), $219.62, counts only the artifacts for tasks that entered the cell's scores, so an excluded task's partial runs stay out of the cost the same way the task stays out of the score.

The 2026-07-14 addendum above redacted 19 temp-path occurrences from the failed attempt's `run-meta.json`. That file no longer sits in this directory: the completed run's `run-meta.json` replaced it. The replacement records no CLI failures and holds no occurrence of that path. The addendum stands as the record of what the earlier file held.

Verification on the artifacts as they now sit in this directory: all 255 JSON files parse, and a scan of the cell finds zero `/Users/`, zero `/home/`, zero `/var/folders/`, zero `/private/tmp/`, and zero `/tmp/` strings, no API keys, bearer tokens, AWS access-key IDs, GitHub tokens, or private-key blocks, no hostname outside `example.com`, and no email address other than the fixture address `qa@example.com`, which appears 34 times. One absolute path does appear, `/var/tmp/llm-scoring/results.db`, in 15 files. It is a path inside the synthetic `pipeline` fixture rather than anything from a run machine, it is part of the frozen task content, and it already appears in 184 files across the other published cells, so it was left as it is. This scan covers `results/lattice-fable-max` only.

The rest of the tree was not re-scanned as part of this pass, with one exception. The 2026-07-11 line above claiming that "a recursive scan of all published result cells finds zero remaining absolute path strings" does not hold today, beyond the single file the 2026-07-14 addendum corrected. Re-running that scan over the other 15 published cells on 2026-07-26 finds `/var/folders/` machine temp paths in 16 files (36 occurrences, in 7 cells) and `/tmp/` paths in 10 files (32 occurrences, in 4 cells), all of them inside model output text rather than metadata fields, and zero `/Users/`, `/home/`, or `/private/tmp/` strings. Nothing in those 15 cells was redacted in this pass; this paragraph records the measurement, not a fix.
