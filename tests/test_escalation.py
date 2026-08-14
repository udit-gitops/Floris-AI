"""
Unit tests for the escalation logic (app/services/escalation.py).
Run with: pytest tests/test_escalation.py -v

These need no DB, no server running — pure function tests. Good to
show judges: "here's proof the escalation rules actually work."
"""

from app.services.escalation import should_escalate


def test_no_escalation_below_threshold():
    result, reason = should_escalate(attempts_made=1, latest_transcript="sure, I'll check the docs")
    assert result is False
    assert reason is None


def test_escalates_on_retry_exhaustion():
    result, reason = should_escalate(attempts_made=2, latest_transcript="okay sounds good")
    assert result is True
    assert reason == "retry_exhaustion"


def test_escalates_on_red_flag_keyword():
    result, reason = should_escalate(attempts_made=0, latest_transcript="please stop calling me")
    assert result is True
    assert reason.startswith("red_flag_keyword")


def test_escalates_on_cannot_afford():
    result, reason = should_escalate(attempts_made=1, latest_transcript="I cannot afford this right now")
    assert result is True
    assert "red_flag_keyword" in reason


def test_case_insensitive_keyword_match():
    result, reason = should_escalate(attempts_made=0, latest_transcript="I want to COMPLAIN about this")
    assert result is True
