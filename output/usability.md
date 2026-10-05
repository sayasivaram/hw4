# Usability Improvements (Problem 9)

Four of the ten improvements identified were implemented this round -- the top two ranked frontend and top two ranked backend items. Each was verified live in the running app (screenshots/interaction notes below), not just by reading the code.

---

## Frontend

### 1. Auto-scroll the chat panel to the latest message

**What changed:** `ChatWidget.tsx` now scrolls its message list to the bottom whenever a new message arrives or the panel is opened (`frontend/src/components/ChatWidget.tsx`).

**The problem it fixes:** The chat panel has a fixed height. Before this change, a reply that pushed the conversation past that height just sat below the visible area -- the shopper had to notice nothing happened and manually scroll down to see the assistant's answer. This hit *every single exchange* once a conversation ran more than 2-3 messages, making it the highest-frequency papercut in the whole app.

**Why it's beneficial:**
- *User:* They see the answer to the question they just asked without extra effort -- the chat behaves like every other chat UI they're used to (iMessage, Slack, etc.).
- *Business:* A shopper who thinks the assistant "isn't responding" because the reply is scrolled out of view is a shopper who closes the widget and leaves -- directly costing the business the sale-assist value the chatbot exists to provide.

**Verified live:** Logged in as the test user, opened the chat (which reloaded prior history already scrolled to the bottom), sent a new message, and watched the panel stay pinned to the newest message through the "..." pending state and the final reply -- see the three chronological screenshots taken during this session.

### 2. Mobile navigation (hamburger menu)

**What changed:** `NavBar.tsx`/`NavBar.css` now hide the desktop nav links and auth buttons below 820px and show a hamburger toggle instead, which opens a full-width mobile menu with the same links, greeting, and Log In/Create Account/Log Out actions.

**The problem it fixes:** The previous CSS (`@media (max-width: 820px) { .navbar-links { display: none; } }`) hid the nav links on any phone-sized screen with **no replacement** -- there was no way to reach Products, About Us, or Login/Create Account from a phone at all except the browser's own back/forward buttons.

**Why it's beneficial:**
- *User:* A shopper on a phone -- very plausibly the majority of traffic for a campus apparel site -- can actually navigate the site instead of being stuck on whatever page they landed on.
- *Business:* This was a hard dead-end, not a rough edge: a mobile visitor literally could not reach the product catalogue through the nav. Fixing it recovers mobile conversions that the site was actively losing.

**Verified live:** Resized the preview to a 375×812 mobile viewport, confirmed the desktop links/buttons disappeared and the hamburger icon appeared, clicked it, and confirmed the mobile menu opened with all links, a divider, and the auth buttons (screenshots above).

---

## Backend

### 1. Real server-side sessions (signed tokens, not a client-stated user_id)

**What changed:** `POST /api/auth/login` and `POST /api/auth/signup` now return a signed, expiring session token (`auth.create_session_token`, HMAC-SHA256 over a `{uid, exp}` payload, secret persisted to a git-ignored local file so it survives `--reload` restarts). Every request that needs to know who's logged in (`POST /api/chat`, `GET /api/chat/history/{user_id}`) now derives the user id from a verified `Authorization: Bearer <token>` header (`get_current_user_id` in `main.py`) instead of trusting a `user_id` value the client simply included in the request body or path.

**The problem it fixes:** Through the end of Problem 8, every endpoint that needed to know "who is this" took a bare `user_id` on faith from the request itself. Nothing stopped a request from claiming to be any other customer -- `GET /api/chat/history/2` with no proof of being user 2 would have happily returned user 2's saved conversation, and the chat endpoint would have let the agent greet you by someone else's name and pull their chat history into context. This is the one item across all 10 identified improvements that was a real impersonation/privacy gap, not just friction.

**Why it's beneficial:**
- *User:* Their saved conversation (which can include their name, and whatever they've told the assistant) is only ever visible to them, not to anyone who happens to know or guess their numeric id.
- *Business:* Closes a real customer-data exposure before this app handles any more real accounts -- the kind of issue that's cheap to fix now and expensive (trust, reputation, compliance) to fix after an incident.

**Verified live:** Logged in via the actual UI (test user), confirmed `main.py` only resolves identity from a verified token; via curl, confirmed a correct token can read its own history (200), the identical token is rejected for a *different* user's history (403), no token at all is also rejected (403), and a garbage/tampered token degrades gracefully to guest behavior on `/api/chat` rather than erroring.

### 2. Input validation and per-identity rate limiting on `/api/chat`

**What changed:** `ChatMessageIn.message` now has `min_length=1, max_length=2000` (`schemas.py`), so FastAPI/Pydantic rejects an empty or absurdly long message with a 422 before it ever reaches the agent. A new minimal sliding-window limiter (`ratelimit.py`) caps each identity (`user:<id>` for a logged-in customer, `ip:<address>` for a guest) at 20 requests per 60 seconds, returning 429 with a clear message over the limit. The frontend's error handling was also updated to surface the real error text (e.g. the 429's message) in the chat bubble instead of a generic "couldn't reach the server," so these new backend guardrails are actually visible to the user, not just enforced silently.

**The problem it fixes:** There was previously no limit on message size and no throttling at all -- a single pasted wall of text, a buggy client loop, or a deliberate abuse attempt could run an unbounded number of calls against the paid model gateway with zero guardrail.

**Why it's beneficial:**
- *User:* Gets a clear, immediate "please slow down" message instead of the assistant silently failing or lagging if something (their own mistake or someone else's abuse) is hammering the endpoint.
- *Business:* Directly controls real, per-call cost against the model gateway -- this is the one item in the whole list with a dollar figure attached if left unfixed.

**Verified live:** Confirmed a too-long message (2001 characters) returns HTTP 422 with `ctx.max_length: 2000`, an empty message returns 422 with `string_too_short`, and a focused unit check of the limiter itself confirms exactly 20 of 25 rapid calls are allowed within the window, matching `MAX_REQUESTS_PER_WINDOW`.
