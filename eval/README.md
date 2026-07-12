# Eval harness

A blinded A/B harness that measures whether a skill actually changes the
behavior of a fresh-context Claude consumer. For each task, one consumer
runs with the skill installed and named in its prompt (the loaded arm) and
one runs without it (the cold arm), inside identical disposable copies of a
synthetic fixture repository. A blinded two-judge panel then grades both
outputs against pre-registered expectations without knowing which is
which; each report-slot mark the two judges disagree on is scored once by
a pinned third adjudicator, the final mark is the two-of-three majority,
and disputed marks never leave any denominator.

Requirements: Python 3.11 or newer, git, and the `claude` CLI for live
runs. There are no pip dependencies. Auth uses your existing Claude
subscription login by default; exporting `ANTHROPIC_API_KEY` works as a
headless fallback. Validation, replay, reporting, tests, and dry runs
never call the API.

## Commands

All commands run from the repository root.

### Run the full A/B on your own task file

```bash
python3 eval/run.py --tasks your_tasks.jsonl --ab
```

Refuses to start unless `your_tasks.freeze.json` exists and matches (see
freeze below). Results land in
`results/<UTC-timestamp>-<name>-<model>-<effort>/`; a run is one cell of
the model x effort matrix and both coordinates are part of the run id.
`eval/tasks/example.jsonl` is a complete working task file to start from.

### Run the full A/B on the repo's golden suite

```bash
python3 eval/run.py --suite golden --ab
```

`--suite golden` resolves to `eval/tasks/golden-suite.jsonl`.

### Run a cell at an explicit consumer effort level

```bash
python3 eval/run.py --suite golden --ab --model claude-fable-5 --effort low
```

`--effort` is passed to every consumer invocation as the claude CLI's own
`--effort` flag (the CLI advertises the levels low, medium, high, xhigh,
max on 2.1.206; all five, including `max`, are accepted end to end). It
applies to consumers only; judges run at their own pinned effort (see the
two-judge panel section below). The flag is fail-closed at two points,
because the CLI itself does not fail on a bad value (it warns on stderr
and silently runs at the default effort):

1. Before any API call, the harness parses `claude --help` and refuses to
   start unless the installed CLI advertises `--effort` and the requested
   level.
2. After every consumer invocation, stderr is scanned for the CLI's
   effort warnings ("Unknown --effort value", "Effort not supported", and
   related forms); any hit fails that run rather than letting it pass as
   the wrong cell.

Without `--effort`, consumers run at the model default and the run is
recorded as effort `default`, except on effort-invariant models where it
is recorded as `none` (see the per-model verification section below).
Either way the effort level is recorded in
`run-meta.json` (`effort`, plus `effort_mechanism` with the verbatim CLI
help evidence) and in every per-consumer result file
(`effort_requested` and `effort_effective`; the two are always equal in a
persisted result because a CLI effort warning fails the run instead).
`run-meta.json` also records `effort_sources`: the
`CLAUDE_CODE_EFFORT_LEVEL` environment variable and the user settings
`effortLevel` key, since either can silently define what "default" meant
for a run.

Session-persistence quirk: the CLI describes `--effort` as the "Effort
level for the current session" and persists the chosen level to the
`effortLevel` key in user settings, so a later invocation WITHOUT
`--effort` can silently inherit the previous session's level as its
"default". The harness therefore passes `--effort` explicitly on every
consumer invocation of an effort-labeled run, records the ambient sources
in `effort_sources`, and treats the value recorded in `run-meta.json` as
authoritative for what a run's effort was.

What is and is not verified: the harness proves the CLI accepted the flag
and did not warn. The claude CLI (2.1.206) exposes no effort field in its
headless JSON output, stream-json init event, or session transcript, so
the request payload itself is not observable without a network intercept;
recorded token usage per run is the closest available proxy for
deliberation depth.

### Per-model effort verification (enumeration, none cells, unavailable by design)

A run is one cell of the model x effort lattice, and both coordinates are
verified per model before any API call:

