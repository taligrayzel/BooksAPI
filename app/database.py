"""Database connection and session management."""
import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Keep aligned with alembic.ini (sqlalchemy.url)
_DEFAULT_URL = "postgresql+psycopg2://postgres:password@localhost:5432/my_project_db"
DATABASE_URL = os.environ.get("DATABASE_URL", _DEFAULT_URL)

_connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def session_scope():
    """Provide a transactional scope: commit on success, rollback on exception, always close."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
