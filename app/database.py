"""Database connection and session management."""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Keep aligned with alembic.ini (sqlalchemy.url)
DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/my_project_db"

engine = create_engine(DATABASE_URL, echo=False, future=True)
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
