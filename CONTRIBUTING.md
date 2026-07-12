# Contributing to Reliable AI Skills

Thanks for being here. This library has one editorial policy, and everything else follows from it.

## The rule

**No skill merges without a measured delta.**

Not "sounds right." Not "worked for me." A measured delta, produced by the harness in this repo, on a defined task set, graded blind. That rule is why the library is 17 skills instead of 1,700, and it applies to the maintainer the same as it applies to you. The 17 here trace back to 26 production skills distilled from two codebases: every one went through four review passes plus a two-vendor adversarial pass; eight of the 26 were A/B tested against 50 pre-registered must-hit expectations with order-blinded grading, cold runs hit 26/50 (52%), skill-loaded runs hit 46/50 (92%), and all eight passed. The 26 then consolidated into these 17 portable skills (nine merge multiple sources, six carry over one to one, two come from a separate personal library, and one source was dropped as too product-specific). A fresh pre-registered matrix on the 17 as rewritten is complete: raising reasoning effort raised cold capability for all three models tested (H1 supported), and it did not shrink the skills' added value for any of them (H2 not supported), so effort and skills are complements, not substitutes. The full report is [`results/matrix/MATRIX.md`](results/matrix/MATRIX.md).

## What a skill PR needs

1. **The skill itself.** A self-contained folder under `skills/` with a `SKILL.md` following the [Agent Skills spec](https://agentskills.io). The `description` field matters more than you think: it is what decides whether the skill triggers at all. Write it for the router, not for the reader.
2. **A task set.** At least 10 real tasks the skill claims to improve, in the harness task format: one JSON object per line, validated against `eval/schemas/task.schema.json`, each with 2 to 6 pre-registered must-hits. `eval/tasks/example.jsonl` is a complete working task file to copy from. Real tasks from real work; synthetic tasks invite synthetic results.
3. **The freeze.** Pre-register your must-hits before running:

   ```bash
   python3 eval/run.py --tasks your_tasks.jsonl --freeze
   ```

   Commit the freeze file before the run so the pre-registration proof is git history rather than a self-reported timestamp.
4. **The A/B run.** Run on your own API key and commit the full results directory under `results/`:

   ```bash
   python3 eval/run.py --tasks your_tasks.jsonl --ab
   ```

   Baseline and treatment arms, blinded grading, raw judge outputs included so `--replay` can reproduce your numbers byte for byte.
5. **The delta, stated plainly.** In the PR description: must-hits without the skill, must-hits with it, and your read of why. If the delta is small, say so. Honest small beats inflated large every time here.

Before you push, run the same gate CI will:

```bash
python3 eval/run.py --validate
python3 -m unittest discover -s eval/tests
```

## What happens to your PR

Contributors run evals on their own API keys and commit the results with the PR. The free deterministic gate (`--validate` plus the unit tests, no API calls) runs on every PR. The maintainer live-verifies committed runs at discretion, using the `live-ab` workflow. PRs are reviewed in batches, typically within two weeks.

Then the PR climbs the same ladder as everything else shipped here:

- **Checked against the standard.** Does the skill follow the spec, and does the eval run reproduce? (`python3 eval/run.py --replay results/<run-id>` must pass.)
- **Checked against intent.** Does it improve the thing it claims to improve, or a nearby easier thing?
- **Checked against the hardest case.** We will look for the task your skill quietly makes worse. Regressions on the golden suite block the merge even if your own task set improves.

Rejections come with specific notes, never a vague no. Address the notes and climb again.

## Flat results are findings

If you ran the harness and your skill measured flat, open a Discussion anyway. A well-designed skill that does not change behavior tells the community something real about what skills can and cannot do. We would rather host that finding than lose it.

## Everything else

- **Bug reports and harness improvements:** open an issue. The harness is half the project; PRs against `eval/` are very welcome and are held to normal code review, not the delta rule.
- **Docs:** typo and clarity PRs merge fast.
- **Conduct:** be the kind of reviewer you would want on your own work. Attack the work, never the person. That distinction is the whole culture of this repo.

## License

By contributing, you agree your contributions are licensed under MIT, same as the project.
