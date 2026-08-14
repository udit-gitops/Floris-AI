"""
Importing every model here means a single `from app.models import *`
(used in scripts/init_db.py) registers all tables with Base.metadata.
Without this, SQLAlchemy won't know a model exists unless it's been
imported somewhere in the run.
"""

from app.models.application import Application  # noqa: F401
from app.models.conversation_state import ConversationState  # noqa: F401
from app.models.human_queue import HumanQueueEntry  # noqa: F401
