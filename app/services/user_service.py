"""User and auth business logic."""
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password
from app.models import Users


class UserService:
    def __init__(self, session: Session):
        self._session = session

    def register(self, username: str, password: str) -> tuple:
        """Returns (user, None) or (None, error_message)."""
        if self._session.query(Users).filter_by(username=username).first():
            return None, "Username already exists"
        user = Users(username=username, hashed_password=hash_password(password))
        self._session.add(user)
        self._session.commit()
        return user, None

    def get_by_username(self, username: str):
        return self._session.query(Users).filter_by(username=username).first()

    def authenticate(self, username: str, password: str) -> tuple:
        """Returns (user, None) if valid, else (None, 'user_not_found'|'invalid_password')."""
        user = self.get_by_username(username)
        if not user:
            return None, "user_not_found"
        if not verify_password(password, user.hashed_password):
            return None, "invalid_password"
        return user, None
