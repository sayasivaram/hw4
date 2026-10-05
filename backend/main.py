"""Campus Customs API -- FastAPI app.

Product catalogue endpoints, product images served as static files, auth,
and a chat endpoint backed by the PydanticAI agent in agent.py. Run with:

    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import auth
import database
import ratelimit
from agent import run_chat
from models import ChatReply
from schemas import AuthUser, ChatHistoryMessage, ChatMessageIn, LoginRequest, Product, SignupRequest

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=str(database.ROOT / "data")), name="media")


def get_current_user_id(authorization: str | None = Header(default=None)) -> int | None:
    """Resolve the logged-in user from a signed session token, never from a
    client-supplied id -- so a request can't claim to be a different
    customer just by stating their id. Returns None (treated as a guest) for
    a missing, malformed, or expired token rather than raising, since an
    expired session should fall back to guest behavior, not break the chat.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    return auth.verify_session_token(token)


@app.get("/api/products", response_model=list[Product])
def get_products() -> list[dict]:
    return database.list_products()


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str) -> dict:
    product = database.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
    return product


def _to_auth_user(row) -> AuthUser:
    return AuthUser(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
        token=auth.create_session_token(row["id"]),
    )


@app.post("/api/auth/signup", response_model=AuthUser, status_code=201)
def signup(payload: SignupRequest) -> AuthUser:
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if database.get_user_by_email(payload.email) is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    password_hash = auth.hash_password(payload.password)
    row = database.create_user(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password_hash=password_hash,
    )
    return _to_auth_user(row)


@app.post("/api/auth/login", response_model=AuthUser)
def login(payload: LoginRequest) -> AuthUser:
    row = database.get_user_by_email(payload.email)
    if row is None or not auth.verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _to_auth_user(row)


@app.post("/api/chat", response_model=ChatReply)
async def post_chat(
    payload: ChatMessageIn,
    request: Request,
    authorization: str | None = Header(default=None),
) -> ChatReply:
    user_id = get_current_user_id(authorization)
    rate_limit_key = f"user:{user_id}" if user_id is not None else f"ip:{request.client.host}"
    if not ratelimit.check_rate_limit(rate_limit_key):
        raise HTTPException(
            status_code=429,
            detail=f"Too many messages -- please wait a moment before sending another "
            f"(limit: {ratelimit.MAX_REQUESTS_PER_WINDOW} per {ratelimit.WINDOW_SECONDS}s).",
        )
    return await run_chat(payload.message, user_id=user_id, page_path=payload.page_path)


@app.get("/api/chat/history/{user_id}", response_model=list[ChatHistoryMessage])
def get_chat_history(user_id: int, authorization: str | None = Header(default=None)) -> list[dict]:
    current_user_id = get_current_user_id(authorization)
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only view your own chat history")
    return database.get_chat_history(user_id)
