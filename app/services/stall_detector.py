"""
Classify the current stall type for a loan application based on its
stage and time since the last customer activity.
"""

from datetime import datetime, timezone

from app.core.constants import (
    KYC_STALL_HOURS,
    PAYMENT_STALL_HOURS,
    SILENT_STALL_HOURS,
    STALL_TYPE_KYC,
    STALL_TYPE_PAYMENT,
    STALL_TYPE_SILENT,
)
from app.models.application import Application


def classify_stall(app: Application) -> str | None:
    """
    Return the applicable stall type, or None if the application is
    not stalled yet.
    """
    now = datetime.now(timezone.utc)
    last_activity = app.last_customer_activity_at
    if last_activity.tzinfo is None:
        last_activity = last_activity.replace(tzinfo=timezone.utc)

    hours_inactive = (now - last_activity).total_seconds() / 3600

    if app.stage == "KYC_UPLOAD" and hours_inactive >= KYC_STALL_HOURS:
        return STALL_TYPE_KYC

    if app.stage == "PAYMENT" and hours_inactive >= PAYMENT_STALL_HOURS:
        return STALL_TYPE_PAYMENT

    if hours_inactive >= SILENT_STALL_HOURS:
        return STALL_TYPE_SILENT

    return None
