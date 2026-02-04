"""Auth and user registration routes."""
from flask import Blueprint, abort, jsonify, request

from app.database import session_scope
from app.auth import create_token
from app.schemas import validate_register, validate_login
from app.services import UserService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def add_user():
    ok, err, payload = validate_register(request.get_json())
    if not ok:
        abort(400, description=err)

    with session_scope() as session:
        user, err = UserService(session).register(payload["username"], payload["password"])
        user_id, username = (user.id, user.username) if user else (None, None)
    if err:
        abort(409, description=err)
    return (
        jsonify({"status": "success", "id": user_id, "message": f"user '{username}' created!"}),
        201,
    )


@auth_bp.route("/auth/login", methods=["POST"])
def user_login():
    ok, err, payload = validate_login(request.get_json())
    if not ok:
        abort(400, description=err)

    with session_scope() as session:
        user, auth_err = UserService(session).authenticate(
            payload["username"], payload["password"]
        )
        user_id = user.id if user else None
    if auth_err == "user_not_found":
        abort(404, description="Username does not exists")
    if auth_err == "invalid_password":
        abort(401, description="Password is not correct")
    token = create_token(user_id)
    return jsonify({"access_token": token}), 200
