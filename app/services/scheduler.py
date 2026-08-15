import logging
from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.models.application import Application
from app.models.conversation_state import ConversationState
from app.services.stall_detector import classify_stall

logger = logging.getLogger("floris.scheduler")

SCAN_INTERVAL_MINUTES = 5


def scan_for_stalls():
    """
    One scan cycle: check every non-opted-out application, classify its
    stall status, and update conversation_state.stall_type if it just
    became stalled (or changed type). Applications with no state row yet
    get one created with status DETECTED.
    """
    db = SessionLocal()
    try:
        apps = db.query(Application).filter(Application.do_not_contact.is_(False)).all()
        newly_flagged = 0

        for app_row in apps:
            stall_type = classify_stall(app_row)
            if not stall_type:
                continue

            state = (
                db.query(ConversationState)
                .filter(ConversationState.loan_id == app_row.loan_id)
                .first()
            )
            if not state:
                state = ConversationState(
                    loan_id=app_row.loan_id,
                    stall_type=stall_type,
                    status="DETECTED",
                    attempts_made=0,
                )
                db.add(state)
                newly_flagged += 1
            elif state.stall_type != stall_type:
                state.stall_type = stall_type
                newly_flagged += 1

        db.commit()
        if newly_flagged:
            logger.info(
                f"[scheduler] Scan complete — {newly_flagged} application(s) newly flagged as stalled."
            )
        else:
            logger.info("[scheduler] Scan complete — no new stalls detected.")
    except Exception as e:
        logger.error(f"[scheduler] Scan failed: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    """
    Call once from app startup (see app/main.py). Runs scan_for_stalls()
    on a fixed interval in a background thread — doesn't block FastAPI's
    request handling.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        scan_for_stalls, "interval", minutes=SCAN_INTERVAL_MINUTES, id="stall_scan"
    )
    scheduler.start()
    logger.info(
        f"[scheduler] Started — scanning every {SCAN_INTERVAL_MINUTES} minutes."
    )
    return scheduler
