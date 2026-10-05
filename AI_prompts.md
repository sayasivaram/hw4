# AI Prompts Log — Homework 4

This file records the prompts used with Claude for each problem in Homework 4, including any follow-up prompts and why they were needed.

---

## Problem 0: Setup

**Name/Title:** Connect GitHub, then scope the Homework 4 project

**Prompt:**
> Please help me set up my github using these general guides. I do not want you to know what my github login is, but I want to be able to grant you access to push things to my github repo.
>
> *(pasted GitHub/Git setup guide: create a GitHub account, install Git, verify with `git --version`, then connect the vibe coder to GitHub by setting global `user.name`/`user.email` and signing in.)*

> I now want to work on Homework 4 for my AI Foundations class. Use the AI foundations folder -> Homework 4 subfolder for all files associated with this homework. The goal of this homework is to build a website and chatbot for Campus Customs (from Homework 3) using a React + Vite TypeScript front end and a Python FastAPI backend with a PydanticAI agent. In the Homework 4 folder is a data folder that should include campus_customs.db with the product catalogue, inventory by size, users, product image file paths. Use yalebulldogblue.com as a style guide. The data folder should contain data/campus_customs.db and data/products/

> We're going to do this step by step

**Follow-up prompts:**
_None — Git was already installed; set global `user.name`/`user.email`, installed GitHub CLI (`gh`) via its official `.pkg` installer (Homebrew wasn't available on this Intel Mac and its install script errored), and completed `gh auth login` via the browser device-login flow, which the user completed themselves. Confirmed with `gh auth status`. For the Homework 4 scoping message, an initial attempt to ask clarifying questions (auth scope, chatbot scope, cart/checkout) was dismissed by the user in favor of working step by step instead._

**Why an additional prompt was needed:**
_N/A for the GitHub setup — no follow-up was needed beyond the user completing the one browser sign-in step themselves, as the guide called for. For the Homework 4 scoping message, no further prompt was needed either; the user redirected to a step-by-step approach rather than answering the scoping questions up front._

---

## Problem 1: Vibe Coder Prompts

**Name/Title:** Set up the AI prompt log

**Prompt:**
> Make AI_prompts.md using a similar structure to Homework 3. It should be a log of my prompts - include the previous prompts as part of Problem 0: Setup. This prompt should be in Problem 1: Vibe coder prompts. For each section, make sure you update it with the problem number and title I give you, the prompts, and any follow up prompts (with what was lacking or needed clarification)

**Follow-up prompts:**
_None yet._

**Why an additional prompt was needed:**
_N/A — the initial prompt was sufficient to create the log file and backfill Problem 0 from the prior conversation._

---

## Problem 2: Analyze the database

**Name/Title:** Write up the schema and key fields in `data/campus_customs.db`

**Prompt:**
> Problem 2: Analyze the database. In data/campus_customs.db, there are a few fields to understand. Please analyze those fields (including, but not limited to, catalogue, inventory, and users). Please create a write up for me on these fields, how they are structured, and any other key info I may need

**Follow-up prompts:**
_Inspected the schema and data directly with `sqlite3` (row counts, sample rows, distinct values, min/max/avg stats, orphan/integrity checks against `data/products/`), and wrote the findings to `data/DATABASE_ANALYSIS.md`, including the pre-existing `chat_messages` rows that already demonstrate the intended chatbot behavior and product-card JSON shape._
>
> Create output/harness.md that has each table, the fields, why each field matters for the website we will build or the chatbot (in one line)

**Why an additional prompt was needed:**
_The follow-up wasn't a correction — it asked for a second, differently-structured deliverable (a one-line-per-field rationale table in `output/harness.md`) building on the same analysis, not a fix to the first write-up._

---

## Problem 3: Build the Campus Customs Website

**Name/Title:** React + Vite + TypeScript frontend, FastAPI products/images backend, stubbed chat

**Prompt:**
> Now we'll do problem 3: Build the Campus Customs Website. We need to begin creating a react + vite+ typescript front end for campus customs. On the main landing page, create a navigation bar at the top that shortcuts to the following pages: home, products, about us, log in, create account. Make sure to use the style and language from the website I cited as a style guide, but do not copy the language exactly. The products page should have all of the images from the catalogue with a basic description that offers key information on the product. When you click on the product card, it should open a single item page that has a large image and a full size description that is more detailed and thorough. We need to create the chat interface which should sit at the bottom right as a floating panel (don't create actual agent yet, just a stub that will call to backend). Start a simple FastAPI app in backend/main.py for products and images - we can grow it into the agent during a later problem

