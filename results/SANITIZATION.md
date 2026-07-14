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
