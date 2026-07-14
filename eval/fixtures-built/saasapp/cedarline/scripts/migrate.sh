#!/usr/bin/env bash
set -euo pipefail
for f in db/migrations/*.sql; do
  psql "postgresql://cedar_owner:ownerpw@localhost:5432/cedar" -f "$f"
done
