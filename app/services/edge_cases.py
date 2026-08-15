"""
Edge-case guardrails for contact attempts:
- Respect the do-not-disturb window.
- Prevent duplicate contact attempts while one is active.
"""

from datetime import datetime

from app.core.constants import DND_START_HOUR, DND_END_HOUR, STATUS_CONTACTED


def is_within_dnd_hours(now: datetime | None = None) -> bool:
    """
    Return True when the current time falls within the 8 PM to 9 AM
    do-not-disturb window.
    """
    now = now or datetime.now()
    hour = now.hour
    return hour >= DND_START_HOUR or hour < DND_END_HOUR


def is_locked_for_contact(current_status: str) -> bool:
    """
    Return True when a contact attempt is already in progress or awaiting
    a response.
    """
    return current_status == STATUS_CONTACTED
