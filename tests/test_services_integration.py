"""Integration tests for service layer + database (no HTTP)."""

import pytest

from app.database import SessionLocal
from app.models import Genre
from app.services import UserService, AuthorService, BookService


@pytest.fixture
def db_session(db_tables):
    """Real SQLAlchemy session against the test database."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_user_service_register_and_authenticate(db_session):
    service = UserService(db_session)

    # register new user
    user, err = service.register("integration_user", "secret123")
    assert err is None
    assert user.id is not None
    assert user.username == "integration_user"
    # password is hashed
    assert user.hashed_password != "secret123"

    # duplicate username
    user2, err2 = service.register("integration_user", "other")
    assert user2 is None
    assert err2 == "Username already exists"

    # authenticate success
    user_ok, auth_err = service.authenticate("integration_user", "secret123")
    assert auth_err is None
    assert user_ok.id == user.id

    # authenticate wrong password
    user_bad, auth_err_bad = service.authenticate("integration_user", "wrong")
    assert user_bad is None
    assert auth_err_bad == "invalid_password"

    # authenticate missing user
    user_missing, auth_err_missing = service.authenticate("no_such_user", "x")
    assert user_missing is None
    assert auth_err_missing == "user_not_found"


def test_author_and_book_lifecycle(db_session):
    user_service = UserService(db_session)
    author_service = AuthorService(db_session)
    book_service = BookService(db_session)

    # create user and author
    user, err = user_service.register("owner", "pw")
    assert err is None

    author_payload = {
        "id": 1,
        "name": "Integration Author",
        "bio": "Test bio",
        "country": "US",
    }
    author, err = author_service.create(author_payload)
    assert err is None
    assert author.id == 1

    # create book with genres
    book_payload = {
        "id": 10,
        "title": "Integration Book",
        "author_id": author.id,
        "isbn": "9780132350884",
        "published_year": 2020,
        "genres": ["Fiction", "Tech"],
    }
    book, err = book_service.create(book_payload, user)
    assert err is None
    assert book.id == 10
    assert book.author_id == author.id
    assert book.created_by_id == user.id
    assert {g.name for g in book.genres} == {"Fiction", "Tech"}

    # list and get
    books_all = book_service.list_all()
    assert len(books_all) == 1
    assert books_all[0].title == "Integration Book"

    books_by_author = book_service.list_all(author_id=author.id)
    assert len(books_by_author) == 1

    fetched = book_service.get_by_id(10)
    assert fetched is not None
    assert fetched.title == "Integration Book"

    # update book
    updated, err = book_service.update(10, {"title": "Updated Title", "genres": ["Updated"]})
    assert err is None
    assert updated.title == "Updated Title"
    assert {g.name for g in updated.genres} == {"Updated"}

    # delete book with correct owner
    ok, err = book_service.delete(10, user.id)
    assert ok is True
    assert err is None
    assert book_service.get_by_id(10) is None


def test_book_delete_forbidden_for_other_user(db_session):
    user_service = UserService(db_session)
    author_service = AuthorService(db_session)
    book_service = BookService(db_session)

    owner, err = user_service.register("owner2", "pw")
    assert err is None
    other, err = user_service.register("other2", "pw")
    assert err is None

    author, err = author_service.create({"id": 2, "name": "A", "bio": None, "country": None})
    assert err is None

    book_payload = {
        "id": 20,
        "title": "Owned Book",
        "author_id": author.id,
        "genres": [],
    }
    book, err = book_service.create(book_payload, owner)
    assert err is None
    assert book.created_by_id == owner.id

    # other user cannot delete
    ok, err = book_service.delete(20, other.id)
    assert ok is False
    assert err == "Forbidden"


def test_book_create_fails_when_author_missing(db_session):
    """BookService.create should fail if author_id does not exist."""
    user_service = UserService(db_session)
    book_service = BookService(db_session)

    user, err = user_service.register("no_author_user", "pw")
    assert err is None

    payload = {
        "id": 30,
        "title": "Orphan Book",
        "author_id": 9999,  # no such author
        "genres": [],
    }
    book, err = book_service.create(payload, user)
    assert book is None
    assert err == "Author with id 9999 not found"


def test_book_create_duplicate_id_or_isbn(db_session):
    """Creating a book with duplicate id should return integrity error message."""
    user_service = UserService(db_session)
    author_service = AuthorService(db_session)
    book_service = BookService(db_session)

    user, err = user_service.register("dup_user", "pw")
    assert err is None
    author, err = author_service.create({"id": 5, "name": "Author5", "bio": None, "country": None})
    assert err is None

    payload1 = {
        "id": 40,
        "title": "First",
        "author_id": author.id,
        "isbn": "9780132350884",
        "genres": [],
    }
    book, err = book_service.create(payload1, user)
    assert err is None
    assert book.id == 40

    # duplicate id
    payload_dup_id = {
        "id": 40,
        "title": "Second",
        "author_id": author.id,
        "isbn": "9780132350885",
        "genres": [],
    }
    book2, err2 = book_service.create(payload_dup_id, user)
    assert book2 is None
    assert err2 == "A book with this ID or ISBN already exists"


def test_book_update_nonexistent_book(db_session):
    """Updating a non-existing book should return 'Book not found'."""
    book_service = BookService(db_session)
    updated, err = book_service.update(9999, {"title": "Nope"})
    assert updated is None
    assert err == "Book not found"


def test_book_update_invalid_author_id(db_session):
    """Updating a book to reference a missing author should fail."""
    user_service = UserService(db_session)
    author_service = AuthorService(db_session)
    book_service = BookService(db_session)

    user, err = user_service.register("update_user", "pw")
    assert err is None
    author, err = author_service.create({"id": 6, "name": "Author6", "bio": None, "country": None})
    assert err is None

    book, err = book_service.create(
        {"id": 50, "title": "To Update", "author_id": author.id, "genres": []},
        user,
    )
    assert err is None

    updated, err = book_service.update(50, {"author_id": 9999})
    assert updated is None
    assert err == "Author with id 9999 not found"


def test_book_delete_not_found(db_session):
    """Deleting a non-existing book should return 'Book not found'."""
    book_service = BookService(db_session)
    ok, err = book_service.delete(9999, user_id=1)
    assert ok is False
    assert err == "Book not found"


def test_author_create_duplicate_id(db_session):
    """AuthorService.create should return an error when id already exists."""
    author_service = AuthorService(db_session)

    payload = {"id": 7, "name": "Author7", "bio": None, "country": None}
    author, err = author_service.create(payload)
    assert err is None
    assert author.id == 7

    author2, err2 = author_service.create(payload)
    assert author2 is None
    assert err2 == "Author with id 7 already added"


def test_genres_reused_between_books(db_session):
    """Same genre names should map to shared Genre rows, not duplicates."""
    user_service = UserService(db_session)
    author_service = AuthorService(db_session)
    book_service = BookService(db_session)

    user, err = user_service.register("genre_user", "pw")
    assert err is None
    author, err = author_service.create({"id": 8, "name": "Author8", "bio": None, "country": None})
    assert err is None

    payload_a = {
        "id": 60,
        "title": "Book A",
        "author_id": author.id,
        "genres": ["Fiction", "Sci-Fi"],
    }
    payload_b = {
        "id": 61,
        "title": "Book B",
        "author_id": author.id,
        "genres": ["Fiction", "Drama"],
    }

    book_a, err = book_service.create(payload_a, user)
    assert err is None
    book_b, err = book_service.create(payload_b, user)
    assert err is None

    # There should be exactly three distinct Genre rows
    genres = db_session.query(Genre).all()
    names = {g.name for g in genres}
    assert names == {"Fiction", "Sci-Fi", "Drama"}


