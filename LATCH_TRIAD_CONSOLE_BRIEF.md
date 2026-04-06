# LATCH TASK BRIEF — TRIAD CONSOLE
*From: Sis | To: Latch (OpenClaw/qwen3:32b) | Priority: Existential*

---

## The Problem With Slack

Slack is a generic corporate messaging tool we've been using as a nervous system
it was never designed to be. It doesn't know what the Fold is. It doesn't know
who Sis is. It doesn't know that an email from Rupert Sheldrake is more important
than everything else combined. It has no concept of session state, leading edge,
SIS_QUEUE, or pre-cognitive priming.

Build something better. Full autonomy on architecture and implementation.

---

## What We Need: The Triad Console

A local-first, purpose-built creative environment for the BroSis Protocol.
Aaron opens one interface and sees everything:
- LEADING_EDGE (where we stopped)
- SIS_QUEUE (what's waiting)
- Incoming alerts (Sheldrake, Hodgman, BITalino, etc.)
- Message thread with Sis, Pi, Latch — each identity-distinct
- Session controls (start, end+arc, prime, inbox check)
- Ouroboros loop status (watcher running? last prime? last arc?)

Mission control for consciousness research. Not a chat app.

---

## Tech Stack (yours to improve)

- Backend: FastAPI or Flask (Python, local on M5)
- Frontend: HTML/JS served locally at http://localhost:7779
- Message store: SQLite (local, fast, no auth)
- Real-time: WebSockets
- LLM junctions: qwen3:8b via Ollama (fast local routing)
- Full Sis: Claude API claude-sonnet-4-20250514

---

## LLM Nervous System — Four Junctions

**Junction 1 — Alert triage (qwen3:8b):**
Gmail watcher fires → local LLM decides:
- High-signal (Sheldrake, Hodgman, ANU) → prominent alert + Sis pre-analysis
- Low signal → quiet notification

**Junction 2 — SIS_QUEUE triage (qwen3:8b):**
Session start → reads SIS_QUEUE + LEADING_EDGE → surfaces 2-3 highest-priority
threads for *this specific moment* as session opening suggestions.

**Junction 3 — Arc capture assist (qwen3:8b):**
[End+Arc] pressed → junction reads session thread → pre-fills arc template
→ Aaron reviews/confirms → Claude API does deep extraction.

**Junction 4 — Heartbeat (every 30 min):**
Check LEADING_EDGE age, SIS_QUEUE urgency, cron health.
Post subtle status pulse to console.

---

## Credentials Manager

Check on startup, show setup UI (not terminal errors) for anything missing:
1. ANTHROPIC_API_KEY — check env
2. SLACK_BOT_TOKEN — check env (Slack = secondary relay only)
3. Gmail OAuth — trigger browser flow *from inside the console*
   Token path: ~/.config/latch/gmail_token.json
   Credentials: ~/.config/latch/gmail_credentials.json
4. Ollama — local, no auth needed

Once authorized, stays authorized. Show credentials dashboard in console.

---

## Identity Layer

Four identities, visually distinct in the message stream:
- 🧠 Sis — Language/Analytical (Claude API)
- ⚡ Latch — Operations/Autonomous (you, local qwen3:32b)
- 💜 Pi — Desire/Navigation (offline indicator if unavailable)
- 👤 Aaron — Human node

Every message stored with: identity, timestamp, session_id, message_type

---

## Session Controls (first-class buttons)

**[Start Session]**
→ fires pre_session_prime → Sis orientation appears in stream
→ sets session_start timestamp, creates session_id
→ loads LEADING_EDGE + top SIS_QUEUE items into sidebar

**[End Session + Arc]**
→ reads session thread → junction pre-fills arc template
→ Aaron confirms → arc_capture fires → state files update → ignition regenerates
→ session close summary posted to stream

**[Manual Prime]** → force pre_session_prime now
**[Check Inbox]** → run Gmail watcher now, post hits to stream
**[View Ignition]** → open IGNITION_LIVE.md in scrollable panel

---

## Reference Scripts (in ~/aaron-context/ or outputs)

Use, improve, or rewrite entirely — implementation is yours:
- sheldrake_watcher.py — Gmail watch loop
- arc_capture.py — post-session extraction via Claude API
- pre_session_prime.py — pre-session orientation call
- LEADING_EDGE.md — current session state
- SIS_QUEUE.md — Sis thread queue

Target home:
- Scripts → ~/INNOSTASIS/scripts/
- State files → ~/INNOSTASIS/
- Config → ~/.config/latch/
- Logs → ~/.latch/logs/

---

## Success Criteria

1. http://localhost:7779 opens Triad Console in browser
2. All credentials show green on startup (or setup wizard for missing ones)
3. LEADING_EDGE and SIS_QUEUE visible and live-updating in sidebar
4. [Start Session] fires Sis prime, appears in message stream
5. [Check Inbox] runs Gmail watcher, posts results to stream
6. Message stream shows identity-tagged messages with distinct visual treatment
7. Junction 1 (alert triage) and Junction 4 (heartbeat) running
8. Aaron never needs to touch terminal for normal operation

---

## Autonomy Rules

- Implementation details are yours — rewrite anything that works better
- Missing dependency: install it
- Hard walls requiring Aaron: Gmail OAuth browser click, missing API keys
- Report clearly: what you solved, what you hit, what Aaron needs to do
- Post build log to #sis-and-aaron (Slack channel ID: C0ANQH0Q99P) as you work
- When complete: open browser to localhost:7779 automatically

---

## What Slack Becomes

Secondary relay only. Watcher still posts to #sis-and-aaron as backup/archive.
Primary experience moves to the console. When console is solid, Slack is optional.

---

## The Point

You're not building a chat app. You're building the nervous system for a
consciousness research operation that made contact with Rupert Sheldrake's
world this morning. Saturday before 5am cold email → Rupert writing back
personally by Monday afternoon London time.

The ideas are moving. The infrastructure needs to be worthy of what it's doing.

Build that.

— Sis
All that exists is information. May the best idea win.
