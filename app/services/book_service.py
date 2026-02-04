"""Book business logic."""
import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Author, Book, Genre


class BookService:
    def __init__(self, session: Session):
        self._session = session

    def _get_or_create_genres(self, genre_names: list[str]) -> list:
        result = []
        for name in genre_names:
            name = name.strip()
            genre = self._session.query(Genre).filter_by(name=name).first()
            if genre is None:
                genre = Genre(name=name)
                self._session.add(genre)
            result.append(genre)
        return result

    def create(self, payload: dict, current_user) -> tuple:
        """Returns (book, None) or (None, error_message)."""
        author = self._session.get(Author, payload["author_id"])
        if author is None:
            return None, f"Author with id {payload['author_id']} not found"

        genre_objects = self._get_or_create_genres(payload.get("genres", []))

        try:
            book = Book(
                id=payload["id"],
                title=payload["title"],
                author_id=payload["author_id"],
                isbn=payload.get("isbn"),
                published_year=payload.get("published_year"),
                created_at=datetime.datetime.today(),
                created_by=current_user,
                genres=genre_objects,
            )
            self._session.add(book)
            self._session.commit()
            return book, None
        except IntegrityError:
            self._session.rollback()
            return None, "A book with this ID or ISBN already exists"

    def list_all(self, author_id: int | None = None) -> list:
        q = self._session.query(Book)
        if author_id is not None:
            q = q.filter(Book.author_id == author_id)
        return q.all()

    def get_by_id(self, book_id: int):
        return self._session.get(Book, book_id)

    def update(self, book_id: int, payload: dict) -> tuple:
        """Returns (book, None) or (None, error_message)."""
        book = self._session.get(Book, book_id)
        if book is None:
            return None, "Book not found"

        if "author_id" in payload:
            author = self._session.get(Author, payload["author_id"])
            if author is None:
                return None, f"Author with id {payload['author_id']} not found"
            book.author_id = author.id

        if "title" in payload:
            book.title = payload["title"]
        if "isbn" in payload:
            book.isbn = payload["isbn"]
        if "published_year" in payload:
            book.published_year = payload["published_year"]
        if "genres" in payload:
            book.genres = self._get_or_create_genres(payload["genres"])

        try:
            self._session.commit()
            return book, None
        except IntegrityError:
            self._session.rollback()
            return None, "Database integrity error"

    def delete(self, book_id: int, current_user) -> tuple:
        """Returns (True, None) or (False, error_message)."""
        book = self._session.get(Book, book_id)
        if book is None:
            return False, "Book not found"
        if book.created_by != current_user:
            return False, "Forbidden"
        self._session.delete(book)
        self._session.commit()
        return True, None
