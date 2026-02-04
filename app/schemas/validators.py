"""Validation logic for API payloads."""
import datetime
from typing import Optional, Tuple


def _non_empty_str(value, field: str, max_len: int) -> Tuple[bool, Optional[str]]:
    if value is None:
        return False, f"Field '{field}' is required"
    if not isinstance(value, str) or not value.strip():
        return False, f"Field '{field}' must be a non-empty string"
    if len(value) > max_len:
        return False, f"Field '{field}' must not exceed {max_len} characters"
    return True, None


def validate_isbn(isbn: Optional[str]) -> bool:
    if not isbn:
        return True
    clean = isbn.replace("-", "").replace(" ", "")
    if len(clean) not in (10, 13):
        return False
    return clean.isdigit() or (len(clean) == 10 and clean[-1].upper() == "X")


def validate_published_year(year: Optional[int]) -> bool:
    if year is None:
        return True
    current = datetime.datetime.now().year
    return isinstance(year, int) and year <= current + 1


def validate_book_create(data: dict) -> Tuple[bool, Optional[str], Optional[dict]]:
    if not data:
        return False, "Request body must be JSON", None

    book_id = data.get("id")
    if book_id is None:
        return False, "Field 'id' is required", None
    if not isinstance(book_id, int):
        return False, "Field 'id' must be an integer", None

    ok, err = _non_empty_str(data.get("title"), "title", 255)
    if not ok:
        return False, err, None
    title = data.get("title", "").strip()

    author_id = data.get("author_id")
    if author_id is None:
        return False, "Field 'author_id' is required", None
    if not isinstance(author_id, int):
        return False, "Field 'author_id' must be an integer", None

    isbn = data.get("isbn")
    if isbn is not None:
        if not isinstance(isbn, str):
            return False, "Field 'isbn' must be a string", None
        if not validate_isbn(isbn):
            return False, "Field 'isbn' must be a valid ISBN-10 or ISBN-13 format", None
        if len(isbn) > 20:
            return False, "Field 'isbn' must not exceed 20 characters", None

    year = data.get("published_year")
    if year is not None:
        if not isinstance(year, int):
            return False, "Field 'published_year' must be an integer", None
        if not validate_published_year(year):
            y = datetime.datetime.now().year
            return False, f"Field 'published_year' must be between 1000 and {y + 1}", None

    genres = data.get("genres", [])
    if not isinstance(genres, list):
        return False, "Field 'genres' must be a list", None
    for g in genres:
        if not isinstance(g, str) or not g.strip():
            return False, "Each genre must be a non-empty string", None

    return True, None, {
        "id": book_id,
        "title": title,
        "author_id": author_id,
        "isbn": isbn,
        "published_year": year,
        "genres": genres,
    }


def validate_book_update(data: dict) -> Tuple[bool, Optional[str], Optional[dict]]:
    if not data:
        return False, "Request body must be JSON", None

    title = data.get("title")
    author_id = data.get("author_id")
    isbn = data.get("isbn")
    published_year = data.get("published_year")
    genres = data.get("genres")

    if all(v is None for v in [title, author_id, isbn, published_year, genres]):
        return False, "At least one field must be provided for update", None

    if title is not None:
        ok, err = _non_empty_str(title, "title", 255)
        if not ok:
            return False, err, None
    if author_id is not None and not isinstance(author_id, int):
        return False, "Field 'author_id' must be an integer", None
    if isbn is not None:
        if not isinstance(isbn, str):
            return False, "Field 'isbn' must be a string", None
        if not validate_isbn(isbn):
            return False, "Field 'isbn' must be a valid ISBN-10 or ISBN-13 format", None
        if len(isbn) > 20:
            return False, "Field 'isbn' must not exceed 20 characters", None
    if published_year is not None:
        if not isinstance(published_year, int):
            return False, "Field 'published_year' must be an integer", None
        if not validate_published_year(published_year):
            y = datetime.datetime.now().year
            return False, f"Field 'published_year' must be between 1000 and {y + 1}", None
    if genres is not None:
        if not isinstance(genres, list):
            return False, "Field 'genres' must be a list", None
        for g in genres:
            if not isinstance(g, str) or not g.strip():
                return False, "Each genre must be a non-empty string", None

    payload = {}
    if title is not None:
        payload["title"] = title.strip()
    if author_id is not None:
        payload["author_id"] = author_id
    if isbn is not None:
        payload["isbn"] = isbn
    if published_year is not None:
        payload["published_year"] = published_year
    if genres is not None:
        payload["genres"] = genres

    return True, None, payload


def validate_author_create(data: dict) -> Tuple[bool, Optional[str], Optional[dict]]:
    if not data:
        return False, "Request body must be JSON", None

    author_id = data.get("id")
    if author_id is None:
        return False, "Field 'id' is required", None
    if not isinstance(author_id, int):
        return False, "Field 'id' must be an integer", None

    ok, err = _non_empty_str(data.get("name"), "name", 255)
    if not ok:
        return False, err, None

    bio = data.get("bio")
    if bio is not None:
        ok, err = _non_empty_str(bio, "bio", 1000)
        if not ok:
            return False, err, None
    country = data.get("country")
    if country is not None:
        ok, err = _non_empty_str(country, "country", 100)
        if not ok:
            return False, err, None

    return True, None, {
        "id": author_id,
        "name": data.get("name", "").strip(),
        "bio": bio,
        "country": country,
    }


def validate_register(data: dict) -> Tuple[bool, Optional[str], Optional[dict]]:
    if not data:
        return False, "Request body must be JSON", None

    ok, err = _non_empty_str(data.get("username"), "username", 100)
    if not ok:
        return False, err, None
    ok, err = _non_empty_str(data.get("password"), "password", 255)
    if not ok:
        return False, err, None

    return True, None, {
        "username": data.get("username", "").strip(),
        "password": data.get("password", "").strip(),
    }


def validate_login(data: dict) -> Tuple[bool, Optional[str], Optional[dict]]:
    if not data:
        return False, "Request body must be JSON", None

    ok, err = _non_empty_str(data.get("username"), "username", 100)
    if not ok:
        return False, err, None
    ok, err = _non_empty_str(data.get("password"), "password", 255)
    if not ok:
        return False, err, None

    return True, None, {
        "username": data.get("username", "").strip(),
        "password": data.get("password", "").strip(),
    }


def parse_author_id_query(value: Optional[str]) -> Tuple[bool, Optional[str], Optional[int]]:
    if value is None:
        return True, None, None
    try:
        return True, None, int(value)
    except ValueError:
        return False, "Query parameter 'author_id' must be an integer", None
