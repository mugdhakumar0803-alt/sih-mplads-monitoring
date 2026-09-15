# Citizen grievance database model
from sqlalchemy import Column, String, DateTime, Text, Integer, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
import enum

from ..database import Base


class GrievanceStatus(str, enum.Enum):
    REGISTERED = "registered"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    CLOSED = "closed"


class GrievanceSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GrievanceVisibility(str, enum.Enum):
    """
    NEW — this is the fix. Public transparency (citizens seeing their own
    filed grievances, and the general public seeing anonymized work-level
    status) is a core feature of this platform. But an MP or official
    raising a concern to a higher authority is an internal administrative
    matter, not something a citizen should see in their feed.
    """
    PUBLIC = "public"                # citizen-filed, visible per normal rules
    OFFICIAL_ONLY = "official_only"  # MP/official-filed escalations — never shown to citizens


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grievance_id = Column(String(50), unique=True, index=True, nullable=False)
    work_id = Column(String(50), ForeignKey("works.work_id"), index=True)

    filed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    filed_by_role = Column(String(30), nullable=False, default="citizen")  # NEW — who actually filed this
    visibility = Column(Enum(GrievanceVisibility), default=GrievanceVisibility.PUBLIC, nullable=False)  # NEW

    citizen_name = Column(String(255), nullable=False)
    citizen_contact = Column(String(20))
    citizen_email = Column(String(255))
    description = Column(Text, nullable=False)
    severity = Column(Enum(GrievanceSeverity), default=GrievanceSeverity.MEDIUM)
    status = Column(Enum(GrievanceStatus), default=GrievanceStatus.REGISTERED, index=True)
    resolution_notes = Column(Text)
    is_escalated = Column(Boolean, default=False)

    current_escalation_level = Column(String(20), default="district")
    last_escalated_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)