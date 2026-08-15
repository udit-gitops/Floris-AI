from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.kipps_client import trigger_recovery_campaign

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.post("/trigger_campaign")
def trigger_campaign():
    """
    Manually dispatches the Kipps recovery campaign — see
    app/services/kipps_client.py for important context on how this
    endpoint was discovered and its reliability caveats.
    """
    return trigger_recovery_campaign()
