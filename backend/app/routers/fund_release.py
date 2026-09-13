from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..auth.dependencies import get_current_user, require_role
from ..models.user import User, UserRole
from ..models.fund_release import FundReleaseRecord, ReleaseStatus
from ..services.fund_release_service import FundReleaseService

router = APIRouter(
    prefix="/fund-release",
    tags=["Fund Release"]
)


@router.get("/")
async def list_fund_releases(
    work_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of fund release records."""
    release_status = None
    if status:
        try:
            release_status = ReleaseStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    releases = FundReleaseService.get_all_releases(
        db, work_id=work_id, status=release_status, skip=skip, limit=limit
    )
    
    return {
        "total": len(releases),
        "releases": [
            {
                "release_id": r.release_id,
                "work_id": r.work_id,
                "sanction_amount": r.sanction_amount,
                "released_amount": r.released_amount,
                "status": r.status,
                "eligibility_status": r.eligibility_status,
                "compliance_score": r.compliance_score,
            }
            for r in releases
        ]
    }


@router.get("/{release_id}")
async def get_fund_release(
    release_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a fund release record."""
    release = FundReleaseService.get_release_by_id(db, release_id)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    return {
        "release_id": release.release_id,
        "work_id": release.work_id,
        "sanction_amount": release.sanction_amount,
        "released_amount": release.released_amount,
        "remaining_amount": release.remaining_amount,
        "status": release.status,
        "eligibility_status": release.eligibility_status,
        "compliance_score": release.compliance_score,
        "approval_notes": release.approval_notes,
    }


@router.post("/{release_id}/approve")
async def approve_fund_release(
    release_id: str,
    approval_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DISTRICT_OFFICIAL)),
):
    """Approve a fund release request."""
    release = FundReleaseService.approve_release(db, release_id, approval_notes)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    return {"status": "approved", "release_id": release.release_id}


@router.post("/{release_id}/release")
async def release_funds(
    release_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STATE_OFFICIAL)),
):
    """Release funds for an approved request."""
    release = FundReleaseService.release_funds(db, release_id)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found or not approved")
    
    return {"status": "released", "amount": release.released_amount}


@router.post("/{release_id}/reject")
async def reject_fund_release(
    release_id: str,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DISTRICT_OFFICIAL)),
):
    """Reject a fund release request."""
    release = FundReleaseService.reject_release(db, release_id, reason)
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    
    return {"status": "rejected", "release_id": release.release_id}
