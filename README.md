# Reliable AI Skills

[![validate](https://github.com/HamzaYM/reliable-ai-skills/actions/workflows/evals.yml/badge.svg?branch=main&event=push)](https://github.com/HamzaYM/reliable-ai-skills/actions/workflows/evals.yml)

This is a skills library: 17 Claude Code agent skills for building and operating AI systems in production, covering adversarial and tiered review, validation gates, cost and safety guardrails, deploy campaigns, debugging playbooks, and change control. Each one started as a discipline that caught a real bug, prevented a real incident, or shortened a real debugging session in a live system, and was then stripped of every identifying detail and rewritten as a portable pattern that drops into any codebase. The repo also ships the eval harness I use to test whether a skill actually changes agent behavior, because "this prompt seems helpful" is not a bar I am willing to publish against.

**The verdict.** I ran a pre-registered evaluation matrix on all 17 skills, across three Claude models at five reasoning-effort levels plus a Haiku baseline, to settle two questions that were fixed before any run started. First: does raising a model's reasoning effort raise its cold, no-skill capability? Yes, for all three models (hypothesis H1 supported). Second: does that added effort shrink the value the skills add on top? No, for any of them (hypothesis H2 not supported). The skills hold their effectiveness even at the highest effort settings. Effort and skills are complements, not substitutes. The completed run is in [`results/matrix/MATRIX.md`](results/matrix/MATRIX.md).

**See the evidence.** Open the [interactive explorer](results/matrix/explorer.html) to drill into any model-by-effort cell, read [every number on one page](results/matrix/NUMBERS.md), or follow the whole study end to end in the write-up, [The effort lattice](https://www.hamz.ai/lab/lattice/).

**Install** (Claude Code plugin, all 17 skills):

```
/plugin marketplace add HamzaYM/reliable-ai-skills
/plugin install reliable-ai-skills@hamz-ai
```

Manual and single-skill install paths are under [Install](#install) below.

Here is where they came from. In July 2026 I distilled 26 skills from two production codebases I run Claude Code against. Every one went through four review passes plus an adversarial pass by a second model vendor. Eight of the 26 were then A/B tested against 50 pre-registered must-hit expectations across 16 tasks, with order-blinded judges grading both arms: cold runs hit 26/50 (52%), skill-loaded runs hit 46/50 (92%), and all eight passed the pre-registered rule. Fifteen of the 17 portable skills here were consolidated from those 26; the other two came from my own tooling and went through the same review passes. Those 17 rewritten skills are what the matrix above tested, on the harness in [`eval/`](eval/README.md).

## The July 2026 study

The table below is the July 2, 2026 study on the **source skills**, as tested inside their original repositories before consolidation. Each source skill ran two tasks; each task has 3 or 4 pre-registered must-hit expectations, graded per arm by order-blinded judges. The rewritten skills in this repo inherit this lineage and have since been re-tested in their rewritten form; the completed matrix below is that re-test.

| # | Source skill (origin anonymized) | Task 1 cold → loaded | Task 2 cold → loaded | Consolidated into |
|---|---|---|---|---|
| S1 | Change control, repo A | 3/3 → 3/3 | 2/3 → 3/3 | [git-change-control-for-agents](skills/change-control/git-change-control-for-agents) |
| S2 | Validation gate, repo A | 1/3 → 3/3 | 4/4 → 4/4 | [pre-merge-validation-gate](skills/validation-gates/pre-merge-validation-gate) |
| S3 | Debugging playbook, repo A | 1/3 → 3/3 | 2/3 → 3/3 | [systematic-debugging-playbook](skills/debugging-playbooks/systematic-debugging-playbook) |
| S4 | Backlog-waves campaign, repo A | 2/4 → 3/4 | 2/3 → 3/3 | [multi-agent-batch-campaigns](skills/campaign-execution/multi-agent-batch-campaigns) |
| S5 | Validation and QA, repo B | 0/3 → 3/3 | 2/3 → 2/3 | [pre-merge-validation-gate](skills/validation-gates/pre-merge-validation-gate) |
| S6 | Change control, repo B | 1/3 → 3/3 | 1/3 → 3/3 | [git-change-control-for-agents](skills/change-control/git-change-control-for-agents) |
| S7 | Debugging playbook, repo B | 0/3 → 2/3 | 2/3 → 2/3 | [systematic-debugging-playbook](skills/debugging-playbooks/systematic-debugging-playbook) |
| S8 | Prod cutover campaign, repo B | 1/3 → 3/3 | 2/3 → 3/3 | [staging-to-prod-cutover-campaign](skills/deploy-and-infra/staging-to-prod-cutover-campaign) |

**Totals: cold 26/50 (52%), loaded 46/50 (92%).** Pass rule, fixed before any run: a task passes if loaded strictly beats cold and loaded reaches at least two thirds of its must-hits; a skill passes if at least one task passes and none regresses. All 8 tested skills passed. The headline row: on a regulated-data consent scenario (S5, task 1), the cold agent missed every must-hit and the loaded agent hit all three.

Four of those 16 task results were ties, and they split two ways. Two are ceiling ties, where the cold arm had already hit everything on offer: S2 task 2 (4/4 → 4/4) and S1 task 1 (3/3 → 3/3). Two are flat ties, where the cold arm still had room left and the skill moved nothing: S5 task 2 (2/3 → 2/3) and S7 task 2 (2/3 → 2/3). At three or four expectations per task a single mark swings a result, so I read all sixteen as direction and not as values I would defend to the decimal.

### Completed: fresh matrix on the 17 as rewritten

A new pre-registered study of the rewritten skills, on a sanitized public task suite, ran on the harness in this repo and is complete. The design pre-registered 16 model-effort conditions (3 models at 5 reasoning-effort levels, plus a Haiku baseline); 15 form the confirmatory matrix and are fully adjudicated in the final data. Fable's confirmatory endpoint is high per the posted amendment, and the Fable max-effort cell sits outside the confirmatory 15: its first attempt failed, then it re-ran and finished 16 of the 17 tasks on 2026-07-12 (`mmar-t1` was excluded as invalid after its loaded arm timed out at 600 seconds on two of the three repeats, not as a quality failure). Its scored data ships as an addendum in [`results/lattice-fable-max`](results/lattice-fable-max), cold 97.4% and loaded 100.0% as the mean over three repeats, and no confirmatory number in this study uses it. The two confirmatory hypotheses resolved cleanly. H1, that raising effort raises cold (no-skill) capability: supported for all three models under the pre-registered 3-point minimum effect. H2, that raising effort shrinks the skills' added value: not supported for any model (Fable's delta shrank 2.5 points and Sonnet's 1.5, both under the 3-point bar; Opus's grew 0.5). The verdict: effort and skills are complements, not substitutes. Judge panels disagreed on 4.6% of marks, 2.5% of report-slot marks went to adjudication, and none were left unresolved. The full report, recomputed from raw judge outputs by `eval/run.py --matrix-report`, is [`results/matrix/MATRIX.md`](results/matrix/MATRIX.md). Per the pre-registered rule, per-skill PASS/FAIL verdicts are suppressed in lattice outputs; skills appear there as rates only.

## Install

**As a Claude Code plugin** (all 17 skills):

```
/plugin marketplace add HamzaYM/reliable-ai-skills
/plugin install reliable-ai-skills@hamz-ai
```

**Manual, one skill in a project:**

```bash
mkdir -p .claude/skills
cp -r skills/<category>/<skill-name> .claude/skills/
```

**Manual, the whole library:**

```bash
git clone https://github.com/HamzaYM/reliable-ai-skills.git
mkdir -p .claude/skills
cp -r reliable-ai-skills/skills/*/* .claude/skills/
```

Each skill is a self-contained folder with one `SKILL.md`: YAML frontmatter (`name`, `description`) followed by the instructions Claude follows when the skill is active. No external dependencies, no build step. Skills also work with any agent harness that reads the same `SKILL.md` convention. **Browse first:** [INDEX.md](INDEX.md) is a flat one-page table of every skill.

## Run the eval harness

The harness is stdlib-only Python 3.11+; validation, replay, reporting, and tests never call the API. Full documentation: [eval/README.md](eval/README.md).

Validate everything (no API calls; this is what CI runs):

```bash
python3 eval/run.py --validate
```

Freeze must-hits before running (pre-registration):

```bash
python3 eval/run.py --tasks your_tasks.jsonl --freeze
```

Run the full A/B on your own task file:

```bash
python3 eval/run.py --tasks your_tasks.jsonl --ab
```

Run the full A/B on the repo's golden suite:

```bash
python3 eval/run.py --suite golden --ab
```

The golden suite ships frozen: its hash manifest (`eval/tasks/golden-suite.freeze.json`) is committed alongside it, and `--ab` verifies the manifest before running. If you edit the suite, re-freeze first with `--freeze` (your run is then marked as not pre-registered against the shipped manifest, which is the honest label for it).

Aggregate completed cells into a matrix:

```bash
python3 eval/run.py --matrix-report results/<run-a> results/<run-b> [--out DIR]
```

Recompute scores from a committed run (the tamper and consistency gate):

```bash
python3 eval/run.py --replay results/<run-id>
```

Tests:

```bash
python3 -m unittest discover -s eval/tests
```

## The 17 skills

I validated this library at the library level, not skill by skill. All 17 went through the same blinded A/B in the completed matrix, and the pre-registered rule reports that run as rates across the whole set instead of per-skill verdicts, so [`results/matrix/MATRIX.md`](results/matrix/MATRIX.md) carries the evidence for every skill in the table below. Five of the 17 additionally carry a signal from the July 2, 2026 study on the source skills (table above), and that is what the third column reports, as raw must-hit counts rather than a verdict. Token figures are the full `SKILL.md` body measured as `wc -c` bytes divided by 4, an approximation of tokens (mean about 1,629 across the 17, range 749 to 2,209); Claude Code loads only each skill's name and description up front and reads the full body when it decides the skill applies.

| Skill | What it does | Source-study signal (July 2, 2026) | ~Tokens |
|---|---|---|---|
| [multi-model-adversarial-review](skills/adversarial-review/multi-model-adversarial-review) | Runs a second, independently-vendored model against your own review pass and reconciles the findings, instead of one model reviewing its own work. | Sources not measured | 2,209 |
| [tiered-consultancy-review](skills/tiered-review/tiered-consultancy-review) | A five-tier escalation ladder (analysts, managers, specialists, partners, polish) for taking a deliverable from rough draft to genuinely finished. | Net-new from a separate personal library, no source study | 1,568 |
| [pre-merge-validation-gate](skills/validation-gates/pre-merge-validation-gate) | Defines what "done" actually means for a change and how to report test results without overstating what was checked. | S2: 1/3 → 3/3 and 4/4 → 4/4; S5: 0/3 → 3/3 and 2/3 → 2/3 | 1,557 |
| [architecture-contracts-as-law](skills/architecture-and-contracts/architecture-contracts-as-law) | Keeps a single, merge-blocking source of truth for system invariants (schema, API shape, module boundaries) in sync with the code. | Sources not measured | 1,727 |
| [multi-tenant-auth-reference](skills/auth-and-tenancy/multi-tenant-auth-reference) | A ground-truth reference pattern for token kinds, role checks, and tenant isolation so you stop guessing during auth bugs. | Sources not measured | 1,447 |
| [llm-eval-harness-and-scoring-pipeline](skills/evals-and-scoring/llm-eval-harness-and-scoring-pipeline) | Locked aggregation math, partial-failure handling, prompt versioning, and shadow comparison for any pipeline that scores LLM output. | Sources not measured | 1,596 |
| [ai-cost-tracking-and-guardrails](skills/cost-and-safety-guardrails/ai-cost-tracking-and-guardrails) | Enforced call tracking, safe cross-provider fallover, and fail-closed rate limiting for LLM calls touching money or sensitive data. | Sources not measured | 1,687 |
| [budget-aware-model-allocation](skills/cost-and-safety-guardrails/budget-aware-model-allocation) | How to work deliberately when a token or rate-limit budget is running low across more than one model or provider. | Net-new from a separate personal library, no source study | 749 |
| [config-and-secrets-hygiene](skills/cost-and-safety-guardrails/config-and-secrets-hygiene) | Picking the right config layer, avoiding precedence traps, and a repeatable recipe for adding a new feature flag safely. | Sources not measured | 1,618 |
| [staging-to-prod-cutover-campaign](skills/deploy-and-infra/staging-to-prod-cutover-campaign) | First-apply traps, the do-not-inherit config scrub, and how to separate go-live gates from infra bring-up. | S8: 1/3 → 3/3 and 2/3 → 3/3; its two other sources not measured | 1,865 |
| [environment-and-build-hazards](skills/deploy-and-infra/environment-and-build-hazards) | The two-role database model, seed-data idempotency, and cloud-auth preflight for local development environments. | Sources not measured | 1,283 |
| [systematic-debugging-playbook](skills/debugging-playbooks/systematic-debugging-playbook) | Establishes ground truth before hypothesizing, and the regression rule for multi-round fix loops after a review pass. | S3: 1/3 → 3/3 and 2/3 → 3/3; S7: 0/3 → 2/3 and 2/3 → 2/3 | 1,766 |
| [failure-archaeology](skills/debugging-playbooks/failure-archaeology) | A "settled battles" reference so nobody re-attempts an approach that was already tried and deliberately abandoned. | Sources not measured | 1,432 |
| [git-change-control-for-agents](skills/change-control/git-change-control-for-agents) | State verification before any git work, the dead-base PR trap, migration collisions, and working-tree discipline. | S1: 3/3 → 3/3 and 2/3 → 3/3; S6: 1/3 → 3/3 and 1/3 → 3/3 | 1,896 |
| [multi-agent-batch-campaigns](skills/campaign-execution/multi-agent-batch-campaigns) | Wave planning, file-contention mapping, and checkpoint-to-file discipline for executing a large backlog across parallel agents. | S4: 2/4 → 3/4 and 2/3 → 3/3 | 1,652 |
| [docs-of-record-and-arbitration](skills/docs-and-compliance/docs-of-record-and-arbitration) | An explicit arbitration order for when project docs disagree, plus a fact-check-first method for business deliverables. | Sources not measured | 1,802 |
| [consent-and-regulated-data-reference](skills/docs-and-compliance/consent-and-regulated-data-reference) | Fail-closed defaults for consent, retention, and audit trails in systems handling regulated personal data. | Sources not measured | 1,836 |

## What's inside a skill file

Every `SKILL.md` in this repository follows the same shape:

1. **Frontmatter**: a `name` matching the folder, and a `description` that states concretely when to reach for it (this is what an agent uses to decide relevance before loading the rest).
2. **The core insight**: one paragraph on the failure mode the skill prevents and why the obvious approach doesn't catch it.
3. **The pattern**: the concrete technique, broken into decision gates, checklists, or tables rather than prose you have to parse under pressure.
4. **When not to use it**: a pointer to the adjacent skill that actually applies, so skills compose instead of overlapping.

Skills with measured July lineage additionally carry a one-line evidence note at the end of the file.

## How the 17 sort

Two classifications, both taken from reading the files rather than from the folder names.

**By what the skill is.**

| Type | Skills |
|---|---|
| Reference, a ground-truth table you check yourself against | multi-tenant-auth-reference, consent-and-regulated-data-reference (2) |
| Procedural, an ordered method with gates | systematic-debugging-playbook, pre-merge-validation-gate, git-change-control-for-agents, tiered-consultancy-review, multi-model-adversarial-review, staging-to-prod-cutover-campaign, multi-agent-batch-campaigns, failure-archaeology, architecture-contracts-as-law, docs-of-record-and-arbitration (10) |
| Domain implementation, how to build one specific kind of system | llm-eval-harness-and-scoring-pipeline, ai-cost-tracking-and-guardrails, config-and-secrets-hygiene, environment-and-build-hazards (4) |
| Agent self-governance, how the agent spends its own budget | budget-aware-model-allocation (1) |

budget-aware-model-allocation gets a row of its own because it fits none of the other three. It is not a lookup table, it prescribes no ordered procedure, and it implements nothing in your system: it tells the agent how to ration its own token and rate-limit budget across providers, and the file itself says "this is judgment, not a hard gate." Filing it under Procedural would claim gates it deliberately refuses to have.

**By how the skill is named.** Three names are branded rather than descriptive: failure-archaeology, tiered-consultancy-review, docs-of-record-and-arbitration. architecture-contracts-as-law sits on the line, since "contracts" and "law" both carry real meaning inside that file. The other 13 say plainly what they do.

## Methodology

The harness design, blinding scheme, pass rules, and everything the harness does not measure are documented in [eval/README.md](eval/README.md). The longer story of how this library was built, with the review receipts, lives at [hamz.ai/lab](https://www.hamz.ai/lab/). Three honesty notes that belong up front:

- The July judges were **order-blinded** (which report came first was randomized and the key withheld), not content-blinded; the harness in this repo closes that gap by scrubbing condition giveaways from judge inputs and verifying the scrub with a leak check that aborts the run. A post-run audit found exactly one committed judge input (of 456) where a sibling skill's name survived the scrub because the ban list was scoped to the task's own skill; it sits in the contextual Haiku cell, outside every confirmatory hypothesis, and is disclosed in the matrix materials. The scrubber and leak check now ban all seventeen skill names in every variant form.
- Deltas attach to the source skills as tested in their original repos on July 2, 2026. The rewritten skills have since been re-tested; the completed matrix ([`results/matrix/MATRIX.md`](results/matrix/MATRIX.md)) is that re-test, and it suppresses per-skill verdicts per the pre-registered rule.
- Data integrity: early write-ups of the July study reported a /51 denominator; a recount of the recovered per-task judge data during launch prep corrected it to 50, and every number here uses the corrected denominator.

**An anecdote, not evidence.** I caught two bugs in this harness's reporting code with a stacked review, which is the method [multi-model-adversarial-review](skills/adversarial-review/multi-model-adversarial-review) prescribes and which is one of the ten skills with no source-study signal. A Sonnet recon pass read the report code against the pre-registration and found that `_endpoint_cells()` hardcoded low-versus-max for every model, ignoring the posted amendment that moves Fable's confirmatory endpoint to low-versus-high. An Opus pass at high effort re-derived the same claim on its own and confirmed it. An Opus pass at xhigh effort, running as a completeness critic, then found the larger one: the complete-case task set feeding H1, H2 and retention was a single global intersection across every cell rather than a per-model intersection over that model's own endpoint cells, so one model's task exclusion could silently shrink another model's confirmatory delta. I fixed both and covered them with new tests before any confirmatory number existed. Two qualifiers, because they change what this shows: all three passes were Claude models at different tiers, so it exercises the skill's different-sizes branch and not the cross-vendor branch it leads with, and the passes ran one after another while the skill prescribes running them concurrently.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The one rule: no skill merges without a measured delta. Maintainer policy: contributors run evals on their own API keys and commit the results with the PR; the free deterministic gate runs on every PR; the maintainer live-verifies at discretion; PRs are reviewed in batches, typically within two weeks.

## License

[MIT](LICENSE). Use these skills, fork them, adapt them to your own stack.

---

Curated by Hamza Malik, [hamz.ai](https://hamz.ai)
