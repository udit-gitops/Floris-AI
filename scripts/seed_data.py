"""
Seeds 8 fake loan applications covering all 3 stall types, so you have
data to demo against immediately after init_db.py runs.

Usage (from project root, venv active):
    python scripts/seed_data.py

Timestamps are backdated deliberately so each row is ALREADY past its
stall threshold (see app/core/constants.py) the moment you seed it —
no waiting around for real time to pass during dev/demo.
"""

import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.application import Application

NOW = datetime.now(timezone.utc)

SEED_APPLICATIONS = [
    # --- Type A: KYC Pending (stage=KYC_UPLOAD, inactive 48h+) ---
    dict(
        loan_id="LOAN-1001",
        customer_name="Ravi Sharma",
        phone_number="+911234567001",
        stage="KYC_UPLOAD",
        loan_amount=250000,
        last_customer_activity_at=NOW - timedelta(hours=60),
    ),
    dict(
        loan_id="LOAN-1002",
        customer_name="Priya Nair",
        phone_number="+911234567002",
        stage="KYC_UPLOAD",
        loan_amount=180000,
        last_customer_activity_at=NOW - timedelta(hours=72),
    ),
    dict(
        loan_id="LOAN-1003",
        customer_name="Amit Verma",
        phone_number="+911234567003",
        stage="KYC_UPLOAD",
        loan_amount=500000,
        last_customer_activity_at=NOW - timedelta(hours=50),
    ),
    # --- Type B: Payment Pending (stage=PAYMENT, inactive 72h+) ---
    dict(
        loan_id="LOAN-2001",
        customer_name="Sneha Kulkarni",
        phone_number="+911234567004",
        stage="PAYMENT",
        loan_amount=320000,
        last_customer_activity_at=NOW - timedelta(hours=80),
    ),
    dict(
        loan_id="LOAN-2002",
        customer_name="Vikram Singh",
        phone_number="+911234567005",
        stage="PAYMENT",
        loan_amount=150000,
        last_customer_activity_at=NOW - timedelta(hours=100),
    ),
    dict(
        loan_id="LOAN-2003",
        customer_name="Anjali Deshmukh",
        phone_number="+911234567006",
        stage="PAYMENT",
        loan_amount=275000,
        last_customer_activity_at=NOW - timedelta(hours=75),
    ),
    # --- Type C: Gone Silent (any stage, inactive 120h+ / 5 days) ---
    dict(
        loan_id="LOAN-3001",
        customer_name="Karan Mehta",
        phone_number="+911234567007",
        stage="SUBMITTED",
        loan_amount=400000,
        last_customer_activity_at=NOW - timedelta(hours=140),
    ),
    dict(
        loan_id="LOAN-3002",
        customer_name="Neha Joshi",
        phone_number="+911234567008",
        stage="SUBMITTED",
        loan_amount=220000,
        last_customer_activity_at=NOW - timedelta(hours=150),
    ),
    # --- Control row: NOT stalled (recent activity, should NOT show on dashboard) ---
    dict(
        loan_id="LOAN-9999",
        customer_name="Test Fresh Applicant",
        phone_number="+911234567099",
        stage="KYC_UPLOAD",
        loan_amount=100000,
        last_customer_activity_at=NOW - timedelta(hours=2),
    ),
]


def seed():
    db = SessionLocal()
    try:
        existing = {row.loan_id for row in db.query(Application.loan_id).all()}
        inserted = 0
        for record in SEED_APPLICATIONS:
            if record["loan_id"] in existing:
                continue
            db.add(Application(**record))
            inserted += 1
        db.commit()
        print(f"Seeded {inserted} new applications (skipped {len(SEED_APPLICATIONS) - inserted} already present).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
