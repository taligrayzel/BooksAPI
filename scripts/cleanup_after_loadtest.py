"""Remove Locust load-test data from the database after a performance check.

Deletes users with username starting with 'locust_' and all books they created.
Run from project root: python -m scripts.cleanup_after_loadtest
"""
import os
import sys

from sqlalchemy import text

# Add project root so app is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine


def main():
    with engine.connect() as conn:
        with conn.begin():
            # Delete in FK order: book_genre -> books -> users
            r1 = conn.execute(
                text("""
                    DELETE FROM book_genre
                    WHERE book_id IN (
                        SELECT id FROM books
                        WHERE created_by_id IN (
                            SELECT id FROM users WHERE username LIKE 'locust_%'
                        )
                    )
                """)
            )
            r2 = conn.execute(
                text("""
                    DELETE FROM books
                    WHERE created_by_id IN (
                        SELECT id FROM users WHERE username LIKE 'locust_%'
                    )
                """)
            )
            r3 = conn.execute(text("DELETE FROM users WHERE username LIKE 'locust_%'"))
            deleted_books = r2.rowcount
            deleted_users = r3.rowcount
    print(f"Cleanup done: {deleted_users} locust users, {deleted_books} books removed.")


if __name__ == "__main__":
    main()
