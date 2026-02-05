"""Pytest fixtures for API tests."""
import os

# Set test env before any app import
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
import httpx
from sqlalchemy import text

# Import after env is set
from app.main import app
from app.database import engine
from app.models import Base

# Tables to clear (order: FK dependencies first)
_CLEAN_TABLES = ["book_genre", "books", "authors", "genres", "users", "tasks"]


def _clean_db():
    with engine.connect() as conn:
        with conn.begin():
            for table in _CLEAN_TABLES:
                try:
                    conn.execute(text(f"DELETE FROM {table}"))
                except Exception:
                    pass


@pytest.fixture(scope="session")
def _setup_db():
    """Create tables once per test session."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_tables(_setup_db):
    """Ensure DB is set up and clean before each test."""
    _clean_db()
    yield


@pytest.fixture
def client(db_tables):
    """HTTP client using httpx against the Flask app (WSGI)."""
    transport = httpx.WSGITransport(app=app)
    with httpx.Client(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """Register a user, login, return headers with Bearer token."""
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    r = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def author_id(client, auth_headers):
    """Create one author and return its id."""
    r = client.post(
        "/authors",
        json={"id": 1, "name": "Test Author", "bio": "Bio", "country": "US"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    return 1
