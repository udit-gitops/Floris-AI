"""
Serves the mini dashboard HTML page (Section 7 of the plan). The page
itself polls /applications/stalled every 5s via JS fetch — this route
just renders the initial shell, it doesn't push data server-side.
"""

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.kipps_client import trigger_recovery_call

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.post("/trigger_call")
def trigger_call(loan_id: str, db: Session = Depends(get_db)):
    """
    Dispatches an outbound recovery call for one specific stalled
    application via Kipps' documented campaign webhook — see
    app/services/kipps_client.py.
    """
    return trigger_recovery_call(loan_id, db)
