"""
SQLAlchemy engine + session factory.
Every DB-touching file imports `get_db` (a FastAPI dependency) from here
instead of creating its own connection — that's what keeps one connection
pool for the whole app instead of leaking connections.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency. Use like:
        def my_route(db: Session = Depends(get_db)):
    Guarantees the session is closed even if the request errors out.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