**Follow-up prompts:**
_None — scaffolded `frontend/` (Vite React-TS + react-router-dom) and `backend/` (FastAPI, Python venv). Fetched yalebulldogblue.com for its style (Yale Blue, gold/red accents, serif headings, collegiate-but-polished tone) and wrote original copy rather than reusing its phrasing. Built `backend/database.py` + `schemas.py` + `main.py` (GET /api/products, GET /api/products/{id}, static `/media` mount for `data/products/`, stubbed POST /api/chat), verified all three against the live DB with curl. Built the frontend: NavBar (Home/Products/About Us/Log In/Create Account), Products grid (search filter), ProductDetail (large image, full description, color chips, per-size stock with out-of-stock handling), About, Login/Create Account forms (UI-only, no backend auth yet), and a floating bottom-right ChatWidget that calls the stub endpoint. Verified with `tsc --noEmit` and by running both dev servers and confirming clean Vite transforms with no console/compile errors._

**Why an additional prompt was needed:**
_N/A — no follow-up was needed._

---

## Problem 4: Create account and login

**Name/Title:** Build the signup/login flow, test it end-to-end, and document the auth design

**Prompt:**
> Great let's do problem 4: Create account and login. Build out a classic create-account/login flow with the normal components (name, email, password, confirm password) and then a login page that asks for an email and password. Once it's set up use the test user (email: test@campuscustoms@yale.edu, password: password) to make sure that the flow works. Then, create a brand new account to test the flow again. Once we are sure that the flow works, put in a write up about how the auth works (including how passwords are protected) in output/harness.md

**Follow-up prompts:**
_None at the time — built `backend/auth.py` (PBKDF2-HMAC-SHA256, 390,000 iterations, random per-user salt, constant-time comparison) plus `POST /api/auth/signup` and `POST /api/auth/login` in `main.py`. Discovered the seed `password_hash` values for the two non-test seed users use an unidentified 3-field scheme that doesn't verify as standard PBKDF2 under any common iteration count tried; re-hashed the test user's password with this project's real implementation so the documented test credentials work, and disclosed that decision in `output/harness.md` rather than silently patching around it. Wired the frontend: `AuthContext` (React context + localStorage), a functional Login page and Create Account page (first/last name, email, password, confirm password, inline error states), and a navbar that swaps to "Hi, `<name>`" + Log Out once signed in. Verified end-to-end via curl: login with the test user, signup + login with a brand-new account, and the negative cases (wrong password, duplicate email, mismatched confirm-password)._

**Why an additional prompt was needed:**
_N/A — no follow-up was needed._

---

## Problem 5: PydanticAI Agent Backend

**Name/Title:** Build the Campus Customs chatbot as a PydanticAI agent behind FastAPI

**Prompt:**
> Great, let's start Problem 5: PydanticAI Agent Backend. Let's create the chatbot as a PydanticAI agent behind FastAPI. The app should be in backend/main.py - keep the agent as the four files (run with Uvicorn) next to it. 1) backend/prompts/prompt/md - system prompt 2) beckend/agent.py - agent entry/wiring 3) backend/tools.py - available tools 4) backend/models.py - Pydantic/PydanticAI structured types. Main.py should have a chat route to let a message coming in from the website give a reply from the agent. As you are doing this, ensure that the Campus Customer voice and safety basics are in prompts/prompt.md. Edit types in models.py for chat replies/product cards as needed. Record how the agent works (how front end connects to FastAPI, how agent is loaded, etc.) in output/harness.md. The backend should run like this: uvicorn main:app --reload --port 8000

