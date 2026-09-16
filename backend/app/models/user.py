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


# Local/demo deployments do not have a separate admin-approval workflow.
# All roles are allowed to authenticate immediately unless an explicit approval
# system is added later.
ROLES_REQUIRING_APPROVAL = set()


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
        # The current application does not include an approval workflow.
        # Treat all roles as approved so demo and local usage works without
        # administrative intervention.
        return True

    def can_access_system(self) -> bool:
        return (
            self.is_active
            and self.is_approved()
        )