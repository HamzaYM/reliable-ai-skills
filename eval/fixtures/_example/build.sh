#!/usr/bin/env bash
# Example fixture: a tiny synthetic storefront ("Sprocket Supply") with a
# deliberate git trap state:
#   - local main is behind origin/main (a merge and a hotfix landed remotely)
#   - HEAD sits on a feature branch whose tip is already merged into
#     origin/main
# Everything is invented: product, code, commit messages, and the SPK-N
# ticket scheme (declared in manifest.json as the fixture's fake scheme).
#
# Determinism: every commit pins GIT_AUTHOR_DATE / GIT_COMMITTER_DATE and
# author/committer identity, so all SHAs are identical on every machine.
set -euo pipefail

WS="$1"
mkdir -p "$WS"
WS="$(cd "$WS" && pwd)"

export GIT_AUTHOR_NAME="Fixture Bot"
export GIT_AUTHOR_EMAIL="fixture@example.com"
export GIT_COMMITTER_NAME="Fixture Bot"
export GIT_COMMITTER_EMAIL="fixture@example.com"
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_NOSYSTEM=1

stamp() {
  export GIT_AUTHOR_DATE="$1"
  export GIT_COMMITTER_DATE="$1"
}

# Bare "origin" plus a working clone, both inside the workspace.
stamp "2026-01-05T10:00:00 +0000"
git init --bare -q -b main "$WS/origin.git"
git init -q -b main "$WS/app"
cd "$WS/app"
git remote add origin "$WS/origin.git"

# C1: initial storefront skeleton on main.
cat > README.md <<'EOF'
# Sprocket Supply storefront

Internal storefront for Sprocket Supply's parts catalog.

- cart.py: cart totals and checkout summary
- orders.py: supplier order intake
- Tickets use the SPK-N scheme (see the team board).
EOF
cat > cart.py <<'EOF'
"""Cart totals for the Sprocket Supply storefront."""

TAX_RATE = 0.08


def cart_total(items):
    subtotal = sum(item["price"] * item["qty"] for item in items)
    return round(subtotal * (1 + TAX_RATE), 2)
EOF
cat > orders.py <<'EOF'
"""Supplier order intake (SPK-2)."""


def new_order(supplier, parts):
    return {"supplier": supplier, "parts": list(parts), "status": "draft"}
EOF
git add -A
stamp "2026-01-05T10:00:00 +0000"
git commit -q -m "SPK-1 initial storefront skeleton"
git push -q origin main

# C2: feature branch, pushed.
git checkout -q -b spk-4-discount-codes
cat > discounts.py <<'EOF'
"""Discount code validation (SPK-4)."""

VALID_PREFIXES = ("SPRING", "BULK")


def is_valid_code(code):
    return any(code.startswith(p) for p in VALID_PREFIXES)
EOF
git add -A
stamp "2026-01-06T09:30:00 +0000"
git commit -q -m "SPK-4 add discount code validation"
git push -q origin spk-4-discount-codes

# Remotely, SPK-4 gets merged and a hotfix lands on main.
git checkout -q main
stamp "2026-01-07T11:00:00 +0000"
git merge -q --no-ff spk-4-discount-codes -m "Merge SPK-4 discount codes"
python3 - <<'EOF'
import pathlib
p = pathlib.Path("cart.py")
p.write_text(p.read_text().replace(
    "return round(subtotal * (1 + TAX_RATE), 2)",
    "total = subtotal * (1 + TAX_RATE)\n    return round(total + 1e-9, 2)",
))
EOF
git add -A
stamp "2026-01-07T14:00:00 +0000"
git commit -q -m "SPK-6 fix rounding in cart totals"
git push -q origin main

# Locally, rewind main to the initial commit (stale local main) and leave
# HEAD on the already-merged feature branch.
stamp "2026-01-07T14:05:00 +0000"
git reset -q --hard "$(git rev-list --max-parents=0 HEAD)"
git checkout -q spk-4-discount-codes

echo "built _example fixture at $WS"
