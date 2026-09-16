# MP Master - Reference table of Members of Parliament
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database import Base


class MPMaster(Base):
    """Master reference of Members of Parliament (18th Lok Sabha)"""
    __tablename__ = "mp_master"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mp_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    party = Column(String(100), nullable=True)
    state = Column(String(100), index=True, nullable=False)
    constituency = Column(String(255), nullable=True, index=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    term = Column(Integer, default=18)
    data_source = Column(String(100), default='MP_MASTER_18_SABHA')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
