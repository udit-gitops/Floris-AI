"""
`applications` table — one row per loan application Floris AI is tracking.
This is the "source of truth" for who the customer is and where their
loan currently stands. The stall detector reads this table to decide
who needs a recovery attempt.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, func

from app.db.base_class import Base


class Application(Base):
    __tablename__ = "applications"

    loan_id = Column(String, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)

    # Where the application currently sits (drives which stall-type applies)
    stage = Column(String, nullable=False)  # e.g. "KYC_UPLOAD", "PAYMENT", "SUBMITTED"
    loan_amount = Column(Integer, nullable=True)

    # Timestamps used by the stall detector to compute inactivity
    application_started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_customer_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    # Edge-case flags (Section 5 of the plan)
    do_not_contact = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
