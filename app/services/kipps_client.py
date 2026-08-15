"""
Client for Kipps' outbound campaign webhook — an OFFICIALLY DOCUMENTED
trigger.
Sending a POST here with a valid phone number dispatches that specific
lead into the connected outbound campaign flow.
"""

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.application import Application


def _split_name(full_name: str) -> tuple[str, str]:
    """Best-effort split of 'Ravi Sharma' into ('Ravi', 'Sharma')."""
    parts = full_name.strip().split(maxsplit=1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0] if parts else "", ""


def trigger_recovery_call(loan_id: str, db: Session) -> dict:
    """
    Looks up the application by loan_id and sends its contact details
    to Kipps' campaign webhook, dispatching an outbound recovery call
    for that specific customer.
    """
    if not (settings.KIPPS_WEBHOOK_URL and settings.KIPPS_WEBHOOK_SECRET):
        return {"ok": False, "error": "Kipps webhook not configured (missing env vars)"}

    app_row = db.query(Application).filter(Application.loan_id == loan_id).first()
    if not app_row:
        return {"ok": False, "error": f"No application found for loan_id={loan_id}"}

    first_name, last_name = _split_name(app_row.customer_name)
    payload = {
        "phone": app_row.phone_number,
        "first_name": first_name,
        "last_name": last_name,
    }
    headers = {
        "X-Webhook-Secret": settings.KIPPS_WEBHOOK_SECRET,
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(
            settings.KIPPS_WEBHOOK_URL, json=payload, headers=headers, timeout=15
        )
        response.raise_for_status()
        return {"ok": True, "status_code": response.status_code, "loan_id": loan_id}
    except httpx.HTTPStatusError as e:
        return {
            "ok": False,
            "error": f"Kipps returned {e.response.status_code}: {e.response.text}",
        }
    except httpx.RequestError as e:
        return {"ok": False, "error": f"Request to Kipps failed: {e}"}
