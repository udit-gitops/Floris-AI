"""
Serves the mini dashboard HTML page (Section 7 of the plan). The page
itself polls /applications/stalled every 5s via JS fetch — this route
just renders the initial shell, it doesn't push data server-side.
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
