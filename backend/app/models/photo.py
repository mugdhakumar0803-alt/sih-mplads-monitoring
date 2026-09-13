# Photo verification database model
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid

from ..database import Base


class PhotoVerification(Base):
    """Work progress photo verification model."""
    __tablename__ = "photo_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_id = Column(String(50), ForeignKey("works.work_id"), index=True, nullable=False)
    photo_url = Column(String(500), nullable=False)
    photo_hash = Column(String(255))  # For duplicate detection
    capture_date = Column(DateTime, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    # Verification metadata
    is_verified = Column(String(50), default="pending")  # pending, verified, rejected
    verification_score = Column(Float)  # 0-1 confidence score
    verification_method = Column(String(100))  # manual, ai_validation, blockchain
    metadata = Column(JSON)  # Location, device info, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
