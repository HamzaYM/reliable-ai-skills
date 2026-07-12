# Reliable AI Skills

[![validate](https://github.com/HamzaYM/reliable-ai-skills/actions/workflows/evals.yml/badge.svg?branch=main)](https://github.com/HamzaYM/reliable-ai-skills/actions/workflows/evals.yml)

This is a library of 17 Claude Code skills for building and operating AI systems in production: adversarial and tiered review, validation gates, cost and safety guardrails, deploy campaigns, debugging playbooks, and change control. Each one started as a discipline that caught a real bug, prevented a real incident, or shortened a real debugging session in a live system, and was then stripped of every identifying detail and rewritten as a portable pattern that drops into any codebase. The repo also ships the eval harness I use to test whether a skill actually changes agent behavior, because "this prompt seems helpful" is not a bar I am willing to publish against.

**The verdict.** I ran a pre-registered evaluation matrix on all 17 skills, across three Claude models at five reasoning-effort levels plus a Haiku baseline, to settle two questions that were fixed before any run started. First: does raising a model's reasoning effort raise its cold, no-skill capability? Yes, for all three models (hypothesis H1 supported). Second: does that added effort shrink the value the skills add on top? No, for any of them (hypothesis H2 not supported). The skills hold their effectiveness even at the highest effort settings. Effort and skills are complements, not substitutes. The completed run is in [`results/matrix/MATRIX.md`](results/matrix/MATRIX.md).

**See the evidence.** Open the [interactive explorer](results/matrix/explorer.html) to drill into any model-by-effort cell, or read [every number on one page](results/matrix/NUMBERS.md).

**Install** (Claude Code plugin, all 17 skills):

```
/plugin marketplace add HamzaYM/reliable-ai-skills
/plugin install reliable-ai-skills@reliable-ai-skills
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

### Completed: fresh matrix on the 17 as rewritten

A new pre-registered study of the rewritten skills, on a sanitized public task suite, ran on the harness in this repo and is complete. The design pre-registered 16 model-effort conditions (3 models at 5 reasoning-effort levels, plus a Haiku baseline); 15 are fully adjudicated in the final data, because the Fable max-effort cell is a pre-registered open cell that never completed and holds no scored data, so Fable's endpoint is high per the posted amendment. The two confirmatory hypotheses resolved cleanly. H1, that raising effort raises cold (no-skill) capability: supported for all three models under the pre-registered 3-point minimum effect. H2, that raising effort shrinks the skills' added value: not supported for any model (Fable's delta shrank 2.5 points and Sonnet's 2.1, both under the 3-point bar; Opus's grew 0.5). The verdict: effort and skills are complements, not substitutes. Judge panels disagreed on 4.7% of marks, 2.6% of report-slot marks went to adjudication, and none were left unresolved. The full report, recomputed from raw judge outputs by `eval/run.py --matrix-report`, is [`results/matrix/MATRIX.md`](results/matrix/MATRIX.md). Per the pre-registered rule, per-skill PASS/FAIL verdicts are suppressed in lattice outputs; skills appear there as rates only.

## Install

**As a Claude Code plugin** (all 17 skills):

```
/plugin marketplace add HamzaYM/reliable-ai-skills
/plugin install reliable-ai-skills@reliable-ai-skills
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

Evidence lineage refers to the July 2, 2026 study on the source skills (table above). The 17 have also been A/B tested as rewritten in the completed matrix ([`results/matrix/MATRIX.md`](results/matrix/MATRIX.md)); per the pre-registered rule, per-skill lattice verdicts are suppressed there, so the lineage column reports source-study evidence only. Token figures are the full `SKILL.md` body measured as `wc -c` bytes divided by 4, an approximation of tokens (mean about 1,567 across the 17, range 642 to 1,857); Claude Code loads only each skill's name and description up front and reads the full body when it decides the skill applies.

| Skill | What it does | July 2026 evidence lineage | ~Tokens |
|---|---|---|---|
| [multi-model-adversarial-review](skills/adversarial-review/multi-model-adversarial-review) | Runs a second, independently-vendored model against your own review pass and reconciles the findings, instead of one model reviewing its own work. | Sources not measured; A/B tested as rewritten in the completed matrix | 1,652 |
| [tiered-consultancy-review](skills/tiered-review/tiered-consultancy-review) | A five-tier escalation ladder (analysts, managers, specialists, partners, polish) for taking a deliverable from rough draft to genuinely finished. | Net-new from a separate personal library; A/B tested in the completed matrix | 1,407 |
| [pre-merge-validation-gate](skills/validation-gates/pre-merge-validation-gate) | Defines what "done" actually means for a change and how to report test results without overstating what was checked. | Both sources passed (S2: 1/3 → 3/3, 4/4 tie; S5: 0/3 → 3/3, 2/3 tie); A/B tested as rewritten in the completed matrix | 1,518 |
| [architecture-contracts-as-law](skills/architecture-and-contracts/architecture-contracts-as-law) | Keeps a single, merge-blocking source of truth for system invariants (schema, API shape, module boundaries) in sync with the code. | Sources not measured; A/B tested as rewritten in the completed matrix | 1,702 |
| [multi-tenant-auth-reference](skills/auth-and-tenancy/multi-tenant-auth-reference) | A ground-truth reference pattern for token kinds, role checks, and tenant isolation so you stop guessing during auth bugs. | Sources not measured; A/B tested as rewritten in the completed matrix | 1,447 |
| [llm-eval-harness-and-scoring-pipeline](skills/evals-and-scoring/llm-eval-harness-and-scoring-pipeline) | Locked aggregation math, partial-failure handling, prompt versioning, and shadow comparison for any pipeline that scores LLM output. | Sources not measured; A/B tested as rewritten in the completed matrix | 1,596 |
| [ai-cost-tracking-and-guardrails](skills/cost-and-safety-guardrails/ai-cost-tracking-and-guardrails) | Enforced call tracking, safe cross-provider fallover, and fail-closed rate limiting for LLM calls touching money or sensitive data. | Sources not measured; A/B tested as rewritten in the completed matrix | 1,687 |
| [budget-aware-model-allocation](skills/cost-and-safety-guardrails/budget-aware-model-allocation) | How to work deliberately when a token or rate-limit budget is running low across more than one model or provider. | Net-new from a separate personal library; A/B tested in the completed matrix | 642 |
| [config-and-secrets-hygiene](skills/cost-and-safety-guardrails/config-and-secrets-hygiene) | Picking the right config layer, avoiding precedence traps, and a repeatable recipe for adding a new feature flag safely. | Sources not measured; A/B tested as rewritten in the completed matrix | 1,617 |
| [staging-to-prod-cutover-campaign](skills/deploy-and-infra/staging-to-prod-cutover-campaign) | First-apply traps, the do-not-inherit config scrub, and how to separate go-live gates from infra bring-up. | One of three sources passed (S8: 1/3 → 3/3, 2/3 → 3/3); A/B tested as rewritten in the completed matrix | 1,826 |
| [environment-and-build-hazards](skills/deploy-and-infra/environment-and-build-hazards) | The two-role database model, seed-data idempotency, and cloud-auth preflight for local development environments. | Sources not measured; A/B tested as rewritten in the completed matrix | 1,283 |
| [systematic-debugging-playbook](skills/debugging-playbooks/systematic-debugging-playbook) | Establishes ground truth before hypothesizing, and the regression rule for multi-round fix loops after a review pass. | Both sources passed (S3: 1/3 → 3/3, 2/3 → 3/3; S7: 0/3 → 2/3, 2/3 tie); A/B tested as rewritten in the completed matrix | 1,728 |
| [failure-archaeology](skills/debugging-playbooks/failure-archaeology) | A "settled battles" reference so nobody re-attempts an approach that was already tried and deliberately abandoned. | Sources not measured; A/B tested as rewritten in the completed matrix | 1,431 |
| [git-change-control-for-agents](skills/change-control/git-change-control-for-agents) | State verification before any git work, the dead-base PR trap, migration collisions, and working-tree discipline. | Both sources passed (S1: 2/3 → 3/3, 3/3 tie; S6: 1/3 → 3/3 twice); A/B tested as rewritten in the completed matrix | 1,857 |
| [multi-agent-batch-campaigns](skills/campaign-execution/multi-agent-batch-campaigns) | Wave planning, file-contention mapping, and checkpoint-to-file discipline for executing a large backlog across parallel agents. | Source passed (S4: 2/4 → 3/4, 2/3 → 3/3); A/B tested as rewritten in the completed matrix | 1,613 |
| [docs-of-record-and-arbitration](skills/docs-and-compliance/docs-of-record-and-arbitration) | An explicit arbitration order for when project docs disagree, plus a fact-check-first method for business deliverables. | Sources not measured; A/B tested as rewritten in the completed matrix | 1,802 |
| [consent-and-regulated-data-reference](skills/docs-and-compliance/consent-and-regulated-data-reference) | Fail-closed defaults for consent, retention, and audit trails in systems handling regulated personal data. | Sources not measured; A/B tested as rewritten in the completed matrix | 1,837 |

## What's inside a skill file

Every `SKILL.md` in this repository follows the same shape:

1. **Frontmatter**: a `name` matching the folder, and a `description` that states concretely when to reach for it (this is what an agent uses to decide relevance before loading the rest).
2. **The core insight**: one paragraph on the failure mode the skill prevents and why the obvious approach doesn't catch it.
3. **The pattern**: the concrete technique, broken into decision gates, checklists, or tables rather than prose you have to parse under pressure.
4. **When not to use it**: a pointer to the adjacent skill that actually applies, so skills compose instead of overlapping.

Skills with measured July lineage additionally carry a one-line evidence note at the end of the file.

## Methodology

The harness design, blinding scheme, pass rules, and everything the harness does not measure are documented in [eval/README.md](eval/README.md). The longer story of how this library was built, with the review receipts, lives at [hamz.ai/lab](https://www.hamz.ai/lab/). Three honesty notes that belong up front:

- The July judges were **order-blinded** (which report came first was randomized and the key withheld), not content-blinded; the harness in this repo closes that gap by scrubbing condition giveaways from judge inputs and verifying the scrub with a leak check that aborts the run. A post-run audit found exactly one committed judge input (of 456) where a sibling skill's name survived the scrub because the ban list was scoped to the task's own skill; it sits in the contextual Haiku cell, outside every confirmatory hypothesis, and is disclosed in the matrix materials. The scrubber and leak check now ban all seventeen skill names in every variant form.
- Deltas attach to the source skills as tested in their original repos on July 2, 2026. The rewritten skills have since been re-tested; the completed matrix ([`results/matrix/MATRIX.md`](results/matrix/MATRIX.md)) is that re-test, and it suppresses per-skill verdicts per the pre-registered rule.
- Data integrity: early write-ups of the July study reported a /51 denominator; a recount of the recovered per-task judge data during launch prep corrected it to 50, and every number here uses the corrected denominator.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The one rule: no skill merges without a measured delta. Maintainer policy: contributors run evals on their own API keys and commit the results with the PR; the free deterministic gate runs on every PR; the maintainer live-verifies at discretion; PRs are reviewed in batches, typically within two weeks.

## License

[MIT](LICENSE). Use these skills, fork them, adapt them to your own stack.

---

Curated by Hamza Malik, [hamz.ai](https://hamz.ai)
