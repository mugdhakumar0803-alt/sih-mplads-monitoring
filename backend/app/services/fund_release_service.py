# Business logic for fund release
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.fund_release import FundReleaseRecord, ReleaseStatus
from ..models.grievance import Grievance, GrievanceStatus
from ..models.work import Work, WorkStatus
from ..ml.compliance_engine import ComplianceEngine


class FundReleaseService:
    """Service for fund release operations."""

    REQUIRED_PROGRESS = 0.75

    @staticmethod
    def evaluate_eligibility(db: Session, release: FundReleaseRecord) -> dict:
        work = db.query(Work).filter(Work.work_id == release.work_id).first()
        if not work:
            return {"eligible": False, "checks": {"work_exists": False}, "reasons": ["Work not found"]}

        open_grievances = db.query(Grievance).filter(
            Grievance.work_id == release.work_id,
            Grievance.status.notin_([GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED]),
        ).count()
        progress = 1.0 if work.status == WorkStatus.COMPLETED else 0.0
        utilization = (release.released_amount or 0.0) / release.sanction_amount if release.sanction_amount else 0.0
        compliance = ComplianceEngine().check_compliance(work)
        checks = {
            "work_exists": True,
            "verified_completion": progress >= FundReleaseService.REQUIRED_PROGRESS,
            "utilization": utilization >= FundReleaseService.REQUIRED_PROGRESS,
            "no_unresolved_grievances": open_grievances == 0,
            "compliance": compliance["status"] == "compliant",
        }
        reasons = [name for name, passed in checks.items() if not passed]
        return {"eligible": not reasons, "checks": checks, "reasons": reasons, "compliance": compliance}
    
    @staticmethod
    def get_all_releases(
        db: Session,
        work_id: Optional[str] = None,
        status: Optional[ReleaseStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FundReleaseRecord]:
        """Get fund release records with optional filtering."""
        query = db.query(FundReleaseRecord)
        
        if work_id:
            query = query.filter(FundReleaseRecord.work_id == work_id)
        if status:
            query = query.filter(FundReleaseRecord.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_release_by_id(db: Session, release_id: str) -> Optional[FundReleaseRecord]:
        """Get a single fund release record."""
        return db.query(FundReleaseRecord).filter(FundReleaseRecord.release_id == release_id).first()
    
    @staticmethod
    def create_release_request(db: Session, release_data: dict) -> FundReleaseRecord:
        """Create a new fund release request."""
        new_release = FundReleaseRecord(**release_data)
        db.add(new_release)
        db.commit()
        db.refresh(new_release)
        return new_release
    
    @staticmethod
    def approve_release(
        db: Session,
        release_id: str,
        approval_notes: Optional[str] = None,
    ) -> Optional[FundReleaseRecord]:
        """Approve a fund release request."""
        release = db.query(FundReleaseRecord).filter(FundReleaseRecord.release_id == release_id).first()
        if release:
            eligibility = FundReleaseService.evaluate_eligibility(db, release)
            release.eligibility_checks = eligibility["checks"]
            release.eligibility_status = "eligible" if eligibility["eligible"] else "ineligible"
            release.compliance_score = eligibility["compliance"]["score"] if "compliance" in eligibility else 0.0
            if not eligibility["eligible"]:
                db.commit()
                raise ValueError("Fund release blocked: " + ", ".join(eligibility["reasons"]))
            release.status = ReleaseStatus.APPROVED
            release.approval_date = datetime.utcnow()
            if approval_notes:
                release.approval_notes = approval_notes
            db.commit()
            db.refresh(release)
        return release
    
    @staticmethod
    def release_funds(db: Session, release_id: str) -> Optional[FundReleaseRecord]:
        """Mark funds as released."""
        release = db.query(FundReleaseRecord).filter(FundReleaseRecord.release_id == release_id).first()
        if release and release.status == ReleaseStatus.APPROVED:
            release.status = ReleaseStatus.RELEASED
            release.release_date = datetime.utcnow()
            release.remaining_amount = release.sanction_amount - release.released_amount
            db.commit()
            db.refresh(release)
        return release
    
    @staticmethod
    def reject_release(
        db: Session,
        release_id: str,
        reason: Optional[str] = None,
    ) -> Optional[FundReleaseRecord]:
        """Reject a fund release request."""
        release = db.query(FundReleaseRecord).filter(FundReleaseRecord.release_id == release_id).first()
        if release:
            release.status = ReleaseStatus.REJECTED
            if reason:
                release.approval_notes = reason
            db.commit()
            db.refresh(release)
        return release