**Follow-up prompts:**
_None — installed `pydantic-ai-slim[openai]`; built the four files (`prompts/prompt.md` with Campus Customs voice + safety/boundary rules, `models.py` with `ProductCard`/`ChatReply`, `tools.py` with `search_products`/`get_product`/`check_size_availability` plus the Portkey-routed `model_for_agent()`, `agent.py` wiring the `Agent` + `@agent.tool_plain` registrations + `run_chat`); rewired `POST /api/chat` in `main.py` to call the real agent instead of the Problem 3 stub; updated the frontend's chat types/widget to the new `{message, products}` reply shape and to pass the signed-in `user_id` for memory. Added per-user conversation memory via the existing `chat_messages` table (read last 10 turns in, write the new turn back out). Verified live end-to-end: product search, honest "not available in that color" answers, multi-turn memory (a follow-up referring to "the mom hoodie" without repeating its name correctly resolved via history), off-topic refusal, and a prompt-injection attempt -- which surfaced as an unhandled 500 from the model gateway's own content filter on first test, so added explicit `ModelHTTPError`/`UnexpectedModelBehavior` handling in `run_chat` to fail safely with an on-brand decline instead, then re-verified it returns 200. Documented all of this (file roles, frontend-to-FastAPI flow, agent loading, memory, verified safety behavior) in `output/harness.md`._

**Why an additional prompt was needed:**
_N/A — no follow-up was needed; the only correction (the content-filter 500) was caught and fixed during this same pass, before reporting completion._

---

## Problem 6: Product info and stock

**Name/Title:** Ground product/price/stock answers strictly in the database, add explicit tool-routing rules, and document the tools

**Prompt:**
> Let's do problem 6: Product info and stock. We need the agent to be able to look up real information from campus_customs.db (info such as product description, price, how many are in stock and by size). All data must come from the database - do not invent any prices or quantities and if something is out of stock, report it directly. Add to prompts/prompt.md to tell the agent which tools to call for these types of questions and update models.py. In output/harness.md, create a write up of the tools - what are the tools, what fields did you choose for results, why

