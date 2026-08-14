"""
App entrypoint. Run with: uvicorn app.main:app --reload

This file's ONLY job is to create the FastAPI app and wire routers in.
No business logic lives here — that's deliberate, so a judge (or you,
at 2 AM on Aug 15) can see the whole API surface by reading this one
file top to bottom.
"""

from fastapi import FastAPI

from app.api.routes import applications, actions, dashboard
from app.core.config import settings

app = FastAPI(
    title="Floris AI",
    description="Autonomous workflow recovery agent — Kipps.AI Hackathon 2026",
    version="0.1.0",
)

# Routers — each file in app/api/routes/ owns one concern
app.include_router(applications.router)
app.include_router(actions.router)
app.include_router(dashboard.router)


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
