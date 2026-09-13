# Citizen grievance database model
from sqlalchemy import Column, String, DateTime, Text, Integer, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
import enum

from ..database import Base


class GrievanceStatus(str, enum.Enum):
    """Grievance status."""
    REGISTERED = "registered"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    CLOSED = "closed"


class GrievanceSeverity(str, enum.Enum):
    """Grievance severity level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Grievance(Base):
    """Citizen grievance model."""
    __tablename__ = "grievances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grievance_id = Column(String(50), unique=True, index=True, nullable=False)
    work_id = Column(String(50), ForeignKey("works.work_id"), index=True)
    citizen_name = Column(String(255), nullable=False)
    citizen_contact = Column(String(20))
    citizen_email = Column(String(255))
    description = Column(Text, nullable=False)
    severity = Column(Enum(GrievanceSeverity), default=GrievanceSeverity.MEDIUM)
    status = Column(Enum(GrievanceStatus), default=GrievanceStatus.REGISTERED, index=True)
    resolution_notes = Column(Text)
    is_escalated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
