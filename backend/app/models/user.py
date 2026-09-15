from datetime import datetime
import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STATE_OFFICIAL = "state_official"
    DISTRICT_OFFICIAL = "district_official"
    MP = "mp"
    MINISTRY = "ministry"
    CITIZEN = "citizen"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ParliamentHouse(str, enum.Enum):
    LOK_SABHA = "lok_sabha"
    RAJYA_SABHA = "rajya_sabha"


ROLES_REQUIRING_APPROVAL = {
    UserRole.ADMIN,
    UserRole.MP,
    UserRole.MINISTRY,
    UserRole.STATE_OFFICIAL,
    UserRole.DISTRICT_OFFICIAL,
}


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    username = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password = Column(
        String(255),
        nullable=False,
    )

    role = Column(
        Enum(UserRole),
        default=UserRole.CITIZEN,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    approval_status = Column(
        Enum(ApprovalStatus),
        default=ApprovalStatus.APPROVED,
        nullable=False,
    )

    house = Column(
        Enum(ParliamentHouse),
        nullable=True,
    )

    constituency_id = Column(
        String(100),
        index=True,
        nullable=True,
    )

    district_id = Column(
        String(100),
        index=True,
        nullable=True,
    )

    state_id = Column(
        String(100),
        index=True,
        nullable=True,
    )

    state = Column(
        String(100),
        nullable=True,
    )

    constituency = Column(
        String(100),
        nullable=True,
    )

    preferred_language = Column(
        String(10),
        default="en-IN",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def requires_approval(self) -> bool:
        return self.role in ROLES_REQUIRING_APPROVAL

    def is_approved(self) -> bool:
        if not self.requires_approval():
            return True

        return self.approval_status == ApprovalStatus.APPROVED

    def can_access_system(self) -> bool:
        return (
            self.is_active
            and self.is_approved()
        )