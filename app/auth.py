"""Authentication: password hashing, JWT, token_required decorator."""
import os
import datetime
from functools import wraps

import jwt
from flask import abort, request
from passlib.context import CryptContext

from app.database import session_scope
from app.models import Users

SECRET_KEY = os.environ.get("SECRET_KEY")  # Set in .env (never commit)
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
TOKEN_EXPIRY_HOURS = int(os.environ.get("TOKEN_EXPIRY_HOURS", "1"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user_from_request():
    """Extract and validate JWT; return (user_id, None) or abort with 401."""
    auth_header = request.headers.get("Authorization")
    token = auth_header[7:] if auth_header and auth_header.startswith("Bearer ") else None

    if not token:
        abort(401, description="Token is missing")

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = data["user_id"]
        with session_scope() as session:
            user = session.query(Users).get(user_id)
            if not user:
                abort(401, description="User not found")
            return user_id, None
    except jwt.ExpiredSignatureError:
        abort(401, description="Token expired")
    except jwt.InvalidTokenError:
        abort(401, description="Invalid token")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id, err_response = get_current_user_from_request()
        if err_response is not None:
            return err_response
        return f(user_id, *args, **kwargs)

    return decorated