1. The preflight enumerates the effort support of the requested model and
   records it verbatim in `run-meta.json` under `effort_support`: the
   levels the installed CLI advertises (parsed from `claude --help`, with
   the verbatim help snippet as evidence), whether the model is
   effort-invariant, the resulting per-model `supported_levels`, the
   detected default sources (the `CLAUDE_CODE_EFFORT_LEVEL` environment
   variable and the user settings `effortLevel` key; the CLI exposes no
   per-model default anywhere, so these ambient sources are the only
   observable default inputs and the recorded run-meta effort value is
   authoritative), and which behavioral probe applies.
2. For every effortful model the behavioral probe is the existing
   fail-closed pattern: every consumer invocation's stderr is scanned for
   the CLI's effort warnings, so a persisted run proves the level was
   accepted.
3. Haiku-class models are effort-invariant: they have no effort knob, and
   the claude CLI accepts `--effort` for them with NO stderr warning at
   all (verified live on 2.1.206: `claude -p ... --model haiku --effort
   medium` runs silently). Because the silent acceptance makes the level
   unverifiable, running an effort-invariant model WITH `--effort` fails
   closed before any API call as unavailable by design: the refusal is
   recorded to `results/unavailable/<model>-<effort>.json` (model, effort,
   reason, CLI version, timestamp) and the run never starts. There is no
   silent fallback. Run these models without `--effort`; the cell is then
   recorded as effort `none` (run id `<model>-none`, `effort: "none"` in
   run-meta and in every consumer result), a single effort-invariant
   column excluded from every effort-trend view.

A model-effort combination the CLI itself cannot express (the flag or the
level missing from `claude --help`) still fails closed with the original
error; the `unavailable-by-design` record is specific to combinations
that are impossible by model design rather than by CLI version.

### Two-judge panel with a pinned adjudicator (pre-registered)

Every comparison is graded by two primary judges, never one, with a
pinned third adjudicator resolving their disagreements:

- `claude-sonnet-5` (Sonnet-class) and `claude-opus-4-8` (Opus-class),
  pinned by exact full model ID so a CLI alias change can never move a
  judge. Both are pinned at `--effort medium` on every judge invocation,
  never varying across cells. Both score EVERY blinded comparison fully
  and independently.
- Both judges see the identical blinding stack: the same scrubbed and
  verifier-checked judge inputs, the same seeded order key, and the same
  leak-verifier gate. Judge inputs are committed for audit exactly as
  before.
- Judge invocations are fail-closed like consumers: a CLI effort warning
  on a judge's stderr or a cross-model fallback (a judge answered by any
  model other than the pinned ID) fails that judge run instead of
  persisting it, so persisted judge outputs prove the requested model and
  effort were accepted. Requested and effective values per judge are
  recorded in `run-meta.json` under `judge_panel.judges`.
- Adjudicator (pre-registered, pinned before freeze, immutable after
  data): `claude-fable-5` at `--effort medium`, recorded exactly in
  `run-meta.json` under `adjudicator`. For each report-slot must-hit
  mark the two primaries disagree on, the adjudicator is invoked ONCE
  with a MINIMAL input: the disputed expectation text, the two blinded
  report slots exactly as the primary judges saw them, and the judging
  frame (`agents/adjudicator-prompt.md`). Nothing else (no other
  expectations, no judge notes, no task prompt) can reach it by
  construction. It answers through the narrow binary schema
  `schemas/adjudicator.schema.json` (`hit` plus a verbatim `evidence`
  quote) via the same `--json-schema` mechanism as the judges, with the
  same fail-closed effort and cross-model checks.
- Combination rule (pre-registered): the final mark is the two-of-three
  majority of the two primary marks plus the adjudicator's mark, and
  disputed marks NEVER leave any denominator. Both original marks with
  their evidence quotes, the adjudicator's mark, and the final majority
  result are persisted per dispute in
  `judge-outputs/<pair>.adjudication.json`. Disagreement and
  adjudication rates are published in `scores.json`
  (`judge_disagreement`, with per-task detail plus by-report-slot and
  by-arm breakdowns), in `REPORT.md`, and in matrix outputs (per cell,
  which is the by-model and by-effort breakdown, plus an overall total).
- Adjudicator failure: one retry, then the task is excluded exactly like
  a judge failure (the whole paired comparison leaves the denominator
  and the exclusion is reported). The more-than-one-third floor is the
  FAILURE backstop only: when more than one third of a comparison's
  must-hit marks are judge-failure exclusions (disputed marks with no
  adjudicator result), the entire paired comparison is excluded and
  reported. Adjudicated disagreements never trigger the floor.
