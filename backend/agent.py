"""Campus Customs agent -- PydanticAI wiring.

Builds the Agent (model, system prompt, tools, structured output type) and
exposes `run_chat`, the one entry point `main.py`'s /api/chat route calls.

Two kinds of memory/context feed into every run:
- Customer identity (name/email) and recent conversation history, scoped to
  logged-in users only, read from and written back to `chat_messages`
  (database.py) -- so the agent remembers earlier turns and who it's
  talking to across requests. Guests get neither.
- "Page context": a short, code-generated description of what the shopper
  is currently looking at on the website (e.g. a specific product page),
  built from the page path the frontend sends, not inferred by the model.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, RunContext
from pydantic_ai.exceptions import ModelHTTPError, UnexpectedModelBehavior

import database
import tools
from models import ChatReply

ROOT = Path(__file__).resolve().parent
SYSTEM_PROMPT = (ROOT / "prompts" / "prompt.md").read_text(encoding="utf-8")

HISTORY_TURNS = 10


@dataclass
class CustomerContext:
    """Agent dependencies for one chat turn -- everything the agent should
    know about who it's talking to and what they're looking at, assembled by
    `run_chat` (never by the model itself) before each run."""

    run_id: str
    user_id: int | None
    first_name: str | None
    last_name: str | None
    email: str | None
    page_description: str | None


agent = Agent(
    tools.model_for_agent(),
    deps_type=CustomerContext,
    output_type=ChatReply,
    retries=2,
)


@agent.system_prompt
def base_prompt() -> str:
    return SYSTEM_PROMPT


@agent.system_prompt
def customer_identity(ctx: RunContext[CustomerContext]) -> str:
    deps = ctx.deps
    if deps.user_id is None:
        return (
            "This shopper is browsing as a guest -- they are not logged in, you have no name or "
            "email on file for them, and there is no saved conversation history with them before "
            "this message."
        )
    full_name = " ".join(part for part in (deps.first_name, deps.last_name) if part) or None
    return (
        f"The logged-in customer's name is {full_name or 'unknown'} and their account email is "
        f"{deps.email}. You may greet them by name and refer to earlier messages in this "
        "conversation (shown below) as things they already told you. Never read their email back "
        "to them unless they specifically ask for it, and never discuss any other customer's "
        "account or data."
    )


@agent.system_prompt
def page_context(ctx: RunContext[CustomerContext]) -> str:
    if not ctx.deps.page_description:
        return "The shopper's current page on the website is unknown."
    return f"What the shopper is currently looking at on the website: {ctx.deps.page_description}"


def _audit_tool_call(ctx: RunContext[CustomerContext], tool_name: str, tool_args: dict, fn) -> object:
    """Run one tool function and append an audit_trail.json entry for it --
    shared by every tool below so each one is logged the same way, with
    args, a short result summary, timing, and the outcome (success or
    error) of this single step in the agent's loop."""
    start = time.monotonic()
    try:
        result = fn()
    except Exception as exc:  # noqa: BLE001 -- log the failure, then still raise it
        tools.append_audit_entries([tools.audit_entry(
            run_id=ctx.deps.run_id,
            tool_name=tool_name,
            tool_args=tool_args,
            result_summary="failed",
            stop_reason=f"error:{type(exc).__name__}",
            duration_ms=(time.monotonic() - start) * 1000,
            error=str(exc),
        )])
        raise

    if isinstance(result, list):
        summary = f"{len(result)} result(s)"
    elif result is None:
        summary = "not found"
    else:
        summary = "found"

    tools.append_audit_entries([tools.audit_entry(
        run_id=ctx.deps.run_id,
        tool_name=tool_name,
        tool_args=tool_args,
        result_summary=summary,
        stop_reason="completed",
        duration_ms=(time.monotonic() - start) * 1000,
    )])
    return result


@agent.tool
def search_products(ctx: RunContext[CustomerContext], query: str, max_results: int = tools.MAX_SEARCH_RESULTS) -> list[dict]:
    """Search the Campus Customs catalogue for products matching a free-text query
    (e.g. a garment type, color, Yale college/team, or general description).

    Leave max_results at its default to get every real match -- the website
    displays this entire list as product cards, so don't lower it just to
    keep the chat reply short; shorten the reply text instead."""
    cards = _audit_tool_call(
        ctx,
        "search_products",
        {"query": query, "max_results": max_results},
        lambda: tools.search_products(query, max_results=max_results),
    )
    return [card.model_dump() for card in cards]


@agent.tool
def get_product(ctx: RunContext[CustomerContext], product_id: str) -> dict | None:
    """Get full details for one product by its exact product_id."""
    card = _audit_tool_call(
        ctx, "get_product", {"product_id": product_id}, lambda: tools.get_product(product_id)
    )
    return card.model_dump() if card else None


