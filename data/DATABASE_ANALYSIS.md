# `data/campus_customs.db` — Schema Analysis

SQLite database, 168 KB, 4 tables: `catalogue`, `inventory`, `users`, `chat_messages`.

---

## 1. `catalogue` — 102 rows (1 per product)

```sql
CREATE TABLE catalogue (
    product_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    garment_type TEXT NOT NULL,
    description TEXT NOT NULL,
    colors TEXT NOT NULL,          -- JSON array, stored as text
    search_tags TEXT NOT NULL,     -- JSON array, stored as text
    image_file_path TEXT NOT NULL,
    price REAL NOT NULL
);
```

| Field | Notes |
|---|---|
| `product_id` | Slug derived from the image filename (e.g. `baseball-left-chest-crewneck`). No separate numeric ID — this slug *is* the primary key, and is what `inventory.product_id` and `chat_messages.products_json` reference. Looks hand/AI-generated from Homework 3's `build_catalogue.py`, not DB-generated. |
| `name` | Human-readable title, basically Title-Case of the slug (e.g. "Baseball Left Chest Crewneck"). Not always grammatically ideal ("2025 Yale Vs Harvard T Shirt") — fine for display, not worth re-deriving. |
| `garment_type` | Free text, **not normalized** — 21 distinct values for 102 products, with near-duplicates like `"hoodie"` vs `"pullover hoodie"` vs `"hooded sweatshirt"` vs `"full-zip hooded sweatshirt"`, and `"short-sleeve t-shirt"` vs `"short-sleeve T-shirt"` (casing difference, same meaning — 16 vs 6 rows). **Important:** any "filter by category" UI should bucket/normalize these rather than using `garment_type` as a clean enum. |
| `description` | 1–3 sentence natural-language description, good for display and for the chatbot's context — written with enough visual detail (color, graphic placement, text) to double as search content. |
| `colors` | JSON array **stored as a TEXT string**, e.g. `'["navy blue", "white"]'` — must `json.loads()` in Python (or `json_each`/`json_extract` in SQL) before using. 2 products have an empty array `[]`. Not a controlled vocabulary (`"navy"` vs `"navy blue"` both appear). |
| `search_tags` | Same JSON-as-text pattern as `colors`. 5–10 free-text tags per product (brand, affiliation, style, "Campus Customs"). Good raw material for a search/recommendation tool but needs tokenizing, not exact-match. |
| `image_file_path` | Relative path like `products/baseball-left-chest-crewneck.jpg`, relative to `data/`. **Verified: all 102 referenced files exist in `data/products/`,** and the two counts match exactly (102 catalogue rows, 102 image files) — no orphans either direction. |
| `price` | Plain float, USD, no currency field. Range **$32.00–$98.00**, mean **$58.48**. |

---

## 2. `inventory` — 612 rows (6 per product, 102 × 6)

```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    size TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES catalogue(product_id),
    UNIQUE (product_id, size)
);
```

- **Every product has exactly 6 size rows**, always `XS, S, M, L, XL, XXL` — confirmed uniform across all 102 products (no product has a subset of sizes).
- `quantity` ranges **0–25**, average **~9.7**. **145 of 612 rows (≈24%) are out of stock (quantity = 0)** — a real, common case any UI/agent needs to handle (disable size, "out of stock" badge, "this size isn't available right now" in chat), not an edge case to ignore.
- `(product_id, size)` is unique, so this is a clean one-row-per-size-variant model — no separate SKU table, `size` itself is the variant key.
- No `updated_at`/timestamp on inventory, so there's no built-in way to track stock changes over time if that's ever needed later.

---

## 3. `users` — 3 rows (seed/test data)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    first_name TEXT,
    last_name TEXT
);
```

- `password_hash` is already `pbkdf2_sha256$...` formatted (Django-style: `pbkdf2_sha256$<iterations>$<salt>$<hash>`) — **real hashed passwords, not plaintext**, so an auth backend needs a PBKDF2-SHA256 verifier compatible with that format (e.g. `django.contrib.auth.hashers` logic, or `passlib`'s `pbkdf2_sha256` handler), not a bcrypt/argon2 assumption.
- `name` duplicates `first_name`/`last_name` (added later via `ALTER TABLE`, per the trailing columns in the schema) — e.g. row 2 has `name="Ada Lovelace"`, `first_name="Ada"`, `last_name="Lovelace"`. Treat `first_name`/`last_name` as canonical for display, `name` as a legacy/combined field.
- Only 3 seed users exist (`Test User`, `Ada Lovelace`, `Tauhid Zaman`), all `@yale.edu`/`@campuscustoms.yale.edu` addresses — this is clearly seed data for development, not a real user base. Any signup flow needs to actually `INSERT` into this table.

---

## 4. `chat_messages` — 22 rows (pre-existing conversation history)

```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,              -- 'user' | 'assistant'
    content TEXT NOT NULL,
    products_json TEXT,              -- JSON array, nullable
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

- This table already has **real sample conversations** (all under `user_id = 1`), which is the single most useful artifact in the database for scoping the chatbot — it shows what a working version of this exact assignment looked like:
  - `"What hoodies do you have?"` → assistant lists matching hoodies, with a `products_json` payload attached.
  - `"you have this in pink?"` → assistant answers about color availability for a specific product.
  - `"Hi — do you remember me? What's my name?"` → tests conversation memory tied to the logged-in user.
- `products_json` (11 of 22 rows have it) is **not just a list of `product_id`s** — it's a fully denormalized product payload per message, e.g.:
  ```json
  {
    "product_id": "basic-hoodie-big-yale",
    "name": "Basic Hoodie Big Yale",
    "garment_type": "pullover hoodie",
    "description": "...",
    "colors": [...], "search_tags": [...],
    "image_file_path": "products/basic-hoodie-big-yale.jpg",
    "image_url": "/media/products/basic-hoodie-big-yale.jpg",
    "price": 68.0,
    "inventory": [{"size": "XS", "quantity": 15}, ...],
    "total_stock": 60
  }
  ```
  This is a strong signal for how the FastAPI backend should shape a "product card" response to the frontend: catalogue fields + `image_url` (web-servable path, distinct from the DB's relative `image_file_path`) + per-size `inventory` + a rolled-up `total_stock`. Worth reusing this shape directly for both the product API and the chatbot's structured tool output.
- `role` is a simple two-value string, not a DB-level enum/CHECK constraint — validate it in the Pydantic layer instead of relying on SQLite to reject bad values.

---

## Key things to design around

1. **JSON-in-TEXT columns** (`colors`, `search_tags` in `catalogue`; `products_json` in `chat_messages`) — always `json.loads`/`json.dumps` at the Python boundary; don't treat them as queryable SQL columns without `json_extract`.
2. **`garment_type` is messy free text** — build a small normalization/grouping step (e.g. map to `hoodie`, `crewneck`, `t-shirt`, `1/4 zip`, `fleece jacket`, `jacket`) before using it to drive category filters/nav.
3. **Out-of-stock is common (24% of size rows)** — the UI and agent must represent "0 available" explicitly, not just omit it.
4. **`image_file_path` is a relative disk path (`products/...`), not a URL** — the FastAPI backend needs to serve `data/products/` as static files and expose a web path (the existing chat history already names this convention: `image_url: "/media/products/<file>"`).
5. **Passwords are PBKDF2-SHA256 hashes** — any login endpoint must verify against that exact hash format, not assume a different hashing library's default.
6. **`chat_messages` already encodes the intended conversational behaviors** to support: product search/listing, attribute questions (color availability), and session/user memory ("do you remember me"). These make a good basis for the chatbot's scope and a few ready-made test cases.
