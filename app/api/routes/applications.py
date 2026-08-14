"""
Read-side endpoints: fetching application/conversation state.
This is what Kipps' `get_application_status` function-call hits, and
what the dashboard polls for its live table.
"""

import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import Application
from app.models.conversation_state import ConversationState
from app.schemas.application import ApplicationStatusResponse, ApplicationSummary
from app.services.stall_detector import classify_stall

router = APIRouter(prefix="/applications", tags=["applications"])


def _find_application(db: Session, raw_loan_id: str) -> Application | None:
    """
    Voice/STT input is messy — customers or the agent may say "1001",
    "loan 1001", "loan_1001" instead of the exact "LOAN-1001" stored in
    the DB. Try an exact match first, then fall back to normalized
    variants before giving up. Keeps the demo resilient to voice
    transcription quirks without needing perfect prompt engineering.
    """
    # 1. Exact match
    app_row = db.query(Application).filter(Application.loan_id == raw_loan_id).first()
    if app_row:
        return app_row

    # 2. Extract digits only (handles "1001", "loan_1001", "loan 1001", etc.)
    digits = re.sub(r"\D", "", raw_loan_id)
    if digits:
        candidate = f"LOAN-{digits}"
        app_row = db.query(Application).filter(Application.loan_id == candidate).first()
        if app_row:
            return app_row

    # 3. Case-insensitive exact match as a last resort
    app_row = (
        db.query(Application).filter(Application.loan_id.ilike(raw_loan_id)).first()
    )
    return app_row


@router.get("/status", response_model=ApplicationStatusResponse)
def get_application_status(loan_id: str, db: Session = Depends(get_db)):
    """
    THE function Kipps Voice/Chat agents call before saying anything to
    the customer. Returns current stage, stall type, and — critically —
    last_summary + last_channel from conversation_state, which is what
    gives the agent continuity across channels.
    """
    app_row = _find_application(db, loan_id)
    if not app_row:
        raise HTTPException(
            status_code=404, detail=f"No application found for loan_id={loan_id}"
        )

    # Use the RESOLVED loan_id (app_row.loan_id) from here on, not the raw
    # input — e.g. customer said "1001", resolved to "LOAN-1001".
    state = (
        db.query(ConversationState)
        .filter(ConversationState.loan_id == app_row.loan_id)
        .first()
    )

    return ApplicationStatusResponse(
        loan_id=app_row.loan_id,
        customer_name=app_row.customer_name,
        stage=app_row.stage,
        stall_type=state.stall_type if state else None,
        status=state.status if state else "DETECTED",
        attempts_made=state.attempts_made if state else 0,
        last_channel=state.last_channel if state else None,
        last_summary=state.last_summary if state else None,
    )


@router.get("/stalled", response_model=List[ApplicationSummary])
def list_stalled_applications(db: Session = Depends(get_db)):
    """
    Powers the dashboard table. Re-classifies every application on each
    call (cheap at hackathon scale) rather than relying on a stale cached
    stall_type, so the dashboard always reflects current reality.
    """
    apps = db.query(Application).filter(Application.do_not_contact.is_(False)).all()

    results = []
    for app_row in apps:
        stall_type = classify_stall(app_row)
        if not stall_type:
            continue  # not stalled, skip

        state = (
            db.query(ConversationState)
            .filter(ConversationState.loan_id == app_row.loan_id)
            .first()
        )

        results.append(
            ApplicationSummary(
                loan_id=app_row.loan_id,
                customer_name=app_row.customer_name,
                stall_type=stall_type,
                status=state.status if state else "DETECTED",
                last_channel=state.last_channel if state else None,
                attempts_made=state.attempts_made if state else 0,
                updated_at=state.updated_at if state else None,
            )
        )

    return results
