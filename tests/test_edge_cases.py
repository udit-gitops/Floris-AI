"""
Unit tests for edge-case guardrails (app/services/edge_cases.py).
Run with: pytest tests/test_edge_cases.py -v
"""

from datetime import datetime

from app.services.edge_cases import is_within_dnd_hours, is_locked_for_contact


def test_dnd_true_at_night():
    assert is_within_dnd_hours(datetime(2026, 8, 12, 22, 0)) is True  # 10 PM


def test_dnd_true_early_morning():
    assert is_within_dnd_hours(datetime(2026, 8, 12, 6, 0)) is True  # 6 AM


def test_dnd_false_during_day():
    assert is_within_dnd_hours(datetime(2026, 8, 12, 14, 0)) is False  # 2 PM


def test_dnd_boundary_9am_is_allowed():
    assert is_within_dnd_hours(datetime(2026, 8, 12, 9, 0)) is False


def test_dnd_boundary_8pm_is_blocked():
    assert is_within_dnd_hours(datetime(2026, 8, 12, 20, 0)) is True


def test_locked_when_contacted():
    assert is_locked_for_contact("CONTACTED") is True


def test_not_locked_when_detected():
    assert is_locked_for_contact("DETECTED") is False
