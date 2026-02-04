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
docker-compose.yml  # PostgreSQL container
run.py              # Entry point
```