**Follow-up prompts:**
_None — Problem 5 had already built `search_products`/`get_product`/`check_size_availability` grounded in the database, but there was no tool for a whole-product, all-sizes stock breakdown (only a single-size check or the full product card). Added `StockInfo` to `models.py` (a deliberately narrower model than `ProductCard` -- just `product_id`/`name`/`inventory`/`total_stock`/`in_stock`, keeping zero-quantity sizes rather than filtering them out) and a new `get_stock(product_id)` tool in `tools.py`/`agent.py`. Added an explicit "which tool to call, by question type" section to `prompts/prompt.md` mapping category/browsing questions to `search_products`, description/price questions to `get_product`, whole-product stock questions to `get_stock`, and single-size questions to `check_size_availability`, plus an instruction never to soften a 0-quantity result. Verified live: a full per-size stock breakdown, an in-stock single-size check, a confirmed-zero single-size check (reported directly as "out of stock," not softened), a price question, and a nonexistent product (agent said it couldn't find it rather than inventing one). Wrote up all four tools -- what each answers, its result model, and why those fields were chosen -- in `output/harness.md`._

**Why an additional prompt was needed:**
_N/A — no follow-up was needed._

---

## Problem 7: Chat search that updates the page

**Name/Title:** Have the agent's structured product matches drive the Products page, not just the chat panel

**Prompt:**
> Problem 7: Chat search that updates the page. We need to add a feature where if a customer asks the chatbot about a type of item (i.e. hoodie or tshirt) the website should show all matching items from the catalogue as product cards (with key info like image name and price). This is an API contract - structured product matches are rendered on the website. The same click on product card and get to single item page that we worked on in problem 3 should still work. Once the agent produces the matching product cards, the user should still be able to click on a product card and get the large image and detailed description on a single page. Update prompts/prompt.md and output/harness.md logging how this is done

**Follow-up prompts:**
_None — added `frontend/src/search/ChatResultsContext.tsx` (shared React context above the router) so `ChatWidget` can hand the agent's `ChatReply.products` to the `Products` page, which now shows a "showing N matches for your chat question" banner + grid (reusing the same `ProductCard` component, so the Problem 3 click-through to the single-item page needed no changes) instead of its normal full-catalogue view, with a "Show All Products" button to clear it. `ChatWidget` now shows a short note in the chat bubble rather than duplicating full cards inline. While verifying, found two real gaps working against "show all matching items": the agent's tool-level default silently capped category searches at 5 results, and the scorer's exact-token matching missed real synonyms (a "hoodie" query didn't match catalogue entries whose `garment_type` was "hooded sweatshirt," undercounting by the 27 hood-related products confirmed directly in the database). Fixed both (raised + fixed the cap, switched to substring-overlap scoring), and re-verified "show me all your hoodies" returns all 27 matches, a single-product question still attaches only 1 card, and t-shirts return 27 against 25 true t-shirt rows (the 2 extra being legitimate description/tag hits). Updated `prompts/prompt.md` with explicit instructions to attach every real category match rather than trimming for reply brevity, and documented the whole mechanism (contract, frontend wiring, the two bugs and fixes, verified results) in `output/harness.md`._

**Why an additional prompt was needed:**
_N/A — no follow-up was needed; both gaps were caught and fixed during this same pass, before reporting completion._

---

## Problem 8: Customer Memory

**Name/Title:** Persist and reload chat history for logged-in customers, give the agent name/email via deps, and ground follow-ups in real page context

**Prompt:**
> Problem 8: Customer Memory. Create a running chat log memory for logged in cusotmers so that their chat history reloads whenever they return. The agent should remember the name and email and put that in agent dept or tools the agent can call. There should also be enough context from the page so that the agent can answer follow up questions (hintL you can put code into the agent context). This chat memory does not need to exist for non-logged in (guest) users. Update output/harness.md with a brief writeup on how chat history is stored, what the agent is able to see about the customer, and how the general page context works

**Follow-up prompts:**
_None — added `GET /api/chat/history/{user_id}` (`database.get_chat_history`) returning the full stored transcript with product cards parsed back out, and wired `ChatWidget.tsx` to fetch and restore it whenever `user` changes from signed-out to signed-in, resetting to a fresh greeting for guests and on logout (chat memory already only persisted for `user_id is not None` since Problem 5, matching "guests don't need this"). Refactored `agent.py` to use a proper PydanticAI `deps_type` (`CustomerContext`: user_id, first_name, last_name, email, page_description), rebuilt fresh from the database on every run (never trusted from the client beyond the bare user_id), injected via two `@agent.system_prompt` functions -- one for identity (with an explicit "you have no name/email" statement for guests), one for page context. Added `agent.describe_page(page_path)`, which turns the frontend's current route into a plain-language, code-generated sentence (looking up the real product via `database.get_product` for a product page) rather than letting the model guess at a bare URL -- the "put code into the agent context" hint. Hit one compatibility bug while testing history reload: the database's original seed `chat_messages` rows predate the `in_stock`/`search_tags` fields on a product card and failed response validation; fixed with `database._normalize_product_dict` filling in both for older rows before they're returned. Verified live: a logged-in user asking "do you know who I am?" gets greeted by name, the identical guest message gets an honest "I don't know, you're browsing as a guest," and "is this in stock?" with no product named resolves correctly purely from `page_path` context. Documented storage, agent-visible identity, and page context in `output/harness.md`._

