"""Books API routes."""
from flask import Blueprint, abort, jsonify, request

from app.database import session_scope
from app.auth import token_required
from app.models import Users
from app.schemas import (
    validate_book_create,
    validate_book_update,
    parse_author_id_query,
    book_to_dict,
)
from app.services import BookService

books_bp = Blueprint("books", __name__)


@books_bp.route("/")
def home():
    return "Welcome to the Books API!"


@books_bp.route("/books", methods=["POST"])
@token_required
def add_book(current_user_id):
    ok, err, payload = validate_book_create(request.get_json())
    if not ok:
        abort(400, description=err)

    with session_scope() as session:
        user = session.get(Users, current_user_id)
        book, err = BookService(session).create(payload, user)
        if err:
            abort(409 if "already exists" in err else 400, description=err)
        book_id, book_title = book.id, book.title
    return (
        jsonify({"status": "success", "id": book_id, "message": f"book '{book_title}' created!"}),
        201,
    )


@books_bp.route("/books", methods=["GET"])
def get_books():
    ok, err, author_id = parse_author_id_query(request.args.get("author_id"))
    if not ok:
        abort(400, description=err)

    with session_scope() as session:
        books = BookService(session).list_all(author_id=author_id)
        data = [book_to_dict(b) for b in books]
    return jsonify(data)


@books_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book_by_id(book_id):
    with session_scope() as session:
        book = BookService(session).get_by_id(book_id)
        if book is None:
            abort(404, description="Book not found")
        data = book_to_dict(book)
    return jsonify({"status": "success", **data}), 200


@books_bp.route("/books/<int:book_id>", methods=["PUT"])
@token_required
def update_book_by_id(_current_user_id, book_id):
    ok, err, payload = validate_book_update(request.get_json())
    if not ok:
        abort(400, description=err)

    with session_scope() as session:
        _, err = BookService(session).update(book_id, payload)
    if err:
        if err == "Book not found":
            abort(404, description=err)
        abort(400, description=err)

    return (
        jsonify({"status": "success", "message": f"Book with id {book_id} updated successfully!"}),
        200,
    )


@books_bp.route("/books/<int:book_id>", methods=["DELETE"])
@token_required
def delete_book_by_id(current_user_id, book_id):
    with session_scope() as session:
        _, err = BookService(session).delete(book_id, current_user_id)
    if err:
        if err == "Book not found":
            abort(404, description=err)
        if err == "Forbidden":
            abort(403, description=err)
        abort(500, description=err)
    return (
        jsonify({"status": "success", "message": f"Book with id {book_id} deleted successfully!"}),
        200,
    )
