# Campus Customs — Homework 4

A website and chatbot for Campus Customs (Yale's licensed apparel shop), built as a React + Vite + TypeScript frontend and a Python FastAPI backend with a PydanticAI shopping-assistant agent.

See [`AI_prompts.md`](AI_prompts.md) for the full prompt log, and [`output/harness.md`](output/harness.md) for a complete technical write-up of how the system works (models, tools, safety rules, specs).

## 1. Get the data pack

This repo does **not** include the product catalogue database or product photos (see `.gitignore`) -- they're provided separately as a data pack. Before running anything, place the data pack's contents here so the layout looks like:

```
data/
├── campus_customs.db
└── products/
    ├── some-product.jpg
    └── ... (102 product photos)
```

## 2. Set up environment variables

Copy the example file and fill in real values:

```bash
cp .env.example .env
```

Edit `.env` and set `PORTKEY_API_KEY` and `PORTKEY_MODEL` (or `OPENAI_API_KEY` if not using Portkey -- see `backend/tools.py`'s `model_for_agent()` for the fallback behavior).

## 3. Run the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000` (product/catalogue endpoints, auth, and the `/api/chat` agent endpoint). On first run, the backend also generates `backend/.session_secret` (git-ignored) used to sign login session tokens -- this is created automatically, no setup needed.

## 4. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The site will be available at `http://localhost:5173`. It expects the backend running at `http://127.0.0.1:8000` (see `frontend/src/api/client.ts`).

## 5. Try it out

- Browse the catalogue at `/products`, or ask the chat widget (bottom-right) something like "what hoodies do you have?"
- Log in with the seeded test account: **test@campuscustoms.yale.edu** / **password** (or create a new account) to see personalized greetings and persistent chat history.

## Project layout

```
.
├── AI_prompts.md         # Full prompt log for this homework
├── requirements.txt      # Backend (Python) dependencies
├── .env.example          # Copy to .env and fill in real keys
├── frontend/             # React + Vite + TypeScript app
├── backend/
│   ├── main.py           # FastAPI app -- run with: uvicorn main:app --reload --port 8000
│   ├── agent.py           # PydanticAI agent wiring (tools, system prompt, memory)
│   ├── models.py          # Pydantic/PydanticAI structured types
│   ├── tools.py           # Agent tool functions + audit-trail helpers
│   ├── database.py        # SQLite access helpers
│   ├── schemas.py         # REST request/response models (auth, chat)
│   ├── auth.py             # Password hashing + session tokens
│   ├── ratelimit.py        # Simple per-identity rate limiter
│   └── prompts/prompt.md  # Agent system prompt (voice + safety guidelines)
└── output/
    ├── harness.md          # Full technical write-up -- start here
    ├── design.md           # Visual design write-up (Problem 10)
    ├── usability.md        # Usability improvements write-up (Problem 9)
    ├── app_check.html      # Live test results with screenshots (Problem 11)
    ├── app_check_images/   # Screenshots linked from app_check.html
    └── audit_trail.json    # Append-only log of every agent tool call
```
