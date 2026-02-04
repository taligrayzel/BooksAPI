"""Author business logic."""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Author


class AuthorService:
    def __init__(self, session: Session):
        self._session = session

    def create(self, payload: dict) -> tuple:
        """Returns (author, None) or (None, error_message)."""
        existing = self._session.get(Author, payload["id"])
        if existing is not None:
            return None, f"Author with id {payload['id']} already added"

        try:
            author = Author(
                id=payload["id"],
                name=payload["name"],
                bio=payload.get("bio"),
                country=payload.get("country"),
            )
            self._session.add(author)
            self._session.commit()
            return author, None
        except IntegrityError:
            self._session.rollback()
            return None, "Author already exists"

    def get_with_books(self, author_id: int):
        return (
            self._session.query(Author)
            .options(joinedload(Author.books))
            .filter(Author.id == author_id)
            .first()
        )
