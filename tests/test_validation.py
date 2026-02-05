"""Validation tests: invalid payloads return 400 with expected error messages."""


def test_register_empty_body(client):
    r = client.post("/register", json={})
    assert r.status_code == 400
    assert "error" in r.json()
    assert "JSON" in r.json()["error"] or "body" in r.json()["error"].lower()


def test_register_missing_username(client):
    r = client.post("/register", json={"password": "secret"})
    assert r.status_code == 400
    assert "username" in r.json()["error"].lower()


def test_register_missing_password(client):
    r = client.post("/register", json={"username": "u"})
    assert r.status_code == 400
    assert "password" in r.json()["error"].lower()


def test_register_empty_username(client):
    r = client.post("/register", json={"username": "   ", "password": "p"})
    assert r.status_code == 400
    assert "username" in r.json()["error"].lower()


def test_register_empty_password(client):
    r = client.post("/register", json={"username": "u", "password": ""})
    assert r.status_code == 400
    assert "password" in r.json()["error"].lower()


def test_login_empty_body(client):
    r = client.post("/auth/login", json={})
    assert r.status_code == 400
    assert "error" in r.json()


def test_login_missing_username(client):
    r = client.post("/auth/login", json={"password": "p"})
    assert r.status_code == 400
    assert "username" in r.json()["error"].lower()


def test_login_missing_password(client):
    r = client.post("/auth/login", json={"username": "u"})
    assert r.status_code == 400
    assert "password" in r.json()["error"].lower()


def test_login_empty_username(client):
    r = client.post("/auth/login", json={"username": "", "password": "p"})
    assert r.status_code == 400
    assert "username" in r.json()["error"].lower()


# --- Book create validation ---

def test_book_create_empty_body(client, auth_headers):
    r = client.post("/books", json={}, headers=auth_headers)
    assert r.status_code == 400
    assert "JSON" in r.json()["error"] or "body" in r.json()["error"].lower()


def test_book_create_missing_id(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={"title": "T", "author_id": author_id},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "id" in r.json()["error"].lower()


def test_book_create_id_not_integer(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={"id": "1", "title": "T", "author_id": author_id},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "id" in r.json()["error"].lower() and "integer" in r.json()["error"].lower()


def test_book_create_missing_title(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={"id": 1, "author_id": author_id},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "title" in r.json()["error"].lower()


def test_book_create_empty_title(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={"id": 1, "title": "   ", "author_id": author_id},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "title" in r.json()["error"].lower()


def test_book_create_missing_author_id(client, auth_headers):
    r = client.post(
        "/books",
        json={"id": 1, "title": "T"},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "author_id" in r.json()["error"].lower()


def test_book_create_author_id_not_integer(client, auth_headers):
    r = client.post(
        "/books",
        json={"id": 1, "title": "T", "author_id": "1"},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "author_id" in r.json()["error"].lower()


def test_book_create_invalid_isbn(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={"id": 1, "title": "T", "author_id": author_id, "isbn": "short"},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "isbn" in r.json()["error"].lower()


def test_book_create_isbn_not_string(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={"id": 1, "title": "T", "author_id": author_id, "isbn": 123},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "isbn" in r.json()["error"].lower()


def test_book_create_published_year_not_integer(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={"id": 1, "title": "T", "author_id": author_id, "published_year": "2020"},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "published_year" in r.json()["error"].lower()


def test_book_create_genres_not_list(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={"id": 1, "title": "T", "author_id": author_id, "genres": "Fiction"},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "genres" in r.json()["error"].lower()


def test_book_create_genre_item_empty(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={"id": 1, "title": "T", "author_id": author_id, "genres": [""]},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "genre" in r.json()["error"].lower()


# --- Book update validation ---

def test_book_update_empty_body(client, auth_headers, author_id):
    client.post(
        "/books",
        json={"id": 1, "title": "T", "author_id": author_id},
        headers=auth_headers,
    )
    r = client.put("/books/1", json={}, headers=auth_headers)
    assert r.status_code == 400
    assert "error" in r.json()


def test_book_update_no_fields(client, auth_headers, author_id):
    client.post(
        "/books",
        json={"id": 2, "title": "T", "author_id": author_id},
        headers=auth_headers,
    )
    # Body with no valid update fields (title, author_id, isbn, published_year, genres)
    r = client.put("/books/2", json={"other": "ignored"}, headers=auth_headers)
    assert r.status_code == 400
    err = r.json()["error"].lower()
    assert "at least one" in err or "field" in err or "provided" in err


def test_book_update_empty_title(client, auth_headers, author_id):
    client.post(
        "/books",
        json={"id": 3, "title": "T", "author_id": author_id},
        headers=auth_headers,
    )
    r = client.put("/books/3", json={"title": "   "}, headers=auth_headers)
    assert r.status_code == 400
    assert "title" in r.json()["error"].lower()


def test_book_update_author_id_not_integer(client, auth_headers, author_id):
    client.post(
        "/books",
        json={"id": 4, "title": "T", "author_id": author_id},
        headers=auth_headers,
    )
    r = client.put("/books/4", json={"author_id": "x"}, headers=auth_headers)
    assert r.status_code == 400
    assert "author_id" in r.json()["error"].lower()


# --- Author create validation ---

def test_author_create_empty_body(client, auth_headers):
    r = client.post("/authors", json={}, headers=auth_headers)
    assert r.status_code == 400
    assert "error" in r.json()


def test_author_create_missing_id(client, auth_headers):
    r = client.post(
        "/authors",
        json={"name": "Author Name"},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "id" in r.json()["error"].lower()


def test_author_create_id_not_integer(client, auth_headers):
    r = client.post(
        "/authors",
        json={"id": "1", "name": "Author"},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "id" in r.json()["error"].lower() and "integer" in r.json()["error"].lower()


def test_author_create_missing_name(client, auth_headers):
    r = client.post(
        "/authors",
        json={"id": 1},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "name" in r.json()["error"].lower()


def test_author_create_empty_name(client, auth_headers):
    r = client.post(
        "/authors",
        json={"id": 1, "name": "   "},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "name" in r.json()["error"].lower()


# --- Query param validation ---

def test_books_list_author_id_not_integer(client):
    r = client.get("/books", params={"author_id": "abc"})
    assert r.status_code == 400
    assert "author_id" in r.json()["error"].lower()
    assert "integer" in r.json()["error"].lower()
