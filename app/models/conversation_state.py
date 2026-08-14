"""
`conversation_state` table — THIS is the dual-channel differentiator.
Both the Voice agent and the Chat agent read/write this same row before
responding, so a customer who talks to Voice today and opens Chat
tomorrow gets continuity instead of a cold start.

One row per loan_id (1:1 with applications, kept as a separate table
on purpose — applications is "what the loan is", this is "what the
conversation has been" — different concerns, different lifecycle).
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func

from app.db.base_class import Base


class ConversationState(Base):
    __tablename__ = "conversation_state"

    loan_id = Column(String, ForeignKey("applications.loan_id"), primary_key=True)

    last_channel = Column(String, nullable=True)  # 'voice' or 'chat'
    last_summary = Column(String, nullable=True)  # what was discussed last, in plain text
    attempts_made = Column(Integer, default=0, nullable=False)

    stall_type = Column(String, nullable=True)  # KYC_PENDING / PAYMENT_PENDING / GONE_SILENT
    status = Column(String, nullable=False, default="DETECTED")
    # DETECTED / CONTACTED / RECOVERED / ESCALATED / ABANDONED

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
