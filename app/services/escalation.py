"""
Escalation decision logic — deliberately kept as a pure function with
no DB/HTTP dependencies. This means:
  1. You can unit-test it directly (see tests/test_escalation.py)
  2. You can explain it to a judge by pointing at ONE function
  3. Routes just call this and act on the result — no logic duplication
"""

from app.core.constants import MAX_AUTO_ATTEMPTS, RED_FLAG_KEYWORDS


def should_escalate(attempts_made: int, latest_transcript: str = "") -> tuple[bool, str | None]:
    """
    Returns (should_escalate: bool, reason: str | None)

    Trigger 1 — retry exhaustion: MAX_AUTO_ATTEMPTS reached with no recovery.
    Trigger 2 — red-flag keyword/sentiment signal in the latest transcript.
    Either trigger alone is sufficient — they are NOT combined with AND.
    """
    if attempts_made >= MAX_AUTO_ATTEMPTS:
        return True, "retry_exhaustion"

    lowered = latest_transcript.lower()
    for flag in RED_FLAG_KEYWORDS:
        if flag in lowered:
            return True, f"red_flag_keyword:{flag}"

    return False, None
