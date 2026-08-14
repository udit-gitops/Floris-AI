"""
Pydantic schemas = the "shape" of data going in/out of the API.
These are DIFFERENT from the SQLAlchemy models in app/models/ on purpose:
models describe the database table, schemas describe the API contract.
Keeping them separate means you can change one without breaking the other.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ApplicationStatusResponse(BaseModel):
    """What the Kipps agent gets back when it calls get_application_status."""

    loan_id: str
    customer_name: str
    stage: str
    stall_type: Optional[str] = None
    status: str
    attempts_made: int
    last_channel: Optional[str] = None
    last_summary: Optional[str] = None

    class Config:
        from_attributes = True  # lets us build this directly from a SQLAlchemy row


class ApplicationSummary(BaseModel):
    """Row shape used by the dashboard table."""

    loan_id: str
    customer_name: str
    stall_type: Optional[str] = None
    status: str
    last_channel: Optional[str] = None
    attempts_made: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
