# Books API

Flask REST API for managing books and authors, with user registration and JWT authentication.

## Tech Stack

- **Flask** – web framework
- **SQLAlchemy** – ORM
- **PostgreSQL** – database
- **Alembic** – migrations
- **passlib[bcrypt]** – password hashing
- **python-dotenv** – environment config

## Prerequisites

- Python 3.x
- PostgreSQL (or use Docker)

## Setup

1. **Clone and create a virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   # source venv/bin/activate   # Linux/macOS
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start PostgreSQL** (if using Docker)

   ```bash
   docker-compose up -d
   ```

4. **Configure database** (optional)

   Default in `app/database.py`: `postgresql+psycopg2://postgres:password@localhost:5432/my_project_db`. Override with a `.env` file or change the URL.

5. **Run migrations**

   ```bash
   alembic upgrade head
   ```

## Run

```bash
python run.py
```

API runs at **http://localhost:5000**.

## API Overview

| Method | Endpoint              | Auth   | Description                         |
| ------ | --------------------- | ------ | ----------------------------------- |
| GET    | `/`                   | —      | Welcome message                     |
| GET    | `/books`              | —      | List books (optional `?author_id=`) |
| GET    | `/books/<id>`         | —      | Get book by ID                      |
| POST   | `/books`              | Bearer | Create book                         |
| PUT    | `/books/<id>`         | Bearer | Update book                         |
| DELETE | `/books/<id>`         | Bearer | Delete book (owner only)            |
| POST   | `/authors`            | Bearer | Create author                       |
| GET    | `/authors/<id>/books` | —      | Get author and their books          |
| POST   | `/register`           | —      | Register user                       |
| POST   | `/auth/login`         | —      | Login, returns `access_token`       |

**Protected routes:** send header `Authorization: Bearer <access_token>`.

## API Docs

- **Swagger UI:** http://localhost:5000/docs
- **OpenAPI spec:** http://localhost:5000/openapi.json

## Testing

Tests use **pytest** and **httpx** (WSGI transport) against an in-memory SQLite DB.

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

Set `DATABASE_URL` and `SECRET_KEY` in env to override; tests default to `sqlite:///:memory:` and a test secret.

## Load testing (Locust)

You can run basic load tests with **Locust** against the running API.

1. Install dependencies (includes `locust`):

   ```bash
   pip install -r requirements.txt
   ```

2. Start the API (in another terminal):

   ```bash
   python run.py
   ```

3. Run Locust in headless mode, targeting ~100 requests/second (depends on response times):

   ```bash
   locust -f locustfile.py --headless -u 100 -r 20 -t 5m -H http://localhost:5000
   ```

   - **`-u 100`**: 100 concurrent simulated users.
   - **`-r 20`**: spawn 20 users per second.
   - **`-t 5m`**: run for 5 minutes.
   - **`-H`**: API base URL.

4. **Cleanup after the load test** (remove Locust-created users and their books):

   ```bash
   python -m scripts.cleanup_after_loadtest
   ```

   This deletes users with `username` starting with `locust_` and all books they created. Uses the same `DATABASE_URL` as the app.

### Performance check guidelines

When you run Locust, check the **response time percentiles** in the summary:

- For local development on a laptop, rough targets:
  - **Median (50%)**: ideally \< **500–800 ms**
  - **p95** (95%): ideally \< **1–2 s**
  - Occasional slower responses are expected during heavy load, but sustained **5–10 s** latencies mean the app or DB is saturated.
- If you see `QueuePool limit ... reached` or many HTTP 500s in Locust:
  - Lower the load (smaller `-u`/`-r`, larger `wait_time` in `locustfile.py`), or
  - Increase DB pool sizes in `app/database.py` and ensure Postgres has enough resources.

## Project Structure

```
app/
  main.py           # App factory
  auth.py           # JWT creation & token_required
  database.py       # SQLAlchemy engine & session
  routers/          # Blueprints: books, authors, auth, docs
  services/         # BookService, AuthorService, UserService
  schemas/          # Validation & serialization
  models/           # SQLAlchemy models
alembic/            # Migrations
tests/              # pytest + httpx API tests
scripts/            # Post-load-test cleanup
locustfile.py       # Locust load test scenarios
docker-compose.yml  # PostgreSQL container
run.py              # Entry point
```