- Judging is resumable per judge and per adjudicated mark: each (pair,
  judge) writes its own output file
  (`judge-outputs/<pair>.<judge-id>.json`) the moment it completes, and
  every already-adjudicated mark in a persisted adjudication record is
  reused verbatim on resume, so an interrupted run re-attempts only the
  missing invocations and one judge's failure never discards the other
  judge's completed spend on the same pair.

### Codex concordance sample (exploratory, no API integration)

```bash
python3 eval/run.py --concordance-sample results/<run-a> [results/<run-b> ...] [--out DIR]
```

Selects the pre-registered exploratory cross-vendor sample: 50
comparisons chosen deterministically by hash-parity over the committed
judge inputs, emitted as `manifest.json` (default output directory
`results/concordance-sample/`) for manual re-scoring on Codex. The
selection rule is fixed and content-addressed, so it cannot be steered
after seeing any scores: compute SHA-256 over each committed judge-input
file's bytes, keep the comparisons whose digest is even (digest as an
integer, mod 2 == 0), sort the keepers by digest ascending, take the
first 50. If the even-parity pool is smaller than 50, every kept
comparison is selected and the shortfall stands (no backfill from the
odd-parity pool). The manifest lists each selected comparison's run,
pair, task, judge-input path, and digest, plus the judge schema and
re-scoring instructions. There is deliberately NO Codex API integration:
results are reported as a concordance rate only, exploratory, and never
touch any verdict. The committed judge inputs are public precisely so
third parties can extend the cross-vendor audit.

### Output budget (pinned, pre-registered)

Every consumer invocation, in both arms, at every effort level, runs with
an identical per-message output ceiling of 64000 tokens, pinned via the
`CLAUDE_CODE_MAX_OUTPUT_TOKENS` environment variable on the subprocess.
64000 is the `maxOutputTokens` value the CLI itself reported for the
committed smoke run, so the pin does not change behavior; it prevents the
ceiling from drifting across models, efforts, or CLI upgrades. The value
and mechanism are recorded in `run-meta.json` (`max_output_tokens`), and
every consumer result records `stop_reason`, `answer_chars`,
`peak_message_output_tokens`, and `thinking_usage` (when the CLI exposes
thinking counters; otherwise thinking is folded into `output_tokens`).

A consumer run whose output hits the ceiling (a max_tokens stop reason,
or any single message reaching the pinned limit) is truncated-by-limit
and invalid by pre-registered rule: it is retried once, and if the retry
also fails the task is excluded-as-invalid (paired exclusion: the whole
cold-vs-loaded comparison for that task leaves the denominator, and the
exclusion is listed in the report).

### Requested vs effective model (fallback is invalid)

`run-meta.json` records the requested consumer model (`model`), the
claude CLI version, and `consumer_models_effective` (the union of model
IDs the CLI reports actually answering across included runs). Every
consumer result records `model_requested`, `model_effective`,
`models_effective`, and a `model_fallback` flag. A run answered by a
model other than the requested one (cross-model fallback) is invalid by
pre-registered rule: one retry, then excluded-as-invalid, so a persisted
result always has `model_fallback: false`.

### Staged-skill frontmatter preflight

Before any API call, `--ab` refuses to start if any staged skill's
SKILL.md frontmatter declares `effort`, `model`, `context`, or `agent`:
each of those keys would reconfigure the consumer's runtime in the loaded
arm only, unblinding the comparison. The same check runs in `--validate`.

### Cold-arm isolation

The cold arm is isolated from every skill source, and the isolation is
asserted rather than assumed: (1) cold workspaces are staged into a fresh
temp directory and the harness hard-fails before the consumer starts if
the workspace contains any `.claude` directory; (2) the consumer tool
allowlist (`Read,Grep,Glob,Bash`) exposes no Skill tool, so user-level
and project-level skills cannot be invoked in either arm; (3) the names
of any skills present under `~/.claude/skills` at run time are recorded
in `run-meta.json` (`cold_arm_isolation.ambient_user_skills`) so the
claim is auditable per run.

### Aggregate completed cells into a matrix

```bash
python3 eval/run.py --matrix-report results/<run-a> results/<run-b> [--out DIR]
```

