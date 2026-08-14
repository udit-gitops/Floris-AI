"""
Edge-case guardrails from Section 5 of the plan. Each one is a small
pure function so they can be tested and explained individually:
  - is_within_dnd_hours: don't call 8 PM - 9 AM
  - is_locked_for_contact: don't double-call while one attempt is in progress
Opt-out (do_not_contact) is checked directly on the Application row
wherever a contact attempt is triggered — no separate function needed
since it's a single boolean field read.
"""

from datetime import datetime

from app.core.constants import DND_START_HOUR, DND_END_HOUR, STATUS_CONTACTED


def is_within_dnd_hours(now: datetime | None = None) -> bool:
    """
    DND window is 8 PM (20:00) to 9 AM (09:00) — wraps past midnight,
    so we can't just check start <= hour <= end.
    """
    now = now or datetime.now()
    hour = now.hour
    return hour >= DND_START_HOUR or hour < DND_END_HOUR


def is_locked_for_contact(current_status: str) -> bool:
    """
    Prevents triggering a second outbound attempt while one is already
    'CONTACTED' (i.e. a call/chat is actively in progress or awaiting
    a response). Acts as the duplicate-call prevention lock from the plan.
    """
    return current_status == STATUS_CONTACTED
