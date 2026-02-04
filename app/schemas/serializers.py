"""Serialize domain models to API-friendly dicts."""
from typing import Any

from app.models import Author, Book


def book_to_dict(book: Book) -> dict[str, Any]:
    return {
        "id": book.id,
        "title": book.title,
        "author_id": book.author_id,
        "isbn": book.isbn,
        "published_year": book.published_year,
        "created_at": book.created_at.isoformat() if book.created_at else None,
        "genres": [g.name for g in book.genres],
    }


def author_to_dict(author: Author) -> dict[str, Any]:
    return {
        "id": author.id,
        "name": author.name,
        "bio": author.bio,
        "country": author.country,
    }