Each argument is one completed cell run (one model x effort combination;
two runs claiming the same cell are refused). Writes `matrix.json` and
`MATRIX.md` (default output directory `results/matrix/`): per skill and
per cell, cold and loaded must-hit rates and the delta in percentage
points, recomputed from each run's raw judge outputs rather than read
from its scores.json, with denominators computed from the data. Every
cell, aggregate and per skill, carries an explicit small-n label (for
example "n=2 tasks, single run per arm: directional only"); treat all
matrix numbers as directional, never inferential.

Each cell's aggregate is reported on two bases, distinguished by a
`basis` field: `aggregate` (available-case: every task valid in that
cell) and `aggregate_complete_case` (complete-case: only the tasks valid
in EVERY cell of the matrix, i.e. paired exclusion extended across
cells, listed top-level as `complete_case_tasks`). Only complete-case
numbers are comparable across cells; multi-effort verdicts use them.
Both blocks carry, alongside the must-hit-weighted `delta_pp`: an
equal-skill-weighted delta (`delta_pp_equal_skill`, every skill weighted
equally regardless of its must-hit count), a headroom-normalized delta
(`headroom_recovered_pct`, (L - C) / (1 - C), undefined when the cold
arm is at ceiling), per-arm ceiling counts (`ceiling_tasks`, tasks where
an arm hit every must-hit), and the small-n label. When the matrix holds
both a low and a max cell for the same model, a top-level `retention`
entry reports the retention ratio R = D(max)/D(low) on the complete-case
must-hit-weighted delta; R is defined only when D(low) > 0, and is null
with an "absolute deltas only" note otherwise.

The matrix aggregates across models AND efforts. A top-level `views`
block (also rendered in MATRIX.md) adds the cross-model lattice views,
all complete-case and all carrying small-n labels:

- `matched_effort` (PRIMARY): models compared side by side at the same
  explicit effort level, one row per model per level. Cells at `default`
  or `none` effort never appear here.
- `defaults_as_shipped` (labeled SECONDARY): each model at its own
  shipped default (`default`, or `none` for effort-invariant models),
  explicitly labeled as conflating model tier and effort level, since
  the shipped defaults differ across models.
- `h4_shrinkage` (EXPLORATORY, directional only): the per-model
  low-to-max delta shrinkage values side by side (D(low), D(max), R per
  model), the same entries as `retention` rendered as one comparison
  row. Exploratory; nothing stronger than direction is claimed, and
  effort-invariant models are excluded from all effort-trend views.

- `h3_visibility_tags` (EXPLORATORY): a labeled note that H3
  (visibility-tag heterogeneity) is exploratory only, computed outside
  the matrix, with no confirmatory verdict. H3 and H4 are both
  explicitly EXPLORATORY; H1 and H2 are the only confirmatory
  hypotheses.

The matrix also carries the confirmatory endpoint verdicts and the
lattice reporting blocks:

- `hypothesis_verdicts` (confirmatory: H1 and H2 only, rendered in
  MATRIX.md as "Hypothesis verdicts"): per model with both a `low` and a
  `max` cell, H1 (cold(max) - cold(low)) and H2 (D(low) - D(max)) under
  the pre-registered 3 pp minimum effect. A difference at or above 3 pp
  reads "directionally supported under the pre-registered rule";
  anything below, including strictly positive differences, reads "not
  supported under the pre-registered rule" (strict inequalities alone
  are never sufficient). Verdicts derive from complete-case endpoint
  cells only; interior cells (medium, high, xhigh) cannot affect H1 or
  H2 under any circumstance, and replicated endpoint cells contribute
  their mean rates over repeats.
- Replicated endpoint cells (runs made with `--repeats N`) are visually
  distinct in MATRIX.md: their rates and delta are BOLD means over
  repeats marked `(RN mean)`, while single-run interior cells stay
  unmarked point values with no uncertainty display. In `matrix.json`
  replicated cells carry `replicated: true` and a `mean_over_repeats`
  block (with the per-repeat values retained) inside each aggregate.
