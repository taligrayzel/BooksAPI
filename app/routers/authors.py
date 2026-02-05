"""Authors API routes."""
from flask import Blueprint, abort, jsonify, request

from app.database import session_scope
from app.auth import token_required
from app.schemas import validate_author_create, book_to_dict, author_to_dict
from app.services import AuthorService

authors_bp = Blueprint("authors", __name__)


@authors_bp.route("/authors", methods=["POST"])
@token_required
def add_author(_current_user_id):
    ok, err, payload = validate_author_create(request.get_json())
    if not ok:
        abort(400, description=err)

    with session_scope() as session:
        author, err = AuthorService(session).create(payload)
        if err:
            abort(409 if "already" in err else 400, description=err)
        author_id, author_name = author.id, author.name
    return (
        jsonify({"status": "success", "id": author_id, "message": f"author '{author_name}' created!"}),
        201,
    )


@authors_bp.route("/authors/<int:author_id>/books", methods=["GET"])
def get_author_books(author_id):
    with session_scope() as session:
        author = AuthorService(session).get_with_books(author_id)
        if author is None:
            abort(404, description="Author not found")
        books_data = [book_to_dict(b) for b in author.books]
        if not books_data:
            abort(404, description="No books found for author")
        payload = {
            "status": "success",
            "author": author_to_dict(author),
            "books": books_data,
        }
    return jsonify(payload), 200
