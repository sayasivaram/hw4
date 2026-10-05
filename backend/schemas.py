"""Pydantic response models for the Campus Customs API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InventorySize(BaseModel):
    size: str
    quantity: int


class Product(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str] = Field(default_factory=list)
    search_tags: list[str] = Field(default_factory=list)
    image_url: str
    price: float
    inventory: list[InventorySize] = Field(default_factory=list)
    total_stock: int
    in_stock: bool


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthUser(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    email: str
    token: str = Field(
        description=(
            "Signed session token proving this is the logged-in user. Sent back on every "
            "subsequent request as an `Authorization: Bearer <token>` header -- never a bare "
            "user_id the client could swap out to act as someone else."
        )
    )


class ChatMessageIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    page_path: str | None = None


class ChatHistoryMessage(BaseModel):
    role: str
    content: str
    products: list[Product] = Field(default_factory=list)
    created_at: str
