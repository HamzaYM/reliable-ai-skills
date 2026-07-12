---
name: staging-to-prod-cutover-campaign
description: Use when standing up a new deployment environment (first staging deploy, or a greenfield production environment), when infra work has been authored but not yet applied, or when deciding what staging config must never be inherited by production. Covers first-apply traps, ops-script deployment pitfalls, and the do-not-inherit scrub.
---

# Staging-to-prod cutover campaign

Standing up real infrastructure (a first staging environment, or a greenfield production environment separate from staging) has a small set of traps that recur across almost every stack, plus one discipline that matters more than any individual trap: **probe the actual live state before acting on what a doc says**, because infra docs rot the moment anyone applies something out of band.

## Step 0: probe, don't assume

Before touching any infrastructure, determine the real state with live commands, not by trusting a doc's last-updated date:

- Has the relevant infra branch/config actually been applied anywhere, or does it only exist as authored-but-unapplied code?
- Does a CI/CD pipeline actually exist and run on the branch you think is live, or does automation live only on an unmerged branch?
- Can you actually authenticate to the target cloud account right now? (Session tokens expire silently and mid-task. Check this before starting any work that touches live infrastructure, not after you hit an auth error partway through.)
- Has the state-backend/bootstrap step (e.g., a Terraform state bucket) actually been created, or does nothing exist yet?

Never proceed on "the doc says X" without a live check backing it up. Treat a doc's own staleness disclaimer as a warning that it needs re-verification, not as ambient permission to trust it anyway.

## Hard rule: never apply, push, or activate automation without an explicit go-ahead

`plan`/`validate`/`diff`/dry-run commands are always safe to run. Anything that creates billable resources, pushes an image, or activates a pipeline that will auto-deploy on future pushes needs an explicit, in-the-moment go-ahead from whoever owns the account, not an inference that "it's probably fine because the branch looks ready." Merging an infra branch that arms an auto-deploy pipeline is itself the action that needs that go-ahead, separate from any individual apply.

## First-apply traps (these recur across almost every stack)

- **DNS/certificate validation can time out on the very first apply**, before the domain's nameservers have actually been pointed at the new infrastructure. This is expected, not a failure: the fix is finishing the manual DNS delegation step and re-applying after propagation, not debugging the certificate module.
- **An empty container registry blocks the first deploy in a chicken-and-egg way**: the compute layer can't start a task with no image to pull. Push a trivial placeholder image first, purely to prove the wiring, before your real image is ready.
- **Placeholder secrets seeded during infra creation are often NOT caught by your weak-secret boot guard**, because that guard's denylist typically only knows about your own dev-environment placeholders, not the placeholder string a cloud provider auto-generates. Replace every placeholder secret with a real value immediately after apply, before the first real workload starts. Don't rely on the app refusing to boot as a safety net here.
- **Automated deploy pipelines commonly don't run your schema migrations for you** on the very first setup. Confirm explicitly whether migrations run automatically or need a manual first pass, and don't assume "the pipeline succeeded" means the schema is current.

## The do-not-inherit scrub, before promoting anything to a stricter environment

Config that's safe in a lower environment and dangerous in a stricter one survives naive copy-paste more often than you'd expect. Build an explicit checklist and review it every time you promote, at minimum:

- Any "developer convenience" flag (debug tools, relaxed auth, preset test accounts): these should be **omitted entirely** from the stricter environment's config, not merely set to false, because "omit vs. false" often has different failure behavior if someone later copies the block wholesale.
- Any shadow/observation-mode AI or experimental feature flag should be fully absent, not just toggled off, since a stray non-empty value elsewhere in the same config can silently re-arm it.
- Any allow-list of internal/test accounts with elevated privileges.
- Any secret injection that's a known dead fossil from a previous architecture: don't recreate it in the new environment just because the old config still references it.
- The deploy-role trust policy and CI/CD authorization: a stricter environment needs its own scoped trust condition, never an inherited or OR'd-together condition shared with a looser environment.

## Rebuild per environment; don't promote a build artifact wholesale

If any client-facing configuration (a base URL, a feature toggle) gets baked into a build artifact at build time rather than read at runtime, promoting the exact same artifact between environments ships the wrong environment's baked-in values with no runtime fix available. Rebuild for each environment's actual config instead of promoting a digest/artifact, and add an automated check that scans the built output for the wrong environment's identifiers before it ships.

## Ops/seed scripts: verify they actually exist in the deployed image

A script that "works locally" is not proven to exist in a containerized deploy unless you've verified it's actually registered in every place the build needs it: a container's file copy allow-list, a pipeline step's explicit file list, and (if it imports sibling files) each of those transitively. This has broken real deploys more than once because deploy-time file inclusion is easy to get subtly wrong even when local execution works perfectly. Write a small static checker that verifies a new script's full import closure is actually included in the deployed image, and run it before merging.

## Separate go-live gates from infra bring-up

Infrastructure can come up completely dark (no real user traffic, every risky feature flag off) well before the business/legal/compliance gates that allow real traffic are satisfied. Don't hold infra work hostage to gates it doesn't actually depend on, and don't let "the infra is ready" become an implicit argument for skipping a compliance gate that's still open. Track them as genuinely separate checklists, and start the longest-lead-time gates (legal sign-off, third-party vendor approvals) as early as possible since they typically take far longer than the engineering work.

## When not to use this

Local development environment setup (not a shared staging/prod environment) is covered by the environment-and-build-hazards skill. Ongoing operational triage of an already-live pipeline (a specific failed deploy, a stuck rollout) is a debugging-playbook problem once the environment itself is established.

*Evidence: one of this skill's three source versions was tested in the pre-registered, order-blinded A/B of July 2, 2026 and passed (must-hits 1/3 cold to 3/3 loaded and 2/3 to 3/3); this merged rewrite was later tested in the July 2026 effort lattice, where the full 17-skill library ran against every model and effort level (results/matrix/MATRIX.md; evidence note updated 2026-07-12).*
