# User database model
from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """User roles."""
    ADMIN = "admin"
    STATE_OFFICIAL = "state_official"
    DISTRICT_OFFICIAL = "district_official"
    MP = "mp"
    MINISTRY = "ministry"
    CITIZEN = "citizen"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, nullable=False)
    is_active = Column(Boolean, default=True)
    constituency_id = Column(String(100), index=True, nullable=True)
    district_id = Column(String(100), index=True, nullable=True)
    state_id = Column(String(100), index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)