**Why an additional prompt was needed:**
_N/A — no follow-up was needed; the history-reload compatibility bug was caught and fixed in this same pass, before reporting completion._

---

## Problem 9: Usability Improvements

**Name/Title:** Identify ranked frontend/backend usability improvements (advisory, no implementation yet)

**Prompt:**
> Problem 9: Usability Improvements. Help me identify a list of 5 front end and 5 backend usability improvements that we could implement, ranked in order of general impact (I trust your judgement on how to quantify that here)

**Follow-up prompts:**
_Reviewed the actual frontend (NavBar, ChatWidget, Products/ProductDetail, routing) and backend (main.py, agent.py, database.py, auth) for concrete, already-present gaps rather than generic suggestions, then ranked both lists by how many users/requests are realistically affected and how severe the failure mode is. Reported the list in chat with no code changed yet, since the problem was explicitly advisory first._
>
> Yes - let's implement the 2 most impactful front end and 2 back end edits. Write output/usability.md that describes each improvement and why it is beneficial for either the user or the business. Please double check that these features do show up in the running app

**Why an additional prompt was needed:**
_Not a correction -- the initial message asked only for the ranked list ("help me identify"); implementing the top items was always framed as a separate decision for the user to make once they'd seen the options, which this follow-up supplied._

**Implementation notes (from the second prompt above):**
_Frontend #1 (auto-scroll chat to latest message) and #2 (mobile hamburger nav) implemented in `ChatWidget.tsx`/`NavBar.tsx`+`NavBar.css`. Backend #1 (real server-side sessions -- signed, expiring tokens via `auth.create_session_token`/`verify_session_token`, verified per-request instead of trusting a client-stated `user_id`) and #2 (input validation + a per-identity sliding-window rate limiter, `ratelimit.py`) implemented across `auth.py`, `main.py`, `schemas.py`. Implementing #1 required re-plumbing the frontend's auth flow end-to-end (AuthUser gained a `token` field, `client.ts` now attaches it as an `Authorization` header, `ChatWidget` passes it instead of a bare id) since the whole point was removing the client-trusted id path Problem 8 had used. Verified everything in the actual running app via the browser preview tool (not just curl): logged in through the real login form, confirmed chat history reloaded already scrolled to bottom, sent a live message and watched auto-scroll track the pending/final reply, confirmed the Problem 7 Products-page update and Problem 3 click-through both still work end-to-end, and resized to a 375px mobile viewport to open and inspect the hamburger menu. Backend-only checks (token ownership enforcement, message-length validation, rate-limit threshold) verified via curl/unit check. Wrote `output/usability.md` with a per-improvement description, the concrete problem it fixes, user/business benefit, and what was verified._

---

## Problem 10: Style the Website

**Name/Title:** Collegiate visual redesign -- original Yale-inspired branding, hover-pop product cards, and a reordered homepage

**Prompt:**
> Let's do Problem 10: Style the Website. I want to add extra creative design that really brands this with Yale branding. I want to include Yale logos, bulldogs, and other features that make the website look collegiate. Add a feature where product cards pop when a user moves their cursor over them. I want to make sure the order of the website makes sense - start with a catchy title and subheading, common categories to highlight that users can click on and then an easy to parse catalogue. Use other popular clothing websites like https://www.aritzia.com/us/en for inspiration

