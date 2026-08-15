"""
Write-side endpoints used by the Kipps agents to update recovery state:
logging contact attempts, escalating to a human, and recording channel
switches between Voice and Chat.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.constants import STATUS_CONTACTED, STATUS_ESCALATED
from app.db.session import get_db
from app.models.application import Application
from app.models.conversation_state import ConversationState
from app.models.human_queue import HumanQueueEntry
from app.schemas.actions import (
    SendRecoveryMessageRequest,
    SendRecoveryMessageResponse,
    EscalateRequest,
    EscalateResponse,
    LogChannelSwitchRequest,
    LogChannelSwitchResponse,
)
from app.services.escalation import should_escalate
from app.api.routes.applications import _find_application

router = APIRouter(tags=["actions"])


def _get_or_create_state(db: Session, loan_id: str) -> ConversationState:
    """Get the conversation state for a normalized loan ID, creating it if needed."""
    state = (
        db.query(ConversationState).filter(ConversationState.loan_id == loan_id).first()
    )
    if not state:
        state = ConversationState(loan_id=loan_id, attempts_made=0, status="DETECTED")
        db.add(state)
        db.flush()
    return state


def _auto_escalate_if_needed(
    db: Session, loan_id: str, state: ConversationState
) -> None:
    """Check whether the latest recovery attempt should trigger escalation."""
    escalate_needed, reason = should_escalate(state.attempts_made, latest_transcript="")
    if escalate_needed:
        state.status = STATUS_ESCALATED
        queue_entry = HumanQueueEntry(
            loan_id=loan_id,
            reason=reason or "retry_exhaustion",
            context_summary=(
                f"Auto-escalated after {state.attempts_made} attempts via "
                f"{state.last_channel}. Last summary: {state.last_summary}"
            ),
        )
        db.add(queue_entry)


@router.post("/send_recovery_message", response_model=SendRecoveryMessageResponse)
def send_recovery_message(
    payload: SendRecoveryMessageRequest, db: Session = Depends(get_db)
):
    """Escalate an application and add the full context to the human queue."""
    app_row = _find_application(db, payload.loan_id)
    if not app_row:
        raise HTTPException(
            status_code=404,
            detail=f"No application found for loan_id={payload.loan_id}",
        )

    resolved_loan_id = app_row.loan_id  # e.g. "2001" -> "LOAN-2001"

    state = _get_or_create_state(db, resolved_loan_id)
    state.attempts_made += 1
    state.last_channel = payload.channel
    state.last_summary = payload.message_summary
    state.status = STATUS_CONTACTED

    _auto_escalate_if_needed(db, resolved_loan_id, state)

    db.commit()
    db.refresh(state)

    return SendRecoveryMessageResponse(
        ok=True, attempts_made=state.attempts_made, status=state.status
    )


@router.post("/escalate", response_model=EscalateResponse)
def escalate(payload: EscalateRequest, db: Session = Depends(get_db)):
    """
    Called either by the agent directly (it detected a red flag) or
    by your own logic after send_recovery_message exhausts retries.
    Writes a FULL-context row to human_queue — not just "escalated".
    """
    app_row = _find_application(db, payload.loan_id)
    if not app_row:
        raise HTTPException(
            status_code=404,
            detail=f"No application found for loan_id={payload.loan_id}",
        )

    resolved_loan_id = app_row.loan_id

    state = _get_or_create_state(db, resolved_loan_id)
    state.status = STATUS_ESCALATED

    queue_entry = HumanQueueEntry(
        loan_id=resolved_loan_id,
        reason=payload.reason,
        context_summary=payload.context_summary,
    )
    db.add(queue_entry)
    db.commit()
    db.refresh(queue_entry)

    return EscalateResponse(ok=True, human_queue_id=queue_entry.id, status=state.status)


@router.post("/log_channel_switch", response_model=LogChannelSwitchResponse)
def log_channel_switch(payload: LogChannelSwitchRequest, db: Session = Depends(get_db)):
    """Record a channel switch and preserve the conversation summary for continuity."""

    app_row = _find_application(db, payload.loan_id)
    if not app_row:
        raise HTTPException(
            status_code=404,
            detail=f"No application found for loan_id={payload.loan_id}",
        )

    resolved_loan_id = app_row.loan_id

    state = _get_or_create_state(db, resolved_loan_id)
    state.last_channel = payload.new_channel
    state.last_summary = payload.summary_so_far

    db.commit()
    db.refresh(state)

    return LogChannelSwitchResponse(ok=True, last_summary=state.last_summary)
