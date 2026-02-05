"""Books API tests."""
import pytest


def test_home(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Welcome" in r.text


def test_list_books_empty(client):
    r = client.get("/books")
    assert r.status_code == 200
    assert r.json() == []


def test_list_books_with_author_filter(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={
            "id": 1,
            "title": "Book One",
            "author_id": author_id,
            "isbn": "978-0-13-235088-4",
            "published_year": 2020,
            "genres": ["Fiction"],
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    r = client.get("/books", params={"author_id": author_id})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["title"] == "Book One"
    assert data[0]["author_id"] == author_id


def test_get_book_by_id_not_found(client):
    r = client.get("/books/99999")
    assert r.status_code == 404
    assert "error" in r.json()


def test_create_book_success(client, auth_headers, author_id):
    r = client.post(
        "/books",
        json={
            "id": 10,
            "title": "New Book",
            "author_id": author_id,
            "published_year": 2023,
            "genres": [],
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "success"
    assert data["id"] == 10
    r2 = client.get("/books/10")
    assert r2.status_code == 200
    assert r2.json()["title"] == "New Book"


def test_create_book_unauthorized(client, author_id):
    r = client.post(
        "/books",
        json={"id": 11, "title": "X", "author_id": author_id},
    )
    assert r.status_code == 401


def test_create_book_author_not_found(client, auth_headers):
    r = client.post(
        "/books",
        json={"id": 12, "title": "Y", "author_id": 99999},
        headers=auth_headers,
    )
    assert r.status_code == 400  # Author not found returns 400 from route


def test_update_book_success(client, auth_headers, author_id):
    client.post(
        "/books",
        json={"id": 20, "title": "Original", "author_id": author_id},
        headers=auth_headers,
    )
    r = client.put(
        "/books/20",
        json={"title": "Updated Title"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    r2 = client.get("/books/20")
    assert r2.json()["title"] == "Updated Title"


def test_update_book_not_found(client, auth_headers):
    r = client.put(
        "/books/99999",
        json={"title": "X"},
        headers=auth_headers,
    )
    assert r.status_code == 404


def test_delete_book_success(client, auth_headers, author_id):
    client.post(
        "/books",
        json={"id": 30, "title": "To Delete", "author_id": author_id},
        headers=auth_headers,
    )
    r = client.delete("/books/30", headers=auth_headers)
    assert r.status_code == 200
    r2 = client.get("/books/30")
    assert r2.status_code == 404


def test_delete_book_forbidden_when_created_by_other_user(client, auth_headers, author_id):
    client.post(
        "/books",
        json={"id": 31, "title": "Owner Book", "author_id": author_id},
        headers=auth_headers,
    )
    client.post("/register", json={"username": "otheruser", "password": "otherpass"})
    r = client.post("/auth/login", json={"username": "otheruser", "password": "otherpass"})
    token = r.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {token}"}
    r = client.delete("/books/31", headers=other_headers)
    assert r.status_code == 403


def test_delete_book_not_found(client, auth_headers):
    r = client.delete("/books/99999", headers=auth_headers)
    assert r.status_code == 404
