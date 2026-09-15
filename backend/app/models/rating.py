from sqlalchemy import (
    Column,
    Float,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    work_id = Column(
        UUID(as_uuid=True),
        ForeignKey("works.id"),
        nullable=False,
        index=True,
    )

    citizen_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    quality_score = Column(Float, nullable=False)
    usefulness_score = Column(Float, nullable=False)
    timeliness_score = Column(Float, nullable=False)
    maintenance_score = Column(Float, nullable=False)
    satisfaction_score = Column(Float, nullable=False)

    overall_score = Column(Float, nullable=False)

    comment = Column(Text)

    is_verified = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "citizen_id",
            "work_id",
            name="uq_citizen_work_rating",
        ),
    )