# Fund release database model
from sqlalchemy import Column, String, DateTime, Float, Integer, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
import enum

from ..database import Base


class ReleaseStatus(str, enum.Enum):
    """Fund release status."""
    PENDING = "pending"
    APPROVED = "approved"
    RELEASED = "released"
    REJECTED = "rejected"


class FundReleaseRecord(Base):
    """Fund release and eligibility tracking."""
    __tablename__ = "fund_releases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_id = Column(String(50), unique=True, index=True, nullable=False)
    work_id = Column(String(50), ForeignKey("works.work_id"), index=True, nullable=False)
    
    # Fund details
    sanction_amount = Column(Float, nullable=False)
    released_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float)
    release_number = Column(Integer, default=1)
    
    # Status and dates
    status = Column(Enum(ReleaseStatus), default=ReleaseStatus.PENDING, index=True)
    requested_date = Column(DateTime, nullable=False)
    approval_date = Column(DateTime)
    release_date = Column(DateTime)
    
    # Eligibility check
    eligibility_status = Column(String(50))  # eligible, ineligible, conditional
    eligibility_checks = Column(JSON)  # Detailed check results
    compliance_score = Column(Float)  # 0-1 compliance score
    
    # Notes
    approval_notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
