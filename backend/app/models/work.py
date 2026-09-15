# MPLADS work/sanction database model
from sqlalchemy import Column, String, Float, DateTime, Integer, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
import enum

from ..database import Base


class WorkStatus(str, enum.Enum):
    """Work status values."""
    SANCTIONED = "Sanctioned"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    UNSANCTIONED = "Unsanctioned"
    REJECTED = "Rejected"


class WorkCategory(str, enum.Enum):
    """Work categories."""
    DRINKING_WATER = "drinking_water"
    ROAD = "road"
    COMMUNITY_INFRASTRUCTURE = "community_infrastructure"
    EDUCATION = "education"
    SANITATION = "sanitation"
    ELECTRIFICATION = "electrification"
    HEALTH = "health"
    SPORTS = "sports"
    IRRIGATION = "irrigation"
    STREET_LIGHTING = "street_lighting"


class Work(Base):
    """MPLADS work record model."""
    __tablename__ = "works"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_id = Column(String(50), unique=True, index=True, nullable=False)
    mp_name = Column(String(255), nullable=False)
    work_title = Column(String(500), nullable=False)
    category = Column(Enum(WorkCategory), nullable=False)
    state = Column(String(100), index=True, nullable=False)
    constituency = Column(String(255), nullable=False)
    location = Column(String(255))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(Enum(WorkStatus), default=WorkStatus.UNSANCTIONED, index=True)
    allocation_amount = Column(Float, nullable=False)
    ida_approval = Column(String(50))
    recommended_date = Column(DateTime, nullable=False)
    completion_date = Column(DateTime)
    recommended_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    sanctioned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    sanctioned_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(50))
    anomaly_drivers = Column(JSON)
    days_since_last_photo = Column(Float)
    citizen_grievance_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
