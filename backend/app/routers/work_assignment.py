"""
Owner: Full-stack/Backend.
Location: backend/app/routers/work_assignment.py

CORRECTED from the earlier version — your real WorkStatus enum already
had UNSANCTIONED/SANCTIONED matching this exact real-world handoff, so
this now uses those instead of inventing new string values.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User, UserRole
from ..models.work import Work, WorkStatus
from ..auth.dependencies import require_role

router = APIRouter(prefix="/works", tags=["Work Assignment"])


@router.post("/recommend")
async def recommend_work(
    work_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.MP])),
):
    """Step 1 — MP recommends a work for their own constituency.
    Starts as UNSANCTIONED — no money committed yet."""
    if current_user.constituency and work_data.get("constituency") != current_user.constituency:
        raise HTTPException(status_code=403, detail="You can only recommend works for your own constituency")

    new_work = Work(
        work_id=work_data["work_id"],
        mp_name=current_user.username,
        work_title=work_data["work_title"],
        category=work_data["category"],
        constituency=current_user.constituency,
        state=current_user.state,
        allocation_amount=work_data["allocation_amount"],
        recommended_date=datetime.utcnow(),
        status=WorkStatus.UNSANCTIONED,
        recommended_by=current_user.id,
    )
    db.add(new_work)
    db.commit()
    db.refresh(new_work)
    return {"work_id": new_work.work_id, "status": new_work.status, "recommended_by": current_user.username}


@router.post("/{work_id}/sanction")
async def sanction_work(
    work_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DISTRICT_OFFICIAL])),
):
    """Step 2 — District Authority formally approves. This is what
    actually authorizes the work and starts the fund pipeline."""
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    if work.status != WorkStatus.UNSANCTIONED:
        raise HTTPException(status_code=400, detail=f"Cannot sanction a work with status '{work.status}' — must be Unsanctioned first")

    if current_user.state and work.state != current_user.state:
        raise HTTPException(status_code=403, detail="You can only sanction works within your own state")

    work.status = WorkStatus.SANCTIONED
    work.sanctioned_by = current_user.id
    work.sanctioned_at = datetime.utcnow()
    db.commit()
    db.refresh(work)
    return {"work_id": work.work_id, "status": work.status, "sanctioned_by": current_user.username}


@router.post("/{work_id}/reject-recommendation")
async def reject_recommendation(
    work_id: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DISTRICT_OFFICIAL])),
):
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    work.status = WorkStatus.REJECTED
    work.rejection_reason = reason
    db.commit()
    return {"work_id": work.work_id, "status": work.status, "reason": reason}