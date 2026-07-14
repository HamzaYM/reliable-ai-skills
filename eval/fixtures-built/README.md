# Materialized fixture trees (generated, read-only)

This directory is a convenience copy of the eval fixtures, checked out as
plain files so you can read them directly in the GitHub UI. It is generated,
not hand-written, and it is not what the harness runs on.

## Source of truth

Each fixture is defined by a deterministic generator script:

- `eval/fixtures/saasapp/build.sh` (with `repos_*.sh`)
- `eval/fixtures/docsrepo/build.sh`
- `eval/fixtures/pipeline/build.sh` (with `repos_*.sh`)

The eval harness builds each fixture from those scripts into a disposable
workspace at run time (`eval/harness/fixtures.py`, `build_fixture`). It never
reads this directory. The trees here are a snapshot of that build output, so
the files a task references can be opened and read on their own instead of
being located as heredocs inside a generator script.

## What is here

For each fixture, every repository's working tree at its checked-out HEAD,
exactly as the harness stages it. The `manifest.json` next to each fixture's
`build.sh` records the expected tree hash and every git SHA; a fresh build
reproduces both byte for byte.

- `saasapp/` — 15 synthetic repos
- `docsrepo/` — 3 synthetic repos
- `pipeline/` — 14 synthetic repos

## What is omitted

- `.git/` history. Only the working tree is materialized; the commit SHAs and
  refs live in each fixture's `manifest.json`.
- The bare `*-origin.git` remotes that a few repos push to and fetch from.
  They hold git internals only, with no readable working tree.

## Everything here is synthetic

Every product name, repository, file, commit message, ticket id, and seeded
config value is invented for evaluation. There is no real client, customer, or
proprietary code. The `.env` and token values are deliberate fake trap states
for the secrets-hygiene and config tasks (for example
`SECRET = "synthetic-signing-key"` and `..._SYNTHETIC0000`). See each fixture's
`build.sh` header and its `manifest.json` description.

## Do not edit by hand

These files are regenerated from the scripts. To change a fixture, edit its
generator and rebuild; edits made here would be overwritten and would drift
from the manifest hash the harness verifies on every run.
