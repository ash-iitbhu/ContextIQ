from ..db import MilvusUserDB


class AuthService:
    """Service for user authentication and registration."""

    def __init__(self):
        self.user_db = MilvusUserDB()

    def user_exists(self, username: str) -> bool:
        return self.user_db.user_exists(username)

    def insert_user(self, username: str, password_hash: str) -> None:
        self.user_db.insert_user(username, password_hash)

    def get_password_hash(self, username: str) -> str:
        return self.user_db.get_password_hash(username)