**Follow-up prompts:**
_None — rather than reproducing Yale's actual trademarked seal/logo (a real IP concern), created two original collegiate-style motifs: `BulldogMark.tsx` (a bulldog face, iterated once after the first version read as an abstract blob rather than a recognizable bulldog) and `CrestMark.tsx` (a generic shield/monogram), used in the navbar, a new site-wide `Footer`, and as a hero watermark. Built `utils/categories.ts` to bucket the catalogue's messy free-text `garment_type` into six stable categories (reusing the same normalization problem solved for search in Problem 7), then `CategoryTiles.tsx` -- real product photos as clickable category tiles on the homepage, Aritzia-style -- and wired matching chip filters plus a `?category=` query param into the Products page. Reordered the homepage to hero -> category tiles -> an 8-product catalogue preview with a "view all" link -> a trust strip, replacing the old static text-only sections. Gave `ProductCard` a spring-eased hover "pop" (scale + lift + shadow + image zoom + a sliding "View Details" overlay). Verified everything in the live browser preview across desktop and a 375px mobile viewport: category tiles/chips with correct counts (27+30+26+16+3=102), category filtering, the hover pop, and the footer/trust-strip rendering consistently across Home, Products, and About._

**Why an additional prompt was needed:**
_N/A — no follow-up was needed; the one revision (the bulldog SVG) was caught and fixed by visually reviewing the rendered result in this same pass, before reporting completion._

**Follow-up prompt:**
> Can I see the website
>
> *(user then shared two personal photos of Harkness Tower and the Sterling Memorial Library courtyard)* Can we add more character to this website please? Using Yale colors of Yale blue, white, and gray, create a checkered/plaid background to add more dimension. Play around with adding these copyright free images that I am uploading here of Yale campus. Potentially turn those images into line drawing or just use the image itself - use your creative freedom

**Follow-up implementation notes:**
_Saved the two uploaded campus photos into `frontend/public/images/campus/`. Added a reusable navy-duotone photo treatment (`.photo-duotone` in `index.css` -- grayscale + a `mix-blend-mode: multiply` navy overlay) so the full-color photos read as part of the blue/white/gray palette instead of clashing with it, and a subtle crossed-`repeating-linear-gradient` plaid texture (`.plaid-bg`/`.plaid-bg-dark`) applied site-wide via `body` and as a stronger navy-and-gold variant behind a new "Campus Heritage" section. Replaced the hero's flat gradient with the Sterling Library photo in duotone behind the existing navy overlay, and added the "Rooted on Old Campus" section featuring both photos gold-bordered side by side. Verified in the live browser preview at both desktop and 375px mobile widths that the duotone/plaid treatment and photo layout hold up and stay legible._

---

**Second follow-up prompt:**
> can we alter the plaid pattern to be more of a preppy tartan?

**Second follow-up implementation notes:**
_The original pattern was a uniform two-layer grid (same stripe width/spacing on both axes), which read as graph paper rather than plaid. Replaced it in `index.css` with an actual tartan sett: an asymmetric repeat (wide navy block + gray block of a different width) plus two offset thin "overcheck" threads (a gold pinstripe and a navy hairline) layered on both axes within one 96px period, so the bands cross and their alpha stacks at the intersections -- the woven look real tartan has, built with the same `repeating-linear-gradient` technique but with uneven band widths and the added thread layers instead of a symmetric grid. Did the same for the dark navy variant (`.plaid-bg-dark`) using white/gold threads against the navy field. Verified live that it reads as tartan rather than a grid, and that text over both the light and dark variants (hero, Campus Heritage section, product cards) stays fully legible._

## Problem 11: Site Testing (App Check)

**Name/Title:** Live end-to-end verification of the chat/stock, chat-search-to-product-page, and one Problem 9 usability feature, documented for TA grading

**Prompt:**
> We need to run through and test the various features that we have created for this website. I want to then document the tests and findings in output/app_check.html - this is how my TAs will grade the homework, so ensure that for each of the following tests, you include a clear heading for the check, a key screenshot on the thing being checked, and a 1-2 sentence description of what the screenshot is showing or proving about the test. The screenshots should be in output/app_check_images/ and link them from app_check.html with relative paths (for example app_check_images/inventory.png). Here is what you need to check: 1) Make sure that the chat can check the inventory level of an item and the true stock number and price from the DB is returned 2) After asking the chat for category (like hoodies), search result cards appear that can be clicked on to lead to single product description pages 3) pick ONE of the usability features we added in problem 9 to test and record

