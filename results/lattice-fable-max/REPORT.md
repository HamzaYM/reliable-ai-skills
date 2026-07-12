# A/B eval report: lattice-fable-max

- Consumer model: claude-fable-5
- Consumer effort: max
- Max output tokens (pinned, both arms): 64000
- Judge panel: claude-sonnet-5 + claude-opus-4-8 (both pinned at --effort medium)
- Adjudicator: claude-fable-5 (pinned at --effort medium, invoked once per disputed report-slot mark, two-of-three majority)
- claude CLI: 2.1.206 (Claude Code)
- Seed: 15602153937591721000
- Preregistered: yes
- Freeze: 2026-07-10T08:32:03Z (task file sha256 b378c7964428)
- Repeats: 3 consumer / 1 judge
- Wall clock: 844.5 s

## Aggregate

Cold 0/0 | Loaded 0/0 | Delta +0

The denominator is the frozen must-hit count over included tasks,
computed from the data.

Repeat-level aggregates (replicated cell; every repeat ran in its own isolated workspace with no shared session state):

| Repeat | Cold | Loaded | Delta (pp) |
|---|---|---|---|
| r1 | 0/0 (-) | 0/0 (-) | - |
| r2 | 0/0 (-) | 0/0 (-) | - |
| r3 | 0/0 (-) | 0/0 (-) | - |

Endpoint mean over repeats: cold - | loaded - | delta - pp.

## Per-skill results

| Skill | Tasks | Cold hits | Loaded hits | Delta | Result |
|---|---|---|---|---|---|

## Per-task must-hits

## Comprehension check (stage B, unblinded, non-scoring)

| Task | Skill read in the with-skill run |
|---|---|

## Run notes

- Excluded tasks: aicg-t2, arch-contracts-t1, bama-t1, consent-t2, csh-t1, dora-t2, env-hazards-t1, eval-harness-t1, farch-t1, git-cc-t2, mabc-t2, mmar-t1, mt-auth-t1, pmvg-t2, s2p-cutover-t1, sysdbg-t2, tcr-t1
- Exclusions by failing arm: cold 17, loaded 17
- Scrub substitutions: 0
- Workspace mutation warnings: none

## Limitations

1. Single-run variance. Unless repeats > 1, each arm was sampled once per
   task; per-task results near ties are not statistically meaningful. Treat
   the aggregate delta and only large per-task swings as signal.
2. Vocabulary echo limits blinding. Judges never see condition labels,
   skill names, paths, or tool logs, and inputs are verifier-checked, but a
   skill that works changes answer content. Blinding removes provenance,
   not the measured effect. Judge inputs are committed for audit.
3. Same-vendor judging. Every comparison is graded by a two-judge
   panel (one Sonnet-class and one Opus-class judge, exact IDs pinned,
   both at medium effort) behind the identical blinding stack; each
   report-slot mark they disagree on is scored once by a pinned
   adjudicator on a minimal input, the final mark is the two-of-three
   majority, disputed marks never leave any denominator, and
   disagreement plus adjudication rates are published. All three judges
   are still Claude models: the residual same-vendor risk is mitigated,
   not removed, by the pre-registered exploratory Codex concordance
   sample re-scored on the committed judge inputs, which are public
   precisely so third parties can extend the cross-vendor audit.
4. Explicit loading, not triggering. These results say nothing about
   whether the description gets the file read autonomously in real
   sessions.
5. Synthetic fixtures. Trap states reconstruct real failure classes in
   small repos; deltas may be conservative or optimistic, direction
   unknown.
6. Read-only is enforced by construction (disposable workspaces,
   per-staging template verification, and post-run snapshot diffs over
   the working tree and git refs), not sandboxing.
