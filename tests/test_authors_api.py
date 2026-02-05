"""Authors API tests."""


def test_create_author_success(client, auth_headers):
    r = client.post(
        "/authors",
        json={"id": 100, "name": "Jane Doe", "bio": "Writer", "country": "UK"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "success"
    assert data["id"] == 100
    assert "Jane Doe" in data["message"]


def test_create_author_unauthorized(client):
    r = client.post(
        "/authors",
        json={"id": 101, "name": "No Auth"},
    )
    assert r.status_code == 401


def test_create_author_duplicate_id(client, auth_headers):
    client.post(
        "/authors",
        json={"id": 102, "name": "First"},
        headers=auth_headers,
    )
    r = client.post(
        "/authors",
        json={"id": 102, "name": "Second"},
        headers=auth_headers,
    )
    assert r.status_code == 409
    assert "error" in r.json()


def test_get_author_books_success(client, auth_headers, author_id):
    # API returns 404 when author has no books; add one book first
    client.post(
        "/books",
        json={"id": 1, "title": "First Book", "author_id": author_id},
        headers=auth_headers,
    )
    r = client.get(f"/authors/{author_id}/books")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["author"]["id"] == author_id
    assert data["author"]["name"] == "Test Author"
    assert len(data["books"]) == 1
    assert data["books"][0]["title"] == "First Book"


def test_get_author_books_with_books(client, auth_headers, author_id):
    client.post(
        "/books",
        json={"id": 200, "title": "Author Book", "author_id": author_id},
        headers=auth_headers,
    )
    r = client.get(f"/authors/{author_id}/books")
    assert r.status_code == 200
    assert len(r.json()["books"]) == 1
    assert r.json()["books"][0]["title"] == "Author Book"


def test_get_author_books_not_found(client):
    r = client.get("/authors/99999/books")
    assert r.status_code == 404
    assert "error" in r.json()
