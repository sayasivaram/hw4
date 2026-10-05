"""SQLite access helpers for the Campus Customs database.

Kept separate from main.py so the route handlers stay thin, and so a later
PydanticAI agent (Problem 4+) can import the same read helpers instead of
re-querying the database its own way.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "campus_customs.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _parse_json_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return value if isinstance(value, list) else []


def _image_url(image_file_path: str) -> str:
    # catalogue stores paths like "products/foo.jpg", relative to data/.
    return f"/media/{image_file_path}"


def _row_to_product(row: sqlite3.Row, inventory: list[dict[str, Any]]) -> dict[str, Any]:
    total_stock = sum(item["quantity"] for item in inventory)
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": _parse_json_list(row["colors"]),
        "search_tags": _parse_json_list(row["search_tags"]),
        "image_url": _image_url(row["image_file_path"]),
        "price": row["price"],
        "inventory": inventory,
        "total_stock": total_stock,
        "in_stock": total_stock > 0,
    }


def list_products() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        catalogue_rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        inventory_rows = conn.execute("SELECT product_id, size, quantity FROM inventory").fetchall()
    finally:
        conn.close()

    inventory_by_product: dict[str, list[dict[str, Any]]] = {}
    for inv_row in inventory_rows:
        inventory_by_product.setdefault(inv_row["product_id"], []).append(
            {"size": inv_row["size"], "quantity": inv_row["quantity"]}
        )

    return [
        _row_to_product(row, inventory_by_product.get(row["product_id"], []))
        for row in catalogue_rows
    ]


def add_chat_message(
    *, user_id: int, role: str, content: str, products_json: str | None = None
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, products_json),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()


def _normalize_product_dict(product: dict[str, Any]) -> dict[str, Any]:
    """Fill in fields missing from older `products_json` payloads (e.g. the
    pre-existing seed rows in `chat_messages`, recorded before `in_stock`/
    `search_tags` were added to the product shape), so old history loads
    cleanly instead of failing response validation."""
    product.setdefault("search_tags", [])
    if "in_stock" not in product:
        if "total_stock" in product:
            product["in_stock"] = product["total_stock"] > 0
        else:
            product["in_stock"] = any(item["quantity"] > 0 for item in product.get("inventory", []))
    return product


def get_chat_history(user_id: int, limit: int = 50) -> list[dict[str, Any]]:
    """Full stored transcript for one user, oldest first, with each message's
    attached product cards parsed back out of `products_json` -- used both to
    reload the chat widget when a logged-in customer returns, and (in a
    shorter slice) to give the agent recent context."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT role, content, products_json, created_at FROM chat_messages "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    finally:
        conn.close()

    history = []
    for row in reversed(rows):
        raw_products = json.loads(row["products_json"]) if row["products_json"] else []
        products = [_normalize_product_dict(p) for p in raw_products]
        history.append(
            {
                "role": row["role"],
                "content": row["content"],
                "products": products,
                "created_at": row["created_at"],
            }
        )
    return history


def get_user_by_email(email: str) -> sqlite3.Row | None:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    finally:
        conn.close()


def create_user(*, first_name: str, last_name: str, email: str, password_hash: str) -> sqlite3.Row:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) "
            "VALUES (?, ?, ?, ?, ?)",
            (f"{first_name} {last_name}", email, password_hash, first_name, last_name),
        )
        conn.commit()
        return conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    finally:
        conn.close()


def get_product(product_id: str) -> dict[str, Any] | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return None
        inventory_rows = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY "
            "CASE size WHEN 'XS' THEN 0 WHEN 'S' THEN 1 WHEN 'M' THEN 2 "
            "WHEN 'L' THEN 3 WHEN 'XL' THEN 4 WHEN 'XXL' THEN 5 ELSE 6 END",
            (product_id,),
        ).fetchall()
    finally:
        conn.close()

    inventory = [{"size": r["size"], "quantity": r["quantity"]} for r in inventory_rows]
    return _row_to_product(row, inventory)