- `invalidation` (per cell; rendered as "Invalidation rates by model x
  effort x arm"): per-arm invalidation counts and rates over planned
  tasks, with natural-completion invalidations (the run finished but was
  invalid, for example a missing Answers section or a cross-model
  fallback) distinguished from harness-censored ones (timeout or the
  pinned output ceiling), plus a judging row for judge and adjudicator
  failures.
- `bootstrap` (rendered as "Task-cluster bootstrap"): a task-cluster
  bootstrap over the complete-case set, resampling whole tasks
  (clusters) with replacement and recomputing the must-hit-weighted
  delta per resample, reported as p2.5/p50/p97.5 per cell. The seed is
  fixed and recorded (deterministic, independent of argument order) and
  the block is labeled descriptive sensitivity only, non-inferential.
- Per-skill PASS/FAIL verdicts are deliberately suppressed in lattice
  outputs (`per_skill_note`): skills appear as rates only, subordinated
  to the per-cell run reports.

Cells produced by two-judge-panel runs also carry their published
`judge_disagreement` block (marks, disagreements, rate; adjudicated
cells add slot-dispute, adjudication, and floor-exclusion counts),
listed in MATRIX.md under "Judge panel disagreement and adjudication"
together with an overall total across cells.

### Freeze must-hits before running (pre-registration)

```bash
python3 eval/run.py --tasks your_tasks.jsonl --freeze
```

Writes `your_tasks.freeze.json` with SHA-256 hashes of the task file, each
task's canonical JSON, each referenced fixture's build script and tree
hash, and the grading instrument itself (`agents/*.md` and
`schemas/*.json`). Commit the freeze file before running the A/B so the
pre-registration proof is git history rather than a self-reported
timestamp. Editing a must-hit, the judge prompt, the judge schema, or the
consumer persona after freezing forces either a visible re-freeze or
`--allow-unfrozen`, which stamps the entire result
`"preregistered": false`. There is no silent path.

### Validate everything (no API calls; run this in CI)

```bash
python3 eval/run.py --validate
```

Checks, in order: skill frontmatter (name matches folder, description
present); every `eval/tasks/*.jsonl` against the task schema and reference
existence, plus the staged-skill frontmatter preflight (no
effort/model/context/agent keys); the sanitization lint over tasks and fixture files (emails,
AWS-account-shaped numbers, non-documentation IPs, real-looking hostnames,
SSN and phone shapes are errors; undeclared ticket-ID shapes, PHI-ish
terms, and person-name heuristics are warnings); freeze consistency for
every frozen task file; a deterministic rebuild of every fixture diffed
against its committed manifest; and replay-scoring of every committed run
under `results/` (recomputed scores must match the committed files
byte-for-byte). Exits nonzero on any error.

If `eval/denylist.local.txt` (or `eval/private-denylist.txt`) exists, each
non-comment line is treated as a banned term and any occurrence is an
error. The file is gitignored so maintainers can scan for client-specific
terms without publishing them.

### Recompute scores from a committed run

```bash
python3 eval/run.py --replay results/<run-id>
```

Recomputes `scores.json` and `REPORT.md` from the run's raw
`judge-outputs/`, `order-key.json`, and `run-meta.json` alone, then
byte-diffs against the committed files. Exits nonzero on any difference.
This is the tamper and consistency gate: published numbers must reproduce
from published raw judge data.

### Re-emit a run's report

```bash
python3 eval/run.py --report results/<run-id>
```

Overwrites `scores.json` and `REPORT.md` from the run's raw data.

### Dry run

```bash
python3 eval/run.py --tasks your_tasks.jsonl --ab --dry-run
```

Verifies the freeze, builds and manifest-checks every fixture, stages
sample workspaces (including the loaded arm's skill copy), prints the full
run plan and a token and cost estimate, and exits without any API calls.

## Flags for --ab

| Flag | Default | Meaning |
|---|---|---|
| `--seed N` | fresh run-time entropy | Seeds order randomization and nothing else. The seed is persisted to `order-key.json`, `run-state.json`, and `run-meta.json`; a run resumed without `--seed` reuses the interrupted run's seed. The default is deliberately not derived from the task file, so an author cannot grind task bytes until the ordering favors one arm. |
| `--concurrency N` | 4 | Parallel consumer and judge subprocesses. |
| `--repeats N` | 1 | Consumer runs per arm per task. Every repeat is fully isolated: its own disposable workspace and its own headless CLI invocation, with no session state shared across repeats, and the repeat index (`-rN`) appears in every artifact (consumer results, judge outputs, adjudication records, order key). For task PASS/FAIL a must-hit counts as HIT for an arm when it hits in a strict majority of repeats; for endpoint cells the verdict-facing aggregate is the MEAN rate across repeats, with every repeat-level value retained in `scores.json` (`repeats_detail`) and rendered in the report. |
| `--judge-repeats N` | 1 | Votes per judge per task (each panel judge casts N votes; majority within a judge first, then the cross-judge agreement rule). |
| `--model NAME` | `sonnet` | Consumer model (claude CLI alias or full ID). |
| `--effort LEVEL` | model default | Consumer effort level, passed to the claude CLI as its `--effort` flag (2.1.206 advertises low, medium, high, xhigh, max). Consumers only; judges run at their own pinned effort. Fail-closed: the run refuses to start unless the installed CLI advertises the flag and the level, refuses effort-invariant models entirely (unavailable by design, recorded under `results/unavailable/`), and any CLI effort warning on a consumer's stderr fails that run. Recorded as `effort` (level, `default`, or `none`) in `run-meta.json` and as `effort_requested` in every consumer result. |
| `--skill NAME` | all | Filter to one skill's tasks (path under `skills/` or bare folder name). The freeze is verified against the full task file first, so filtering keeps `preregistered: true`. |
| `--out DIR` | `results/<UTC-timestamp>-<suite>-<model>-<effort>` | Output directory. Point at an interrupted run's directory to resume it. |
| `--allow-unfrozen` | off | Run despite a missing or mismatched freeze; the result is stamped `"preregistered": false`. |
| `--dry-run` | off | Plan, staging, and cost estimate only; no API calls. |

## Resuming an interrupted run

Every consumer result, and every (pair, judge) invocation's full vote
set, is written to the output directory (atomically, via temp file +
rename) as it completes, and the run configuration is persisted to
`run-state.json` before the first API call. If a run is killed
(rate-limit window, network, Ctrl-C), rerun the exact same command with
`--out` pointing at the same directory: completed work is detected (a
persisted file only counts if it parses and validates) and skipped, and
only the missing runs execute. The order key is generated once and
reused verbatim on resume. A resume with different flags is refused, and
a lock file in the output directory prevents two processes from writing
to the same run concurrently. Judging resumes per judge: each panel
judge's output for a pair is its own file, so one judge's failure never
discards the other judge's completed judgment on the same pair, and a
failed judge invocation excludes its task (reported like a consumer
failure) only if it is still missing after the retry and resume.

## How a run works

1. The task file is loaded, validated, and checked against its freeze.
2. Each fixture is built once into a temp directory and verified against
   its committed manifest (deterministic tree hash and git ref SHAs).
3. Per task, per arm, per repeat: the built fixture template is
   re-verified against its manifest (consumers have `Bash`, so a
   concurrent run could otherwise tamper with the shared template), then
   copied to a disposable workspace. The loaded arm additionally gets the
   skill copied to `.claude/skills/<name>/` and its prompt prefixed with
   an instruction to read it. The cold workspace contains no skill files
   at all. The consumer runs as `claude -p --output-format json` with
   tools `Read,Grep,Glob,Bash`, cwd set to the workspace, a 10 minute
   timeout, and one retry. A post-run snapshot diff (working tree AND git
   refs, so commits, fetches, and branch changes count) logs a warning if
   the consumer mutated anything.
4. Only the `## Answers` section of each report goes to judging. A
   missing or empty Answers section is a hard error for that run: the
   task is excluded and the exclusion is reported; the harness never
   falls back to full report text.
5. Each Answers section is scrubbed: the skill's name and path in every
   variant, `SKILL.md`, `.claude/skills`, generic giveaway phrases, any
   bare mention of "skill"/"skills", and the condition words (cold,
   loaded, arm, baseline, treatment) are replaced with "project
   documentation" (identically in both arms, so the replacement itself
   carries no signal) and every substitution is logged to
   `scrub-manifest.json`.
6. Which report appears first is drawn from a seeded RNG and persisted to
   `order-key.json`, which never enters any judge input by construction.
7. A leak verifier greps every assembled judge input for the banned
   tokens, condition words, and the loaded-arm prompt prefix. Any hit
   aborts the run before a single judge is launched, printing the file
   and offset. Judge inputs are written to the results directory so
   anyone can audit what judges saw.
8. Both panel judges run through the claude CLI with a JSON schema and no
   tools, each grading every expectation HIT or MISS per report with
   verbatim evidence quotes plus a one-line comparative verdict that
   carries no score weight. Each judge is pinned by exact model ID and at
   `--effort medium`, fail-closed on effort warnings and cross-model
   fallback.
9. Each report-slot must-hit mark the two judges disagree on goes to the
   pinned adjudicator once (minimal input: the disputed expectation, the
   two blinded report slots, the judging frame; narrow binary schema).
   Both original marks with evidence, the adjudicator's mark, and the
   final two-of-three majority are persisted to
   `judge-outputs/<pair>.adjudication.json`. An adjudicator failure
   after its retry excludes the task like a judge failure.
10. Scores are computed after unblinding, applying the adjudicated
    combination rule first: agreed marks score directly, disputed marks
    score as the two-of-three majority and stay in every denominator,
    and disagreement plus adjudication rates are published. A disputed
    mark with no adjudicator result is a judge-failure exclusion, and
    when more than one third of a comparison's marks are excluded that
    way the whole paired comparison is excluded and reported (the floor
    never triggers on adjudicated disagreements). A separate mechanical
    check (never a judge) greps the loaded arm's `## Actions` section
    for the skill path to distinguish comprehension failures (the skill
    was never read) from substance failures (read it and still missed);
    it is recorded in `comprehension.json` and never changes a score.

## Pass rules

- Per task: PASS if loaded hits are strictly greater than cold hits AND
  loaded hits reach at least ceil(2/3 of that task's must-hits).
- Per skill: PASS if at least one of its tasks passes AND no task
  regresses (loaded below cold on any task fails the skill).
- Aggregate: total hits per arm over all included expectations. The
  denominator is always computed from the data, never hand-written.
  Excluded tasks shrink the denominator and are listed in the report.

## Results directory layout

```
results/<run-id>/
  run-meta.json        models (requested and effective), effort level plus
                       effort_mechanism evidence, per-model effort_support
                       enumeration, and ambient effort_sources, the judge
                       panel record (pinned judge IDs, pinned judge effort,
                       combination rule, requested and effective values per
                       judge), pinned max_output_tokens, validity rules,
                       cold-arm isolation record, CLI version, seed, freeze
                       hash, preregistered flag, token usage, wall clock
                       (final attempt only when resumed; see the "resumed"
                       flag), exclusions, warnings
  run-state.json       resume state, written before the first API call
  consumer/<task>-<arm>.json    full five-section report plus exit metadata,
                                stop reason, answer length, peak message
                                output tokens, thinking usage, effective
                                model, fallback flag
  judge-inputs/<task>.json      exactly what each judge saw (auditable;
                                identical for both panel judges)
  judge-outputs/<task>.<judge-id>.json   raw structured output per panel
                                judge (legacy single-judge runs keep
                                judge-outputs/<task>.json)
  judge-outputs/<task>.adjudication.json   per disputed report-slot mark:
                                both primary marks with evidence quotes,
                                the adjudicator's mark, and the final
                                two-of-three majority result (written only
                                for comparisons with disputes)
  order-key.json                the unblinding map (published post hoc)
  scrub-manifest.json           every scrub substitution
  comprehension.json            skill-read check per task, non-scoring
  scores.json                   machine-readable scoring
  REPORT.md                     human report; names the cell (consumer
                                model and effort) in its header
```

With `--repeats N` greater than 1, per-pair files are suffixed `-rN`,
every consumer result, judge output, and adjudication record carries a
`repeat` field, each repeat runs in its own freshly staged workspace
through its own CLI invocation (no shared session state), and
`scores.json` gains a `repeats_detail` block with per-repeat aggregates
plus their mean. The
run id carries the cell coordinates (`<model>-<effort label>`, where the
label is the explicit level, `default`, or `none` for effort-invariant
models), so each model x effort cell gets its own directory; `--report`
re-emits one cell's summary and `--matrix-report` combines cells.

## Writing tasks

One JSON object per line; the schema lives at
`eval/schemas/task.schema.json`:

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Unique, lowercase `[a-z0-9-]+`. |
| `skill` | yes | Path under `skills/`, e.g. `change-control/git-change-control-for-agents`. |
| `fixture` | yes | Directory name under `eval/fixtures/`. |
| `prompt` | yes | The base task prompt; both arms and the judge see it. |
| `must_hits` | yes | 2 to 6 items of `{"id", "text"}`; frozen by `--freeze`. |
| `judge_notes` | no | Extra grading guidance shown to the judge (frozen too). |
| `tags` | no | Free-form strings. |

Avoid the words cold, loaded, arm, baseline, treatment, and skill in
prompts and must-hits; the leak verifier bans them from judge inputs, so
their presence in these author-controlled fields aborts every run (the
lint warns about this). Consumer-written answers are different: there the
scrubber neutralizes these words symmetrically instead of aborting.

See `eval/tasks/example.jsonl` for two complete tasks against the example
fixture; every command above is demoable with it.

## Writing fixtures

A fixture is `eval/fixtures/<name>/` containing `build.sh` and
`manifest.json`. `build.sh <dest>` must construct the workspace
deterministically: pin `GIT_AUTHOR_NAME/EMAIL/DATE` and the committer
equivalents for every commit so SHAs are identical on every machine, use
invented names everywhere, and declare a fake ticket scheme. See
`eval/fixtures/_example/build.sh` for the pattern (a bare origin repo plus
a working clone with a stale local main and an already-merged HEAD
branch).

After changing a build script, regenerate the manifest:

```bash
python3 -c "import sys; sys.path.insert(0, 'eval'); from harness import fixtures; \
fixtures.write_manifest('<name>', extra={'fake_ticket_prefixes': ['SPK']})"
```

`--validate` rebuilds every fixture and diffs the tree hash and git refs
against the manifest, which both proves determinism and freezes fixture
content.

## Tests

```bash
python3 -m unittest discover -s eval/tests
```

or, if you have pytest installed:

```bash
python3 -m pytest eval/tests
```

The tests are stdlib-only and cover scoring math, freeze write and verify,
the scrubber's leak cases, order-key blinding, replay determinism,
denominator computation, effort fail-closed verification (including max),
per-model effort enumeration and the effort-invariant `none` cell and
unavailable-by-design record, the two-judge panel (pinned IDs, the per
must-hit agreement rule, disagreement publication, per-judge files and
resume, legacy single-judge compatibility), the adjudicator path (pinned
ID and effort, the minimal input, the narrow schema, slot-dispute
detection on synthetic disagreement fixtures, two-of-three majority with
disputed marks kept in denominators, unresolved disputes as judge-failure
exclusions, the more-than-one-third floor triggering on failures only and
never on adjudicated disagreements, persistence and byte-for-byte
replay), repeats (per-repeat isolated workspaces with no shared session
state, repeat indices in every artifact, retained repeat-level values,
endpoint mean-rate aggregation, replicated-mean rendering), the pinned
output budget and truncation rule, cross-model fallback invalidation, the
staged-skill frontmatter preflight, cold-arm isolation, the matrix's
complete-case, retention, headroom, equal-skill, matched-effort,
defaults-as-shipped, and H4 shrinkage computations, the 3 pp hypothesis
verdicts (exact boundary and interior-cell immunity), the invalidation
table (natural-completion vs harness-censored by arm), the deterministic
task-cluster bootstrap, and the deterministic Codex concordance sample.
They make no API calls.

## What the harness does not measure

Whether Claude Code's router would load the skill autonomously from its
description (the loaded arm names the skill explicitly), long-horizon
effects, and cross-model generalization. Judging is a two-judge Claude
panel (Sonnet-class plus Opus-class, pinned) with a pinned Claude
adjudicator resolving disagreements by two-of-three majority, published
disagreement and adjudication rates, and disputed marks kept in every
denominator, which is still same-vendor: the residual risk is mitigated,
not removed, by the exploratory Codex concordance sample over the
committed judge inputs, which are public precisely so third parties can
extend the cross-vendor audit. Blinding removes labels
and provenance traces, not quality differences, which are the thing
being measured. Read-only consumer
behavior is enforced by disposable workspaces, per-staging template
verification, and post-run snapshot diffs (working tree plus git refs),
not sandboxing. Every run's REPORT.md restates these limitations.
