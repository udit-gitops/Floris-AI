"""
Run once to create all tables in PostgreSQL from the SQLAlchemy models.
Usage (from project root, venv active):
    python scripts/init_db.py

This is intentionally a raw create_all() rather than Alembic migrations
— for a hackathon timeline, migrations add ceremony you don't need.
If the schema needs to change later, just drop and re-run this (seed
data script will repopulate).
"""

import sys
import os

# Allow running this script directly (python scripts/init_db.py) by
# adding the project root to sys.path, since it's outside the app/ package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base_class import Base
from app.db.session import engine
from app import models  # noqa: F401  — import registers all models on Base.metadata


def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created:", list(Base.metadata.tables.keys()))


if __name__ == "__main__":
    init_db()
