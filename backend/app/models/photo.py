import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class PhotoVerification(Base):
    __tablename__ = "photo_verifications"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    work_id = Column(
        String(50),
        ForeignKey("works.work_id"),
        nullable=False
    )

    photo_url = Column(String(500), nullable=True)
    photo_hash = Column(String(64), unique=True, nullable=False)

    capture_date = Column(DateTime, nullable=True)
    upload_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    is_verified = Column(String(20), default="pending")
    verification_score = Column(Float, default=0.0)

    verification_method = Column(String(100), nullable=True)

    photo_metadata = Column(JSON, nullable=True)