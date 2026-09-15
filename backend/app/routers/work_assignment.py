"""
Owner: Full-stack/Backend.
Location: backend/app/routers/work_assignment.py

This is the real-world MPLADS handoff that was missing: an MP does not
build anything directly. An MP RECOMMENDS a work for their constituency;
a District Authority then SANCTIONS it (formally approves it, which is
what actually triggers the fund pipeline). Two separate roles, two
separate actions, two separate audit trail entries — not one person
just "creating a work."
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User, UserRole
from ..models.work import Work
from ..auth.dependencies import require_role, get_current_user

router = APIRouter(prefix="/works", tags=["Work Assignment"])


@router.post("/recommend")
async def recommend_work(
    work_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.MP])),
):
    """
    Step 1 — an MP recommends a work for their own constituency.
    Status starts as 'recommended', NOT 'sanctioned' — no money is
    committed yet, this is just a proposal on record.
    """
    if current_user.constituency and work_data.get("constituency") != current_user.constituency:
        raise HTTPException(
            status_code=403,
            detail="You can only recommend works for your own constituency",
        )

    new_work = Work(
        work_id=work_data["work_id"],
        work_title=work_data["work_title"],
        category=work_data["category"],
        constituency=current_user.constituency,
        state=current_user.state,
        allocation_amount=work_data["allocation_amount"],
        status="recommended",
        recommended_by=current_user.id,
        recommended_at=datetime.utcnow(),
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
    """
    Step 2 — the District Authority formally approves an MP's
    recommendation. THIS is what actually authorizes the work to
    proceed and the fund pipeline to start. A District Authority can
    only sanction works within their own jurisdiction.
    """
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    if work.status != "recommended":
        raise HTTPException(status_code=400, detail=f"Cannot sanction a work with status '{work.status}' — must be 'recommended' first")

    if current_user.state and work.state != current_user.state:
        raise HTTPException(status_code=403, detail="You can only sanction works within your own state/district")

    work.status = "sanctioned"
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
    """A District Authority can also decline an MP's recommendation outright — e.g. non-permissible category."""
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    work.status = "rejected"
    work.rejection_reason = reason
    db.commit()
    return {"work_id": work.work_id, "status": work.status, "reason": reason}