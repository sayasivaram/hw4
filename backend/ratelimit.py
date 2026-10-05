"""A minimal in-memory sliding-window rate limiter.

Deliberately simple (a dict of deques, no external service) since this is a
single-process dev/demo backend -- the goal is a basic guardrail against a
runaway client hammering the model gateway, not a production-grade limiter
that survives multiple server processes.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 20

_hits: dict[str, deque[float]] = defaultdict(deque)


def check_rate_limit(key: str) -> bool:
    """Record one hit for `key` and return whether it's still within the
    limit. `key` is usually `user:<id>` for a logged-in customer or
    `ip:<address>` for a guest, so each identity gets its own budget."""
    now = time.monotonic()
    hits = _hits[key]
    while hits and now - hits[0] > WINDOW_SECONDS:
        hits.popleft()
    if len(hits) >= MAX_REQUESTS_PER_WINDOW:
        return False
    hits.append(now)
    return True
