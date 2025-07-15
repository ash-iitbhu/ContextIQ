from pydantic import BaseModel


class User(BaseModel):
    """User model for authentication."""

    username: str
    password: str