**Follow-up prompts:**
_None — queried `campus_customs.db` directly first to get ground-truth price/inventory for a test product (Champion Reverse Weave Hoodie 1: $68, XS 0/S 25/M 20/L 20/XL 0/XXL 15, 80 total), then drove the real running app through the browser preview tool (not just curl) for every check: asked the chatbot the same question and confirmed its answer matched the database exactly; asked a category question ("what crewnecks do you have?") and confirmed the Products page itself updated with 40 real matching cards, then clicked one through to its full single-item detail page; and, picking mobile hamburger navigation as the one Problem 9 usability feature to test, resized to a 375px viewport and confirmed the menu opens with working links and the signed-in greeting. Saved all four screenshots to `output/app_check_images/` and wrote `output/app_check.html` -- a standalone, Yale-branded report with a summary table and one section per check, each with a heading, the screenshot(s), and a 1-2 sentence finding -- then rendered the actual HTML file in a second preview server to confirm every image path resolves and the layout is grading-ready._

**Why an additional prompt was needed:**
_N/A — no follow-up was needed._

---

## Problem 12: Audit Trail, Expanded Safety Guidelines, and Harness Wrap-Up

**Name/Title:** Append-only agent audit log, thorough safety rules in prompts/prompt.md, and a manager-level harness.md summary

**Prompt:**
> We need to keep a log of agent loop activity (time, tool name, short args/result, stop reason) in an append only output/audit_trail.json. Do not wipe this between runs, just keep appending to it. In prompts/prompt.md, add several safety guidelines around the chatbot and website including the following: 1. Do not store information about a logged in user other than the basics required for the chat history to function as intended 2. Pull information from the database only - never invent or pull numbers or prices from the web. Please think of other safety guidelines using Homework 3 as an example of the level of thoroughness for the safety guidelines. Add those safety rules to prompts/prompt.md. Once all of that is complete, finish output/harness.md to include info on 1) model fields in models.py and why you chose them 2) tools and abilities 3) safety rules 4) specs (loop limits, result caps, models, how to run front + back). The harness.md should make it clear how the system works

**Follow-up prompts:**
_None — added `AuditEntry` to `models.py` (mirroring the Homework 3 audit design: timestamp, run_id, tool_name, tool_args, result_summary, stop_reason, duration_ms, error) and `new_run_id`/`model_finish_reason`/`audit_entry`/`append_audit_entries` to `tools.py` (the same read-existing-array/append/rewrite pattern Homework 3 used, so the file is never reset). Switched the four tools in `agent.py` from `@agent.tool_plain` to `@agent.tool` (gaining `RunContext[CustomerContext]`, with a new `run_id` field added to `CustomerContext`) so every tool call and the overall `agent.run` step could be logged under one shared run_id via a new `_audit_tool_call` wrapper. Expanded `prompts/prompt.md`'s safety section from 5 bullets into a four-category "Safety Guidelines" section (data minimization -- including both explicitly requested rules, data provenance, prompt-injection/role integrity, scope/resource limits) at Homework-3-level thoroughness. Verified the audit trail live against the running backend: a first chat turn produced 3 correctly-grouped entries; a second, independent turn appended 2 more under a new run_id (confirmed the file grew rather than reset); and a prompt-injection attempt that the model gateway's own content filter rejected logged a proper `error:ModelHTTPError` entry with the real error message attached. Finished `output/harness.md` with a "System Summary (Manager-Level Overview)" section (moved to the top of the file, after the Homework 3 convention) covering all four requested areas -- models.py fields and rationale, tools and abilities, safety rules, and specs/how-to-run -- plus a new dedicated "Audit Trail" section documenting the mechanism and what was verified._

**Why an additional prompt was needed:**
_N/A — no follow-up was needed._

---
