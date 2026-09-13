# Pydantic schemas for auth
from pydantic import BaseModel
from typing import Optional


class TokenData(BaseModel):
    """JWT token data."""
    user_id: str


class Token(BaseModel):
    """Token response."""
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    """User login request."""
    username: str
    password: str


class UserRegister(BaseModel):
    """User registration request."""
    username: str
    email: str
    password: str
    role: str = "citizen"
