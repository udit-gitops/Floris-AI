from fastapi import FastAPI

from app.api.routes import applications, actions, dashboard
from app.core.config import settings
from app.services.scheduler import start_scheduler

app = FastAPI(
    title="Floris AI",
    description="Autonomous workflow recovery agent — Kipps.AI Hackathon 2026",
    version="0.1.0",
)

# Routers — each file in app/api/routes/ owns one concern
app.include_router(applications.router)
app.include_router(actions.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def on_startup():
    """
    Starts the background stall-scanner when the app boots — this is
    what makes stall detection continuous/autonomous instead of only
    running when someone happens to hit /applications/stalled.
    """
    start_scheduler()


@app.get("/")
def root():
    return {
        "service": "Floris AI",
        "env": settings.APP_ENV,
        "docs": "/docs",
        "dashboard": "/dashboard",
    }


@app.get("/health")
def health():
    """Simple liveness check — useful when demoing to prove backend is up."""
    return {"status": "ok"}
