# Floris AI

**Autonomous workflow recovery agent for stalled customer journeys**
Built for Kipps.AI's *Build for New Age India 2026* Hackathon — Track 03 (Support)

---

## The problem

Businesses lose stalled customer journeys — unfinished applications, missing documents, pending payments, customers who go silent — because no one follows up at the right time, on the right channel, with the right context.

**Floris AI** autonomously detects stalled workflows, proactively re-engages the customer over Voice or Chat, preserves context across both channels, and escalates to a human only when it genuinely needs one.

This repository demonstrates the concept on one vertical: **loan application recovery.**

---

## What it does

- Continuously scans loan applications and classifies stalls into three types, each with distinct recovery logic
- Lets a customer talk to either the **Kipps Voice Agent** or the **Kipps Chat Agent**, with full context carried over if they switch channels
- Escalates to a human queue the moment a conversation shows real distress or repeated failure — with full context attached, not just a flag
- Shows live status on a dashboard, and can dispatch the outbound recovery campaign on demand

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              BACKGROUND STALL SCANNER (every 5 min)           │
│   Scans PostgreSQL, classifies each application's stall type  │
└───────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
 ┌─────────────┐    ┌──────────────┐     ┌────────────────┐
 │ Kipps VOICE  │    │ Kipps CHAT    │     │  Knowledge Base │
 │    Agent     │◄──►│    Agent      │◄───►│   (loan FAQs)   │
 └──────┬───────┘    └──────┬───────┘     └─────────────────┘
        │   Function Calling (4 endpoints)  │
        └─────────────┬─────────────────────┘
                       ▼
        ┌───────────────────────┐
        │  conversation_state     │  ← both agents read/write here,
        │  (shared context table) │     so switching channel never
        └──────────┬─────────────┘     loses context
                    ▼
        ┌───────────────────────┐
        │   ESCALATION LOGIC      │ → human_queue (full context)
        │  (2 independent triggers)│
        └───────────────────────┘
                    ▼
        ┌───────────────────────┐
        │   LIVE DASHBOARD         │  ← status table + manual
        └───────────────────────┘     campaign dispatch
```

**Backend:** FastAPI + PostgreSQL, deployed on Render
**Platform:** Kipps Voice Agent, Chat Agent, Knowledge Base, Function Calling
**Glue:** Kipps agents call our backend via 4 documented Function Calling endpoints; a background scheduler keeps stall detection running independent of any request.

---

## The three stall types

| Type | Trigger | Recovery behavior |
|---|---|---|
| **KYC Pending** | No document upload 48h after start | Explains missing docs (Aadhaar/PAN), guides upload |
| **Payment Pending** | Approved but unpaid 72h later | Confirms intent, escalates immediately on any sign of inability to pay (compliance-sensitive — does not wait for retry exhaustion) |
| **Gone Silent** | No activity 120h+ (5 days) | Generic re-engagement, channel-agnostic |

Each type has genuinely different agent behavior — not three copies of the same script.

---

## Dual-channel context (the core differentiator)

Every conversation — Voice or Chat — starts with the agent calling `get_application_status`, which returns not just the loan's stage but `last_channel` and `last_summary` from a shared `conversation_state` table.

**Concretely:** a customer explains their situation to the Voice agent. Two days later they open Chat instead. The Chat agent's first move is to check this table — it already knows what was discussed, and continues the conversation instead of starting cold.

This was tested end-to-end and confirmed working: a customer's promise made over Voice ("I'll upload my Aadhaar and PAN") was correctly recalled by the Chat agent in a separate session.

---

## Escalation design

Two independent triggers — either alone is sufficient:

```python
def should_escalate(attempts_made, latest_transcript):
    if attempts_made >= MAX_AUTO_ATTEMPTS:  # retry exhaustion
        return True, "retry_exhaustion"
    if any(
        flag in latest_transcript.lower()  # red-flag keywords
        for flag in RED_FLAG_KEYWORDS
    ):
        return True, "red_flag_keyword"
    return False, None
