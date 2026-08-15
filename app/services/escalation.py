"""
Escalation decision logic kept independent of database andd HTTP dependencies.
"""

from app.core.constants import MAX_AUTO_ATTEMPTS, RED_FLAG_KEYWORDS


def should_escalate(
    attempts_made: int, latest_transcript: str = ""
) -> tuple[bool, str | None]:
    """
    Return whether the application should be escalated and the reason.

    Escalation occurs when the maximum number of automatic attempts has
    been reached or a red-flag keyword is detected in the latest transcript.
    """
    if attempts_made >= MAX_AUTO_ATTEMPTS:
        return True, "retry_exhaustion"

    lowered = latest_transcript.lower()
    for flag in RED_FLAG_KEYWORDS:
        if flag in lowered:
            return True, f"red_flag_keyword:{flag}"

    return False, None