@agent.tool
def get_stock(ctx: RunContext[CustomerContext], product_id: str) -> dict | None:
    """Get the full size-by-size stock breakdown for one product (all six sizes)."""
    result = _audit_tool_call(
        ctx, "get_stock", {"product_id": product_id}, lambda: tools.get_stock(product_id)
    )
    return result.model_dump() if result else None


@agent.tool
def check_size_availability(ctx: RunContext[CustomerContext], product_id: str, size: str) -> dict | None:
    """Check how many units of one specific size are in stock for one product."""
    result = _audit_tool_call(
        ctx,
        "check_size_availability",
        {"product_id": product_id, "size": size},
        lambda: tools.check_size_availability(product_id, size),
    )
    return result.model_dump() if result else None


def _format_history(history: list[dict]) -> str:
    lines = [f"{item['role']}: {item['content']}" for item in history]
    return "\n".join(lines)


def describe_page(page_path: str | None) -> str | None:
    """Turn a frontend route into a plain-language sentence the agent can use
    as context -- built entirely in code from real data (never left for the
    model to infer from the raw path), so a follow-up like "is this in
    stock?" on a product page resolves to the actual product being viewed.
    """
    if not page_path:
        return None
    path = page_path.split("?")[0].rstrip("/")

    if path.startswith("/products/"):
        product_id = path.removeprefix("/products/")
        product = database.get_product(product_id)
        if product is None:
            return f"A product detail page for an unrecognized product_id ({product_id})."
        return (
            f"The product detail page for \"{product['name']}\" (product_id={product_id}), "
            f"a {product['garment_type']} priced at ${product['price']:.2f}, "
            f"{'in stock' if product['in_stock'] else 'currently out of stock in every size'}."
        )
    if path in ("", "/"):
        return "The home page."
    if path == "/products":
        return "The full product catalogue page (no specific product selected)."
    if path == "/about":
        return "The About Us page."
    if path in ("/login", "/create-account"):
        return "An account page (login or create account), not a product page."
    return f"Page path {path}."


async def run_chat(message: str, user_id: int | None = None, page_path: str | None = None) -> ChatReply:
    run_id = tools.new_run_id()
    history: list[dict] = []
    deps = CustomerContext(
        run_id=run_id,
        user_id=user_id,
        first_name=None,
        last_name=None,
        email=None,
        page_description=describe_page(page_path),
    )

    if user_id is not None:
        user_row = database.get_user_by_id(user_id)
        if user_row is not None:
            deps.first_name = user_row["first_name"]
            deps.last_name = user_row["last_name"]
            deps.email = user_row["email"]
        history = database.get_chat_history(user_id, limit=HISTORY_TURNS)

    if history:
        prompt = (
            "Conversation so far with this same customer:\n"
            f"{_format_history(history)}\n\n"
            f"New message from the customer: {message}"
        )
    else:
        prompt = message

    start = time.monotonic()
    try:
        result = await agent.run(prompt, deps=deps)
        reply = result.output
    except (ModelHTTPError, UnexpectedModelBehavior) as exc:
        # Covers both the model gateway's own content filter rejecting a
        # message outright (e.g. a prompt-injection attempt) and the model
        # failing to produce valid structured output -- either way, fail
        # safely with an on-brand decline instead of a raw 500.
        tools.append_audit_entries([tools.audit_entry(
            run_id=run_id,
            tool_name="agent.run",
            tool_args={"message": message[:200], "user_id": user_id},
            result_summary="failed -- fell back to a safe decline reply",
            stop_reason=f"error:{type(exc).__name__}",
            duration_ms=(time.monotonic() - start) * 1000,
            error=str(exc),
        )])
        reply = ChatReply(
            message=(
                "I can't help with that request. I'm the Campus Customs shopping assistant -- "
                "ask me about our Yale apparel, sizes, or colors and I'm happy to help."
            ),
            products=[],
        )
    else:
        tools.append_audit_entries([tools.audit_entry(
            run_id=run_id,
            tool_name="agent.run",
            tool_args={"message": message[:200], "user_id": user_id},
            result_summary=f"reply={reply.message[:120]!r}, products_attached={len(reply.products)}",
            stop_reason=tools.model_finish_reason(result),
            duration_ms=(time.monotonic() - start) * 1000,
        )])

    if user_id is not None:
        database.add_chat_message(user_id=user_id, role="user", content=message)
        products_json = (
            json.dumps([p.model_dump(mode="json") for p in reply.products]) if reply.products else None
        )
        database.add_chat_message(
            user_id=user_id, role="assistant", content=reply.message, products_json=products_json
        )

    return reply
