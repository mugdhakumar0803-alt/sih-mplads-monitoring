from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.work import Work
from ..services.work_service import WorkService

router = APIRouter(
    prefix="/works",
    tags=["Works"]
)


@router.get("/")
async def list_works(
    state: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of MPLADS works with optional filtering."""
    works = WorkService.get_all_works(db, state=state, skip=skip, limit=limit)
    return {
        "total": len(works),
        "works": [
            {
                "work_id": w.work_id,
                "title": w.work_title,
                "category": w.category,
                "state": w.state,
                "status": w.status,
                "allocation_amount": w.allocation_amount,
                "risk_score": w.risk_score,
                "risk_level": w.risk_level,
            }
            for w in works
        ]
    }


@router.get("/dashboard/stats")
async def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    works = db.query(Work).all()
    total = len(works)
    completed = sum(1 for work in works if getattr(work.status, "value", work.status) == "Completed")
    sanctioned = sum(work.allocation_amount or 0 for work in works)
    high_risk = sum(1 for work in works if work.risk_level == "high")
    breakdown = {}
    for work in works:
        status = getattr(work.status, "value", work.status)
        breakdown[status] = breakdown.get(status, 0) + 1
    return {
        "total_works": total,
        "total_sanctioned": sanctioned,
        "completed": completed,
        "active_anomalies": high_risk,
        "status_breakdown": breakdown,
    }


@router.get("/{work_id}")
async def get_work(
    work_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific work."""
    work = WorkService.get_work_by_id(db, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    return {
        "work_id": work.work_id,
        "title": work.work_title,
        "category": work.category,
        "state": work.state,
        "status": work.status,
        "allocation_amount": work.allocation_amount,
        "risk_score": work.risk_score,
        "risk_level": work.risk_level,
        "anomaly_drivers": work.anomaly_drivers,
        "grievance_count": work.citizen_grievance_count,
        "days_since_last_photo": work.days_since_last_photo,
    }


@router.post("/{work_id}/risk-assessment")
async def assess_work_risk(
    work_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate risk assessment for a work."""
    work = WorkService.get_work_by_id(db, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    return {
        "work_id": work.work_id,
        "risk_score": work.risk_score,
        "risk_level": work.risk_level,
        "drivers": work.anomaly_drivers or [],
    }
