"""Tool functions available to the Campus Customs agent.

Each function here is plain Python -- no PydanticAI imports -- so it can be
unit-tested or called directly without spinning up an agent. agent.py wraps
each one as an `@agent.tool_plain` so the model can call it by name.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import database
from models import AuditEntry, InventorySize, ProductCard, StockInfo

ROOT = Path(__file__).resolve().parent
AUDIT_TRAIL_PATH = ROOT.parent / "output" / "audit_trail.json"
# Upper bound on one search call, not a target -- Problem 7 requires every
# real catalogue match for a category question to reach the website, so this
# only exists to cap a pathological query, not to truncate a normal one
# (the full catalogue is 102 products, so no real category comes close).
MAX_SEARCH_RESULTS = 50

# .env lives at the Homework 4 project root (sibling of backend/, frontend/,
# output/) -- see .env.example for the keys this project needs. Load only
# the model settings this project needs, without printing or copying any
# secret values.
_ENV_PATH = ROOT.parent / ".env"
if _ENV_PATH.exists():
    for _line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in _line and not _line.lstrip().startswith("#"):
            _key, _value = _line.split("=", 1)
            if _key.strip() in {"PORTKEY_API_KEY", "PORTKEY_MODEL", "OPENAI_API_KEY"}:
                os.environ.setdefault(_key.strip(), _value.strip().strip("\"'"))


def model_for_agent() -> object:
    """Return a PydanticAI model, routed through Portkey when configured."""
    from openai import AsyncOpenAI
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    model_id = os.getenv("PORTKEY_MODEL") or os.getenv("PYDANTIC_AI_MODEL", "gpt-4o-mini")
    if os.getenv("PORTKEY_API_KEY"):
        client = AsyncOpenAI(
            api_key=os.environ["PORTKEY_API_KEY"],
            base_url="https://api.portkey.ai/v1",
            default_headers={"x-portkey-api-key": os.environ["PORTKEY_API_KEY"]},
            timeout=60.0,
            max_retries=0,
        )
        provider = OpenAIProvider(openai_client=client)
        return OpenAIChatModel(model_id.split(":", 1)[-1], provider=provider)
    return f"openai:{model_id}"


# --- Audit trail ------------------------------------------------------------


def new_run_id() -> str:
    """A fresh identifier shared by every audit entry from one `run_chat` call."""
    return str(uuid.uuid4())


def model_finish_reason(result: Any) -> str:
    """Pull the real finish_reason off the last model response in a PydanticAI
    run result (e.g. 'tool_call' for a structured-output response), instead of
    inventing one. Falls back to 'completed' if none is present."""
    for message in reversed(result.all_messages()):
        finish_reason = getattr(message, "finish_reason", None)
        if finish_reason:
            return str(finish_reason)
    return "completed"


def audit_entry(
    *,
    run_id: str,
    tool_name: str,
    tool_args: dict[str, Any],
    result_summary: str,
    stop_reason: str,
    duration_ms: float,
    error: str | None = None,
) -> AuditEntry:
    return AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        run_id=run_id,
        tool_name=tool_name,
        tool_args=tool_args,
        result_summary=result_summary,
        stop_reason=stop_reason,
        duration_ms=duration_ms,
        error=error,
    )


def append_audit_entries(entries: list[AuditEntry]) -> None:
    """Append entries to the audit trail JSON array, creating it if needed.

    JSON (unlike JSONL) isn't naturally appendable, so this reads the
    existing array, adds the new entries, and rewrites the file -- the
    trail still grows across every run of the agent (and across server
    restarts, since it's just a file), it just isn't a byte-level append.
    This file is never wiped/reset between runs.
    """
    if not entries:
        return
    existing: list[dict[str, Any]] = []
    if AUDIT_TRAIL_PATH.is_file():
        try:
            loaded = json.loads(AUDIT_TRAIL_PATH.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                existing = loaded
        except json.JSONDecodeError:
            existing = []
    existing.extend(entry.model_dump(mode="json") for entry in entries)
    AUDIT_TRAIL_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_TRAIL_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def _to_product_card(row: dict[str, Any]) -> ProductCard:
    return ProductCard(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=row["colors"],
        image_url=row["image_url"],
        price=row["price"],
        inventory=[InventorySize(**item) for item in row["inventory"]],
        total_stock=row["total_stock"],
        in_stock=row["in_stock"],
    )


def _tokens(*values: str | None) -> set[str]:
    text = " ".join(value for value in values if value)
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 1}


def _overlap(query_tokens: set[str], entry_tokens: set[str]) -> int:
    """Count query/entry token pairs that share a common stem, via substring
    containment rather than exact equality -- plain set intersection would
    miss e.g. query "hoodie" against a garment_type token "hooded", which are
    the same category in practice. Each side only counts once even if it
    matches multiple tokens on the other side, so one entry token can't
    inflate the score by matching several query tokens or vice versa."""
    matched_query: set[str] = set()
    matched_entry: set[str] = set()
    for q in query_tokens:
        if len(q) < 3:
            continue
        for e in entry_tokens:
            if len(e) < 3:
                continue
            if q in e or e in q:
                matched_query.add(q)
                matched_entry.add(e)
    return len(matched_query) + len(matched_entry)


def _score_product(query_tokens: set[str], row: dict[str, Any]) -> float:
    score = 0.0
    score += 3 * _overlap(query_tokens, _tokens(row["name"], row["garment_type"]))
    score += 2 * _overlap(query_tokens, _tokens(*row["colors"]))
    score += 1.5 * _overlap(query_tokens, _tokens(*row["search_tags"]))
    score += 1 * _overlap(query_tokens, _tokens(row["description"]))
    return score


def search_products(query: str, max_results: int = MAX_SEARCH_RESULTS) -> list[ProductCard]:
    """Search the catalogue for products matching a free-text query.

    Scores every product by token overlap with the query against its name,
    garment type, colors, search tags, and description, and returns the
    top matches. Returns an empty list if nothing scores above zero rather
    than guessing at unrelated products.
    """
    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    products = database.list_products()
    scored = [(product, _score_product(query_tokens, product)) for product in products]
    scored = [(product, score) for product, score in scored if score > 0]
    scored.sort(key=lambda pair: (-pair[1], pair[0]["name"]))

    limit = min(max_results, MAX_SEARCH_RESULTS)
    return [_to_product_card(product) for product, _ in scored[:limit]]


def get_product(product_id: str) -> ProductCard | None:
    """Look up one product by its exact catalogue product_id."""
    row = database.get_product(product_id)
    return _to_product_card(row) if row else None


def get_stock(product_id: str) -> StockInfo | None:
    """Get the full size-by-size stock breakdown for one product.

    Use this for "how many do you have" / "what sizes are in stock"
    questions about a whole product, as opposed to `check_size_availability`,
    which checks a single named size. Returns None if the product doesn't
    exist, rather than fabricating stock numbers.
    """
    row = database.get_product(product_id)
    if row is None:
        return None
    return StockInfo(
        product_id=row["product_id"],
        name=row["name"],
        inventory=[InventorySize(**item) for item in row["inventory"]],
        total_stock=row["total_stock"],
        in_stock=row["in_stock"],
    )


def check_size_availability(product_id: str, size: str) -> InventorySize | None:
    """Check stock for one specific size of one product.

    Returns None if the product or size doesn't exist, rather than
    fabricating a quantity.
    """
    row = database.get_product(product_id)
    if row is None:
        return None
    size_upper = size.strip().upper()
    for item in row["inventory"]:
        if item["size"].upper() == size_upper:
            return InventorySize(**item)
    return None
