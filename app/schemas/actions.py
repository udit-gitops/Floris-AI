"""
Request/response schemas for the 4 function-calling endpoints that
Kipps Voice and Chat agents call:
  - get_application_status
  - send_recovery_message
  - escalate
  - log_channel_switch

These field names matter — they become the "parameters" Kipps'
Function Calling UI expects, so keep them descriptive and stable
once you wire them into the agent dashboard.
"""

from typing import Optional

from pydantic import BaseModel


class SendRecoveryMessageRequest(BaseModel):
    loan_id: str
    channel: str  # 'voice' or 'chat'
    message_summary: str  # what the agent said/is about to say, in plain text


class SendRecoveryMessageResponse(BaseModel):
    ok: bool
    attempts_made: int
    status: str


class EscalateRequest(BaseModel):
    loan_id: str
    reason: str  # 'retry_exhaustion' or 'red_flag_keyword'
    context_summary: str
    transcript_snippet: Optional[str] = None


class EscalateResponse(BaseModel):
    ok: bool
    human_queue_id: int
    status: str


class LogChannelSwitchRequest(BaseModel):
    loan_id: str
    new_channel: str  # channel the customer just switched to
    summary_so_far: str  # what the OTHER channel discussed, for continuity


class LogChannelSwitchResponse(BaseModel):
    ok: bool
    last_summary: str
