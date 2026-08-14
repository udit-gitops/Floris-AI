"""
Shared declarative Base. Every model in app/models/ inherits from this
`Base` so that Alembic (migrations) and SQLAlchemy's metadata can see
all tables in one place.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
