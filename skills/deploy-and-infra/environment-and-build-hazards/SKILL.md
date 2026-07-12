---
name: environment-and-build-hazards
description: "Use when bringing up or diagnosing a local development environment: services won't start, database connection/permission errors, seed data missing, or when \"local\" development actually points at a shared remote environment and destructive commands are one keystroke away from hitting it."
---

# Environment and build hazards

Most local-environment pain falls into two buckets: a privilege/role mismatch that only shows up as a confusing runtime error, and "local" actually being a shared remote resource in disguise. Both are worth documenting explicitly rather than re-discovering per session.

## The two-role model, if your database enforces row-level isolation

If your database enforces tenant isolation via row-level security (or an equivalent per-tenant policy), you need **two distinct database roles**, not one:

- A schema-owning role, used **only** for running migrations.
- A least-privilege application role with no bypass privileges, used for everything the running app does.

The reason this has to be two roles: a superuser or bypass-privileged connection skips row-level security unconditionally and silently. No error, no warning: every isolation policy just quietly does nothing. If your app ever connects with the migration-owning role "because it was easier," every isolation guarantee in the system is inert without any visible signal that it's broken. On first-time setup, the app-only role is often created by an init script that runs once, at cluster creation. If you ever reset the underlying data volume, that role won't exist until you either re-run the init script by hand or fully recreate the environment.

## Seed data: know exactly what's idempotent and what isn't

Document precisely what a seed script does on a second run: does it add more data, or does it drop and recreate a known synthetic set? Getting this wrong wastes real debugging time (assuming stale seed data is old when it's actually freshly regenerated with new IDs, or vice versa). If a seed script exists specifically to avoid real API costs (a deterministic stand-in swapped in for a real LLM/API call), don't "fix" it by making it call the real service. That defeats its entire purpose.

## The defining hazard when "local" isn't actually local

Some stacks don't have a real local environment at all: "local" development runs against a shared remote database and shared remote auth, typically because standing up a fully local equivalent (a local auth provider, a local database matching production extensions) is more effort than it's worth for a small team. If that's your situation, treat every local database command as a **remote operation against shared state**, and:

- **Never run a schema-mutating command "locally"** if the connection string actually points at shared infrastructure. A destructive migration command run against what you think is a disposable local database can silently mutate the shared environment everyone else depends on.
- **Confirm which environment you're actually pointed at by resource identity** (the actual hostname or account ID), not by an environment-name variable. A shared environment may deliberately set its environment-name variable to look like production, precisely to get production's safety defaults (see the config-and-secrets-hygiene skill for why).
- **A stack-bringup tool (docker-compose, a bootstrap script) that looks current may be a dead fossil** from a previous architecture. If it hasn't been touched in a long time and references services you know were replaced, verify it's actually still wired to anything before spending time debugging why it "doesn't work."

## Cloud auth: verify it before you need it, not when you hit the wall

If any part of a task will touch a shared cloud resource (a remote database, a secrets manager, an infrastructure tool, a deploy), verify you're actually authenticated **at the start of the task**, not when the first API call fails partway through. Session credentials expire silently and often mid-task; a single preflight check at the top saves discovering an expired session in the middle of something you can't easily unwind.

```bash
# generic pattern, substitute your own provider's identity check
your-cloud-cli sts get-caller-identity --profile <profile>
```

If it fails, re-authenticate immediately (this usually opens a browser: tell whoever you're working with and wait for it, rather than silently retrying) and re-check before proceeding.

## Ports, processes, and "it's already running somewhere else"

A surprising fraction of "the stack won't start" reports are actually "something is already listening on that port." Check for a squatting process before debugging application code. Keep a short list of the ports your stack needs and a one-line command to check each one.

## When not to use this

Deploying to, or standing up, a genuinely shared staging or production environment (not your own local dev loop) is the staging-to-prod-cutover-campaign skill. Running the actual test/validation suite once the environment is up is the validation-gates skill.
