from datetime import datetime

from sqlalchemy import Column, DateTime, String, Index

from ..database import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti = Column(
        String(36),
        primary_key=True,
    )

    user_id = Column(
        String(100),
        index=True,
        nullable=False,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    revoked_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_revoked_tokens_expires_at",
            "expires_at",
        ),
    )