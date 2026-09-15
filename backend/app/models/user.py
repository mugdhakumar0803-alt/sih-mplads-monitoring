# User database model
from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STATE_OFFICIAL = "state_official"
    DISTRICT_OFFICIAL = "district_official"
    MP = "mp"
    MINISTRY = "ministry"
    CITIZEN = "citizen"


class ApprovalStatus(str, enum.Enum):
    """NEW — controls who can actually act as a privileged role.
    Citizens are auto-approved; every official role needs Ministry sign-off
    before their account can do anything beyond viewing."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ParliamentHouse(str, enum.Enum):
    """NEW — only meaningful when role == MP."""
    LOK_SABHA = "lok_sabha"
    RAJYA_SABHA = "rajya_sabha"


# Roles that require Ministry approval before they're trusted — citizens
# don't need this, they're approved automatically at registration.
ROLES_REQUIRING_APPROVAL = {UserRole.MP, UserRole.MINISTRY, UserRole.STATE_OFFICIAL, UserRole.DISTRICT_OFFICIAL}


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, nullable=False)
    is_active = Column(Boolean, default=True)

    # NEW fields
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    house = Column(Enum(ParliamentHouse), nullable=True)   # only set when role == MP
    state = Column(String(100), nullable=True)             # for citizens AND officials — used to scope what they see
    constituency = Column(String(100), nullable=True)      # for MPs specifically

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_privileged_and_unapproved(self) -> bool:
        return self.role in ROLES_REQUIRING_APPROVAL and self.approval_status != ApprovalStatus.APPROVED
preferred_language = Column(String(10), default="en-IN")