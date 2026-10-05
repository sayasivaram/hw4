"""Pydantic/PydanticAI structured types for the Campus Customs agent.

Kept separate from schemas.py (which holds the plain REST request/response
models for the product/auth endpoints) so every type the *agent* produces or
consumes -- tool outputs, the final chat reply -- lives in one place, the
same convention Homework 3 used.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class InventorySize(BaseModel):
    size: str = Field(description="Size label, one of XS, S, M, L, XL, XXL.")
    quantity: int = Field(description="Units currently in stock for this size.")


class ProductCard(BaseModel):
    """One catalogue product, shaped for direct display on the website --
    the agent attaches these to a reply instead of just naming a product, so
    the frontend can render an image/price/stock card without a second
    lookup."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str] = Field(default_factory=list)
    image_url: str
    price: float
    inventory: list[InventorySize] = Field(default_factory=list)
    total_stock: int
    in_stock: bool


class StockInfo(BaseModel):
    """Stock-only lookup result for one product: every size's quantity, straight
    from the `inventory` table. Kept separate from `ProductCard` so a pure
    stock question doesn't need the model to also re-state the full product
    description/price -- just the numbers the user actually asked about."""

    product_id: str
    name: str = Field(description="Product name, so the reply can name what's in/out of stock.")
    inventory: list[InventorySize] = Field(
        description="Quantity for every size, XS through XXL, including sizes with 0 in stock."
    )
    total_stock: int = Field(description="Sum of quantity across all sizes.")
    in_stock: bool = Field(description="Whether at least one size has quantity > 0.")


class ChatReply(BaseModel):
    """The agent's structured output for one turn of conversation."""

    message: str = Field(
        description="The assistant's natural-language reply to show in the chat window."
    )
    products: list[ProductCard] = Field(
        default_factory=list,
        description=(
            "Product cards to display alongside the reply, e.g. search results or the specific "
            "product the user asked about. Empty if no product is relevant to this reply."
        ),
    )


class AuditEntry(BaseModel):
    """One record in the append-only audit trail (output/audit_trail.json).

    Captures one step of one agent run -- either a single tool call or the
    overall model turn -- so the full sequence of steps behind any chat
    reply can be reconstructed later. Every step belonging to the same
    top-level `run_chat` call shares the same `run_id`. Mirrors the audit
    design from Homework 3's agent.
    """

    timestamp: str = Field(description="UTC ISO-8601 timestamp of when this step completed.")
    run_id: str = Field(description="Identifier shared by every step belonging to the same chat turn.")
    tool_name: str = Field(
        description="Name of the tool/step this entry represents, e.g. 'search_products' or 'agent.run'."
    )
    tool_args: dict[str, Any] = Field(
        default_factory=dict,
        description="Small, serializable arguments passed into this step (e.g. a query string, a product_id).",
    )
    result_summary: str = Field(description="Short, human-readable summary of what this step returned.")
    stop_reason: str = Field(
        description=(
            "Why this step ended: the model's own finish_reason for an 'agent.run' step, "
            "'completed' for a tool call that returned normally, or 'error:<ExceptionType>' if it failed."
        )
    )
    duration_ms: float = Field(description="Wall-clock time this step took, in milliseconds.")
    error: str | None = Field(default=None, description="Error message if this step failed, else null.")
