from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime

from ..database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(100), index=True)
    username = Column(String(255), index=True)
    role = Column(String(50), index=True)
    action = Column(String(100), index=True, nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255), index=True)
    ip_address = Column(String(64))
    user_agent = Column(Text)
    status = Column(String(30), nullable=False, default="SUCCESS")
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
