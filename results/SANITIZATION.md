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