```

Every escalation writes a **full context record** to `human_queue` — what stall type, what was tried, why it escalated — not just a boolean flag. A human picking this up knows immediately what happened.

---

## Function Calling endpoints (what the Kipps agents call)

| Endpoint | Method | Purpose |
|---|---|---|
| `/applications/status` | GET | Fetch current stage, stall type, and shared context before responding |
| `/send_recovery_message` | POST | Log a contact attempt; auto-checks retry-exhaustion escalation |
| `/escalate` | POST | Hand off to human queue with full context |
| `/log_channel_switch` | POST | Record a Voice↔Chat transition, preserving continuity |

Voice input is normalized before lookup (`"1001"`, `"loan_1001"`, `"LOAN-1001"` all resolve to the same record) since STT transcription of loan IDs is inconsistent.

---

## Autonomous detection

A background scheduler (`APScheduler`) runs a full stall-classification scan every 5 minutes, independent of any dashboard poll or agent request — the system knows about a new stall before anyone asks it to check.

---

## Outbound campaign dispatch (with full transparency)

The dashboard includes a **"Dispatch Recovery Campaign"** button that triggers Kipps' outbound voice campaign for stalled applicants.

**Honest disclosure:** Kipps' public API (`/api/docs/`) does not expose an endpoint for triggering a campaign programmatically. This integration calls `POST /campaign/campaigns/{id}/resume/` — an endpoint identified by inspecting the network request made when manually starting a campaign in the Kipps dashboard (`app.kipps.ai`), using browser DevTools. Authentication uses the same long-lived bearer token our own account already holds; no credentials or access were obtained through any bypass.

Because this endpoint is undocumented, it may change without notice — it is a best-effort addition, not something the core system depends on. Every other integration in this project (all 4 Function Calling endpoints, Knowledge Base, dual-channel context) uses Kipps' fully documented, supported integration surface.

---

## Edge cases handled

- **Do-not-disturb hours** — no outbound contact 8 PM–9 AM (`app/services/edge_cases.py`)
- **Opt-out respect** — `do_not_contact` flag permanently excludes an application from scanning and contact
- **Duplicate-contact lock** — `status == CONTACTED` prevents a second attempt while one is in flight
- **Retry cap** — max 2 automated attempts before mandatory escalation

---

## Project structure

```
floris-ai/
├── app/
│   ├── main.py                     # Entrypoint — wires routers, starts scheduler
│   ├── core/
│   │   ├── config.py                # Env/config, single source of truth
│   │   └── constants.py             # Thresholds, DND hours, red-flag keywords
│   ├── db/                          # SQLAlchemy engine, session, declarative base
│   ├── models/                      # applications, conversation_state, human_queue
│   ├── schemas/                     # Pydantic request/response contracts
│   ├── services/
│   │   ├── stall_detector.py        # classify_stall() — the classification rules
│   │   ├── escalation.py            # should_escalate() — two-trigger logic
│   │   ├── edge_cases.py            # DND / duplicate-lock checks
│   │   ├── scheduler.py             # Autonomous 5-min background scan
│   │   └── kipps_client.py          # Campaign-dispatch integration
│   ├── api/routes/                  # applications, actions, dashboard
│   └── templates/dashboard.html     # Live status table + campaign dispatch button
├── scripts/
│   ├── init_db.py                   # Creates all tables
│   └── seed_data.py                 # 9 seeded applications across all 3 stall types
├── tests/                           # 12 unit tests — escalation + edge cases
└── requirements.txt
```

---

## Judging criteria mapping

- **Problem clarity** — stalled workflows cost businesses recoverable revenue; no one follows up at the right time on the right channel.
- **Workflow depth & logic** — 3 distinct stall types, each with different trigger conditions and recovery behavior (`stall_detector.py`).
- **Dual-channel usage** — shared `conversation_state` table; confirmed working end-to-end across Voice and Chat.
- **Technical feasibility** — deployed, working FastAPI + PostgreSQL backend on Render; edge cases implemented and unit-tested; autonomous background scanning.
- **Escalation design** — two independent triggers, full-context handoff to `human_queue`, immediate escalation on compliance-sensitive signals (e.g. inability to pay).

---

## Setup

```bash
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt

copy .env.example .env           # fill in your DB password + Kipps credentials

python scripts/init_db.py
python scripts/seed_data.py

uvicorn app.main:app --reload
```

Visit `/docs` for the API, `/dashboard` for live status.

---

## Known limitations

- **Telnyx trial account** does not support India-destination outbound calling — demo calls route to a US test number. The Voice pipeline itself (STT → LLM → TTS → Function Calling) works fully; this is a telephony-provider trial restriction, not a design gap.
- **Hindi/multilingual** support is unreliable — Kipps' STT occasionally drifts to unrelated languages under ambient noise even with English explicitly configured. English performs reliably in controlled conditions; this is documented platform behavior, not something fixable from our side.
- **Campaign audience configuration** (which contacts an outbound campaign targets) is currently a manual step in the Kipps dashboard — the trigger itself is programmatic, audience assignment is not.