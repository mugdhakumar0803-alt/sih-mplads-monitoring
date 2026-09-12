# Business logic for MPLADS works
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.work import Work, WorkStatus
from ..ml.anomaly import score_works, WorkFeatures


class WorkService:
    """Service for work-related operations."""
    
    @staticmethod
    def get_all_works(
        db: Session,
        state: Optional[str] = None,
        status: Optional[WorkStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Work]:
        """Get works with optional filtering."""
        query = db.query(Work)
        
        if state:
            query = query.filter(Work.state == state)
        if status:
            query = query.filter(Work.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_work_by_id(db: Session, work_id: str) -> Optional[Work]:
        """Get a single work by ID."""
        return db.query(Work).filter(Work.work_id == work_id).first()
    
    @staticmethod
    def create_work(db: Session, work_data: dict) -> Work:
        """Create a new work record."""
        new_work = Work(**work_data)
        db.add(new_work)
        db.commit()
        db.refresh(new_work)
        return new_work
    
    @staticmethod
    def update_work(db: Session, work_id: str, updates: dict) -> Optional[Work]:
        """Update an existing work record."""
        work = db.query(Work).filter(Work.work_id == work_id).first()
        if work:
            for key, value in updates.items():
                setattr(work, key, value)
            db.commit()
            db.refresh(work)
        return work
    
    @staticmethod
    def calculate_risk_scores(db: Session, works: List[Work]) -> List[dict]:
        """Calculate risk scores for works using ML model."""
        work_features = [
            WorkFeatures(
                work_id=w.work_id,
                cost_ratio_vs_category_median=1.0,  # Would come from training
                progress_vs_elapsed_time_ratio=0.5,
                days_since_last_photo=w.days_since_last_photo or 30,
                citizen_grievance_count=float(w.citizen_grievance_count or 0),
            )
            for w in works
        ]
        
        return score_works(work_features)
