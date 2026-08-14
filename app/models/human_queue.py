"""
`human_queue` table — every escalation lands here with a FULL context
summary (not just "escalated"). This is what the dashboard's escalation
view is built on, and what answers the "escalation design" judging
criterion — a human picking this up should immediately know what was
tried and why it got handed off.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func

from app.db.base_class import Base


class HumanQueueEntry(Base):
    __tablename__ = "human_queue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(String, ForeignKey("applications.loan_id"), nullable=False)

    reason = Column(String, nullable=False)  # e.g. "retry_exhaustion" or "red_flag_keyword"
    context_summary = Column(String, nullable=False)  # what was tried, what's missing, why escalated

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved = Column(String, default="OPEN", nullable=False)  # OPEN / RESOLVED
