from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
import uuid

from ..database import Base


class ReportSignature(Base):
    __tablename__ = "report_signatures"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(100), unique=True, index=True, nullable=False)
    report_hash = Column(String(64), nullable=False)
    signature = Column(Text, nullable=False)
    algorithm = Column(String(100), nullable=False)
    signed_by = Column(String(100), nullable=False)
    signed_at = Column(DateTime, default=datetime.utcnow)
