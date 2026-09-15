from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from .schemas import TokenData
from ..config import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:

    now = datetime.now(timezone.utc)

    expire = (
        now + expires_delta
        if expires_delta
        else now + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    to_encode = data.copy()

    to_encode.update(
        {
            "iat": now,
            "exp": expire,
            "jti": str(uuid4()),
            "type": "access",
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        }
    )

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_token(
    token: str,
) -> Optional[TokenData]:

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )

        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            return None

        return TokenData(
            user_id=str(user_id),
            role=payload.get("role"),
            constituency_id=payload.get("constituency_id"),
            district_id=payload.get("district_id"),
            state_id=payload.get("state_id"),
            jti=str(jti),
        )

    except (
        JWTError,
        ValueError,
        TypeError,
    ):
        return None