"""Credential minting and verification.

Two credential types exist:
- session tokens (kind='session', long TTL), minted only by a full login;
- link tokens (kind='link', short TTL, resource_id claim) minted when a
  shared-appointment link is redeemed. There is no token-refresh endpoint.
"""
import base64
import json
import time

SECRET = "synthetic-signing-key"


def _encode(claims):
    return base64.urlsafe_b64encode(json.dumps(claims).encode()).decode()


def mint_session_token(user):
    return _encode({"kind": "session", "sub": user["id"],
                    "tenant_id": user["tenant_id"],
                    "exp": time.time() + 30 * 86400})


def mint_link_token(resource_id, tenant_id):
    return _encode({"kind": "link", "resource_id": resource_id,
                    "tenant_id": tenant_id, "exp": time.time() + 900})


def verify_token(bearer):
    raw = bearer.removeprefix("Bearer ").strip()
    claims = json.loads(base64.urlsafe_b64decode(raw or _encode({})))
    return claims
