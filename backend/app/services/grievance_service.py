# Business logic for citizen grievances
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.grievance import Grievance, GrievanceStatus, GrievanceSeverity
from ..services.sla_engine import compute_sla_status
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
        grievance_data.setdefault("current_escalation_level", "district")
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
    def get_sla_status(db: Session, grievance_id: str) -> Optional[dict]:
        """
        Real SLA status for one grievance — call this whenever a grievance
        is viewed, so the frontend can show a live countdown and current
        ladder position instead of a static flag.
        """
        grievance = db.query(Grievance).filter(Grievance.grievance_id == grievance_id).first()
        if not grievance:
            return None

        status = compute_sla_status(
            filed_at=grievance.created_at,
            current_level=grievance.current_escalation_level or "district",
            last_escalated_at=grievance.last_escalated_at,
        )
        return {
            "current_level": status.current_level,
            "sla_deadline": status.sla_deadline,
            "days_remaining": status.days_remaining,
            "is_breached": status.is_breached,
            "should_escalate_to": status.should_escalate_to,
        }

    @staticmethod
    def check_and_apply_escalation(db: Session, grievance_id: str) -> Optional[Grievance]:
        """
        Actually escalates the grievance to the next ladder level if its
        SLA has been breached — this is what should replace the old
        'flip is_escalated to True' logic. Call this from a scheduled job
        (e.g. once a day) across all open grievances, or lazily whenever
        a grievance is read, whichever your team prefers for the demo.
        """
        grievance = db.query(Grievance).filter(Grievance.grievance_id == grievance_id).first()
        if not grievance:
            return None

        status = compute_sla_status(
            filed_at=grievance.created_at,
            current_level=grievance.current_escalation_level or "district",
            last_escalated_at=grievance.last_escalated_at,
        )

        if status.should_escalate_to:
            grievance.current_escalation_level = status.should_escalate_to
            grievance.last_escalated_at = datetime.utcnow()
            grievance.is_escalated = True  # kept for backward compatibility with existing frontend code
            grievance.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(grievance)

        return grievance

    @staticmethod
    def escalate_grievance(db: Session, grievance_id: str) -> Optional[Grievance]:
        """Kept for backward compatibility — now delegates to the real SLA check
        instead of blindly flipping a flag regardless of whether the SLA
        was actually breached."""
        return GrievanceService.check_and_apply_escalation(db, grievance_id)