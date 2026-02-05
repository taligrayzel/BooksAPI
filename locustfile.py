"""Locust load tests for the Books API.

Usage (example ~100 RPS, depends on response times):

    locust -f locustfile.py --headless -u 100 -r 20 -t 5m -H http://localhost:5000

Make sure the Flask app is running (python run.py) before starting Locust.
"""

import random
import string

from locust import HttpUser, task, between


def _random_suffix(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class BooksApiUser(HttpUser):
    """
    Simulates a user that:
    - registers + logs in on start
    - frequently lists books
    - sometimes filters by author_id
    - occasionally creates a book (authenticated)
    """

    # Small wait so users keep sending requests; tune for desired RPS.
    wait_time = between(0.0, 0.05)

    def on_start(self):
        """Register and log in once per simulated user."""
        self.username = f"locust_{_random_suffix()}"
        self.password = "testpass"
        # Try to register; ignore conflicts if user already exists
        self.client.post(
            "/register",
            json={"username": self.username, "password": self.password},
            name="POST /register",
        )
        login_resp = self.client.post(
            "/auth/login",
            json={"username": self.username, "password": self.password},
            name="POST /auth/login",
        )
        if login_resp.status_code == 200:
            self.token = login_resp.json().get("access_token")
        else:
            self.token = None

    @property
    def auth_headers(self) -> dict:
        if getattr(self, "token", None):
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(5)
    def list_books(self):
        """List all books."""
        self.client.get("/books", name="GET /books")

    @task(2)
    def list_books_by_author(self):
        """List books filtered by author_id (if any)."""
        # For load, just hit with a small author_id; API returns 200 or 400/404 as usual.
        self.client.get("/books", params={"author_id": 1}, name="GET /books?author_id=1")

    @task(1)
    def create_book(self):
        """Create a book (requires auth)."""
        if not self.token:
            return

        # Random IDs to minimize collisions; conflicts are still valid behavior.
        book_id = random.randint(1, 1_000_000_000)
        title = f"LoadTest Book {_random_suffix(6)}"
        payload = {
            "id": book_id,
            "title": title,
            # Use a small author_id; for higher success rate, you can pre-seed authors with id=1.
            "author_id": 1,
            "isbn": "9780132350884",
            "published_year": 2020,
            "genres": ["LoadTest"],
        }
        self.client.post("/books", json=payload, headers=self.auth_headers, name="POST /books")

