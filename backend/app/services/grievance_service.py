# Business logic for citizen grievances
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.grievance import Grievance, GrievanceStatus, GrievanceSeverity
import uuid


class GrievanceService:
    """Service for grievance-related operations."""
    
    @staticmethod
    def get_all_grievances(
        db: Session,
        work_id: Optional[str] = None,
        status: Optional[GrievanceStatus] = None,
        severity: Optional[GrievanceSeverity] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Grievance]:
        """Get grievances with optional filtering."""
        query = db.query(Grievance)
        
        if work_id:
            query = query.filter(Grievance.work_id == work_id)
        if status:
            query = query.filter(Grievance.status == status)
        if severity:
            query = query.filter(Grievance.severity == severity)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_grievance_by_id(db: Session, grievance_id: str) -> Optional[Grievance]:
        """Get a single grievance by ID."""
        return db.query(Grievance).filter(Grievance.grievance_id == grievance_id).first()
    
    @staticmethod
    def create_grievance(db: Session, grievance_data: dict) -> Grievance:
        """Create a new grievance record."""
        grievance_data = dict(grievance_data)
        grievance_data.setdefault("grievance_id", f"GRV-{uuid.uuid4().hex[:10].upper()}")
        new_grievance = Grievance(**grievance_data)
        db.add(new_grievance)
        db.commit()
        db.refresh(new_grievance)
        return new_grievance
    
    @staticmethod
    def update_grievance_status(
        db: Session,
        grievance_id: str,
        new_status: GrievanceStatus,
        resolution_notes: Optional[str] = None,
    ) -> Optional[Grievance]:
        """Update grievance status and resolution notes."""
        grievance = db.query(Grievance).filter(Grievance.grievance_id == grievance_id).first()
        if grievance:
            grievance.status = new_status
            if resolution_notes:
                grievance.resolution_notes = resolution_notes
            grievance.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(grievance)
        return grievance
    
    @staticmethod
    def escalate_grievance(db: Session, grievance_id: str) -> Optional[Grievance]:
        """Escalate a grievance."""
        grievance = db.query(Grievance).filter(Grievance.grievance_id == grievance_id).first()
        if grievance:
            grievance.is_escalated = True
            grievance.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(grievance)
        return grievance
