"""Password hashing and verification.

Uses PBKDF2-HMAC-SHA256, stored as `pbkdf2_sha256$<iterations>$<salt>$<hex digest>`
-- the same shape Django uses for its default hasher, chosen so the iteration
count travels with the hash instead of being hard-coded, which lets it be
raised later without breaking already-stored hashes (old hashes just keep
whatever iteration count they were created with).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 390_000  # OWASP-recommended minimum for PBKDF2-HMAC-SHA256 as of 2023.

SESSION_TTL_SECONDS = 7 * 24 * 3600  # 7 days.
_SECRET_PATH = Path(__file__).resolve().parent / ".session_secret"


def _session_secret() -> bytes:
    """A random secret used to sign session tokens, persisted to a local,
    git-ignored file so tokens survive a server restart (important since
    `--reload` restarts the process on every code change during development)
    rather than regenerating -- and silently invalidating every session --
    each time.
    """
    if _SECRET_PATH.is_file():
        return bytes.fromhex(_SECRET_PATH.read_text(encoding="utf-8").strip())
    secret = secrets.token_bytes(32)
    _SECRET_PATH.write_text(secret.hex(), encoding="utf-8")
    return secret


def create_session_token(user_id: int) -> str:
    """Sign a session token binding this token to exactly one user_id, so a
    request carrying it can't be used to act as a different user -- unlike
    a client simply stating its own user_id in a request body."""
    payload = json.dumps({"uid": user_id, "exp": int(time.time()) + SESSION_TTL_SECONDS}).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload).rstrip(b"=")
    signature = hmac.new(_session_secret(), payload_b64, hashlib.sha256).hexdigest()
    return f"{payload_b64.decode('ascii')}.{signature}"


def verify_session_token(token: str) -> int | None:
    """Return the user_id bound to a valid, unexpired token, or None if the
    token is missing, malformed, expired, or its signature doesn't match --
    in every failure case, treat the request as an anonymous guest rather
    than raising, since a bad/stale token shouldn't break the chat."""
    try:
        payload_b64_str, signature = token.split(".", 1)
    except ValueError:
        return None

    payload_b64 = payload_b64_str.encode("ascii")
    expected_signature = hmac.new(_session_secret(), payload_b64, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        padded = payload_b64 + b"=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
        if int(payload["exp"]) < int(time.time()):
            return None
        return int(payload["uid"])
    except (ValueError, KeyError, TypeError):
        return None


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS).hex()
    return f"{ALGORITHM}${ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    parts = stored_hash.split("$")
    if len(parts) != 4 or parts[0] != ALGORITHM:
        # Hash isn't in our format (e.g. a legacy/seed hash from an unknown
        # scheme) -- can't verify it, so always reject rather than guess.
        return False
    _, iterations_str, salt, expected_digest = parts
    try:
        iterations = int(iterations_str)
    except ValueError:
        return False
    actual_digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    ).hex()
    return hmac.compare_digest(actual_digest, expected_digest)
