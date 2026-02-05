"""Auth API tests: register, login."""


def test_register_success(client):
    r = client.post("/register", json={"username": "alice", "password": "secret123"})
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "success"
    assert "id" in data
    assert "alice" in data["message"]


def test_register_missing_body(client):
    r = client.post("/register", json={})
    assert r.status_code == 400
    assert "error" in r.json()


def test_register_duplicate_username(client):
    client.post("/register", json={"username": "bob", "password": "pass"})
    r = client.post("/register", json={"username": "bob", "password": "other"})
    assert r.status_code == 409
    assert "error" in r.json()


def test_login_success(client):
    client.post("/register", json={"username": "logintest", "password": "mypass"})
    r = client.post("/auth/login", json={"username": "logintest", "password": "mypass"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    client.post("/register", json={"username": "u", "password": "right"})
    r = client.post("/auth/login", json={"username": "u", "password": "wrong"})
    assert r.status_code == 401
    assert "error" in r.json()


def test_login_user_not_found(client):
    r = client.post("/auth/login", json={"username": "nonexistent", "password": "x"})
    assert r.status_code == 404
    assert "error" in r.json()


def test_login_missing_body(client):
    r = client.post("/auth/login", json={})
    assert r.status_code == 400
