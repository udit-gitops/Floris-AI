"""
Read-side endpoints for fetching application and conversation state.
Used by Kipps agents to retrieve recovery context and by the dashboard
to display the current state of stalled applications.
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
    Resolve a loan ID from exact, normalized, or case-insensitive input.
    This also handles variations that can occur with voice transcription.
    """
    # Try the exact loan ID first.
    app_row = db.query(Application).filter(Application.loan_id == raw_loan_id).first()
    if app_row:
        return app_row

    # Extract digits to handle inputs such as "1001", "loan 1001", or "loan_1001".
    digits = re.sub(r"\D", "", raw_loan_id)
    if digits:
        candidate = f"LOAN-{digits}"
        app_row = db.query(Application).filter(Application.loan_id == candidate).first()
        if app_row:
            return app_row

    # Fall back to a case-insensitive match.
    app_row = (
        db.query(Application).filter(Application.loan_id.ilike(raw_loan_id)).first()
    )
    return app_row


@router.get("/status", response_model=ApplicationStatusResponse)
def get_application_status(loan_id: str, db: Session = Depends(get_db)):
    """
    Return the current application and conversation state used by
    Kipps Voice and Chat agents to maintain continuity.
    """
    app_row = _find_application(db, loan_id)
    if not app_row:
        raise HTTPException(
            status_code=404, detail=f"No application found for loan_id={loan_id}"
        )

    # Use the resolved loan ID for all subsequent state lookups.
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
    Return currently stalled applications for the dashboard.
    Stall types are calculated from the latest application data.
    """
    apps = db.query(Application).filter(Application.do_not_contact.is_(False)).all()

    results = []
    for app_row in apps:
        stall_type = classify_stall(app_row)
        if not stall_type:
            continue

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
