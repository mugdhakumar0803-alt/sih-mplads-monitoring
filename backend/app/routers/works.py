from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..auth.dependencies import get_current_user, write_audit
from ..auth.scope import require_work_scope
from ..models.user import User
from ..models.work import Work
from ..services.work_service import WorkService

router = APIRouter(prefix="/works", tags=["Works"])


def serialize_work(w):
    return {
        "work_id": w.work_id,
        "title": w.work_title,
        "category": w.category,
        "state": w.state,
        "status": w.status,
        "allocation_amount": w.allocation_amount,
        "risk_score": w.risk_score,
        "risk_level": w.risk_level,
    }


@router.get("/")
async def list_works(
    request: Request,
    state: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    works = WorkService.get_all_works(
        db, user=current_user, state=state, skip=skip, limit=limit
    )
    write_audit(
        db, current_user, "WORKS_LIST_VIEWED", request,
        resource_type="work", status_value="SUCCESS",
    )
    return {"total": len(works), "works": [serialize_work(w) for w in works]}


@router.get("/{work_id}")
async def get_work(
    work_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    work = WorkService.get_work_by_id(db, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    try:
        require_work_scope(work, current_user)
    except HTTPException:
        write_audit(
            db, current_user, "WORK_SCOPE_VIOLATION", request,
            resource_type="work", resource_id=work_id,
            status_value="FAILURE",
        )
        raise

    write_audit(
        db, current_user, "WORK_VIEWED", request,
        resource_type="work", resource_id=work_id,
    )

    return {
        **serialize_work(work),
        "anomaly_drivers": work.anomaly_drivers,
        "grievance_count": work.citizen_grievance_count,
        "days_since_last_photo": work.days_since_last_photo,
    }


@router.post("/{work_id}/risk-assessment")
async def assess_work_risk(
    work_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    work = WorkService.get_work_by_id(db, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    require_work_scope(work, current_user)

    write_audit(
        db, current_user, "WORK_RISK_ASSESSMENT_VIEWED", request,
        resource_type="work", resource_id=work_id,
    )

    return {
        "work_id": work.work_id,
        "risk_score": work.risk_score,
        "risk_level": work.risk_level,
        "drivers": work.anomaly_drivers or [],
    }
