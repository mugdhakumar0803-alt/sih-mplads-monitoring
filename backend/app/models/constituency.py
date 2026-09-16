# Constituencies - Reference table
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database import Base


class Constituency(Base):
    """Constituency reference with reservation status (543 constituencies)"""
    __tablename__ = "constituencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    constituency_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    state = Column(String(100), index=True, nullable=False)
    constituency_no_in_state = Column(Integer, nullable=True)
    reservation_status = Column(String(50), nullable=True)  # SC, ST, OBC, None
    electors_2024 = Column(Integer, nullable=True)
    data_source = Column(String(100), default='CONSTITUENCY_REFERENCE')
    created_at = Column(DateTime, default=datetime.utcnow)
