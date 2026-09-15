from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..auth.dependencies import get_current_user, write_audit
from ..auth.scope import require_work_scope
from ..models.user import User
from ..models.work import Work, WorkStatus, WorkCategory
from ..services.work_service import WorkService

router = APIRouter(prefix="/works", tags=["Works"])


def serialize_work(w):
    return {
        "work_id": w.work_id,
        "title": w.work_title,
        "category": getattr(w.category, "value", w.category),
        "state": w.state,
        "status": getattr(w.status, "value", w.status),
        "allocation_amount": w.allocation_amount,
        "sanctioned_amount": w.sanctioned_amount,
        "expenditure_amount": w.expenditure_amount,
        "recommended_date": w.recommended_date,
        "sanction_date": w.sanction_date,
        "completion_date": w.completion_date,
        "district": w.district,
        "block": w.block,
        "village": w.village,
        "ward": w.ward,
        "source_dataset": w.source_dataset,
        "source_record_id": w.source_record_id,
        "risk_score": w.risk_score,
        "risk_level": w.risk_level,
    }


@router.get("/")
async def list_works(
    request: Request,
    state: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    district: Optional[str] = None,
    constituency: Optional[str] = None,
    category: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        status_filter = WorkStatus(status) if status else None
        category_filter = WorkCategory(category) if category else None
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    filters = dict(state=state, district=district, constituency=constituency, category=category_filter, risk_level=risk_level, search=search, status=status_filter, current_user=current_user)
    works = WorkService.get_all_works(db, skip=skip, limit=limit, **filters)
    total = WorkService.count_works(db, **filters)
    write_audit(
        db, current_user, "WORKS_LIST_VIEWED", request,
        resource_type="work", status_value="SUCCESS",
    )
    return {"total": total, "skip": skip, "limit": limit, "works": [serialize_work(w) for w in works]}


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
