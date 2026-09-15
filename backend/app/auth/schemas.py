from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TokenData(BaseModel):
    user_id: str
    role: Optional[str] = None
    constituency_id: Optional[str] = None
    district_id: Optional[str] = None
    state_id: Optional[str] = None
    jti: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[dict] = None


class UserLogin(BaseModel):
    username: str
    password: str = Field(min_length=8)


class UserRegister(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=255,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role: str = "citizen"

    constituency_id: Optional[str] = None
    district_id: Optional[str] = None
    state_id: Optional[str] = None