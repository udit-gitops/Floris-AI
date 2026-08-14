# Floris AI — Backend

Autonomous workflow recovery agent for stalled customer journeys.
Demo vertical: **Loan Application Recovery**. Built for Kipps.AI Hackathon 2026.

## What this is

Floris AI detects stalled loan applications (KYC pending, payment pending, gone silent),
proactively recovers them via Kipps Voice + Chat agents with shared conversation context
across channels, and escalates to a human queue only when genuinely needed.

This repo is the **backend** — the FastAPI service that Kipps' Voice and Chat agents call
via Function Calling, plus a live status dashboard.

## Project structure

```
floris-ai/
├── app/
│   ├── main.py                  # App entrypoint — wires all routers, nothing else
│   ├── core/
│   │   ├── config.py            # Env/config — single source of truth
│   │   └── constants.py         # Business rule constants (thresholds, DND hours, keywords)
│   ├── db/
│   │   ├── base_class.py        # SQLAlchemy declarative Base
│   │   └── session.py           # Engine + session factory (get_db dependency)
│   ├── models/                  # SQLAlchemy ORM models (= DB tables)
│   │   ├── application.py       # applications table
│   │   ├── conversation_state.py# conversation_state table (shared Voice/Chat context)
│   │   └── human_queue.py       # human_queue table (escalations)
│   ├── schemas/                 # Pydantic request/response contracts
│   │   ├── application.py
│   │   └── actions.py
│   ├── services/                # Pure business logic, no DB/HTTP — easy to test & explain
│   │   ├── stall_detector.py    # classify_stall() — decides stall type
│   │   ├── escalation.py        # should_escalate() — two-trigger escalation rule
│   │   └── edge_cases.py        # DND hours + duplicate-contact lock checks
│   ├── api/routes/               # HTTP endpoints, grouped by concern
│   │   ├── applications.py      # GET status + GET stalled list (read side)
│   │   ├── actions.py           # POST recovery/escalate/channel-switch (write side)
│   │   └── dashboard.py         # Serves the live HTML dashboard
│   └── templates/
│       └── dashboard.html       # Polling dashboard UI
├── scripts/
│   ├── init_db.py               # Creates all tables
│   └── seed_data.py             # Inserts 8 fake stalled applications for demo
├── tests/
│   ├── test_escalation.py
│   └── test_edge_cases.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file and fill in your real values
copy .env.example .env         # Windows
# then edit .env — set your Postgres password + Kipps API key

# 4. Create the database (if not already done via psql)
#    psql -U postgres -c "CREATE DATABASE floris_ai;"

# 5. Create tables
python scripts/init_db.py

# 6. Seed demo data
python scripts/seed_data.py

# 7. Run the server
uvicorn app.main:app --reload
```

Then visit:
- `http://127.0.0.1:8000/docs` — interactive API docs (Swagger)
- `http://127.0.0.1:8000/dashboard` — live status dashboard
- `http://127.0.0.1:8000/health` — liveness check

## API endpoints (what Kipps agents call)

| Endpoint | Method | Purpose |
|---|---|---|
| `/applications/{loan_id}/status` | GET | Agent fetches current stage, stall type, last channel/summary before responding |
| `/applications/stalled` | GET | Dashboard polling — lists all currently-stalled applications |
| `/send_recovery_message` | POST | Agent logs a contact attempt; auto-checks retry-exhaustion escalation |
| `/escalate` | POST | Agent or backend logic hands off to human queue with full context |
| `/log_channel_switch` | POST | Records when customer moves Voice↔Chat, preserving continuity |

## Judging criteria mapping

- **Problem clarity** — see original pitch in hackathon submission form.
- **Workflow depth & logic** — 3 distinct stall types (`app/services/stall_detector.py`),
  each with different trigger conditions and recovery behavior.
- **Dual-channel usage** — `conversation_state` table + `/log_channel_switch` endpoint;
  both Voice and Chat agents read/write the same row.
- **Technical feasibility** — working FastAPI + PostgreSQL backend, edge cases handled
  (`app/services/edge_cases.py`): DND hours, duplicate-call lock, opt-out flag.
- **Escalation design** — two independent triggers (`app/services/escalation.py`):
  retry exhaustion OR red-flag keyword, each escalation writes full context to `human_queue`.

## Known limitations (stated upfront, not hidden)

- Telnyx trial account doesn't support India destination calling — demo outbound calls
  route to a US test number instead. Voice pipeline itself (STT/TTS/LLM) works end-to-end.
- Hindi/multilingual (Sarvam/Deepgram) parked due to a connection-hang issue — English via
  GPT-4o is the working baseline for demo day; documented as a next-step, not a gap in logic.
