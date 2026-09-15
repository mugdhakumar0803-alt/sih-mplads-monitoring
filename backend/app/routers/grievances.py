from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..auth.dependencies import get_current_user, write_audit
from ..models.user import User, UserRole
from ..models.grievance import Grievance, GrievanceStatus, GrievanceSeverity
from ..models.work import Work
from ..services.grievance_service import GrievanceService

router = APIRouter(
    prefix="/grievances",
    tags=["Grievances"]
)

OFFICIAL_ROLES = {
    UserRole.ADMIN, UserRole.MINISTRY, UserRole.STATE_OFFICIAL,
    UserRole.DISTRICT_OFFICIAL, UserRole.MP,
}


@router.get("/")
async def list_grievances(
    request: Request,
    work_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of grievances."""
    grievance_status = None
    if status:
        try:
            grievance_status = GrievanceStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    grievances = GrievanceService.get_all_grievances(
        db,
        current_user=current_user,
        work_id=work_id,
        status=grievance_status,
        skip=skip,
        limit=limit,
    )

    write_audit(db, current_user, "GRIEVANCES_LIST_VIEWED", request, resource_type="grievance")

    return {
        "total": len(grievances),
        "grievances": [
            {
                "grievance_id": g.grievance_id,
                "work_id": g.work_id,
                "citizen_name": g.citizen_name,
                "description": g.description,
                "severity": g.severity,
                "status": g.status,
                "is_escalated": g.is_escalated,
                "created_at": g.created_at,
            }
            for g in grievances
        ]
    }


@router.get("/{grievance_id}")
async def get_grievance(
    grievance_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific grievance."""
    grievance = GrievanceService.get_grievance_by_id(db, grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")

    write_audit(
        db, current_user, "GRIEVANCE_VIEWED", request,
        resource_type="grievance", resource_id=grievance_id,
    )

    return {
        "grievance_id": grievance.grievance_id,
        "work_id": grievance.work_id,
        "citizen_name": grievance.citizen_name,
        "citizen_contact": grievance.citizen_contact,
        "citizen_email": grievance.citizen_email,
        "description": grievance.description,
        "severity": grievance.severity,
        "status": grievance.status,
        "resolution_notes": grievance.resolution_notes,
        "is_escalated": grievance.is_escalated,
        "created_at": grievance.created_at,
        "updated_at": grievance.updated_at,
    }


@router.post("/file")
async def file_grievance(
    grievance_data: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """File a new grievance. Open to any authenticated user, including citizens."""
    work_id = grievance_data.get("work_id")
    if not work_id or not db.query(Work).filter(Work.work_id == work_id).first():
        raise HTTPException(status_code=400, detail="A valid work_id is required")
    grievance_data["filed_by_user_id"] = current_user.id
    grievance_data["filed_by_role"] = current_user.role.value
    grievance = GrievanceService.create_grievance(db, grievance_data)

    write_audit(
        db, current_user, "GRIEVANCE_FILED", request,
        resource_type="grievance", resource_id=grievance.grievance_id,
    )

    return {
        "grievance_id": grievance.grievance_id,
        "status": "registered",
        "message": "Grievance filed successfully",
    }


@router.post("/run-sla-check")
async def run_sla_check(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in OFFICIAL_ROLES:
        raise HTTPException(status_code=403, detail="Only officials may run SLA checks")
    open_grievances = db.query(Grievance).filter(Grievance.status.notin_([GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED])).all()
    escalated = []
    for grievance in open_grievances:
        previous = grievance.current_escalation_level
        updated = GrievanceService.check_and_apply_escalation(db, grievance.grievance_id)
        if updated and updated.current_escalation_level != previous:
            escalated.append({"grievance_id": updated.grievance_id, "previous_level": previous, "new_level": updated.current_escalation_level})
    write_audit(db, current_user, "SLA_CHECK_RUN", request, resource_type="grievance", details={"escalated": len(escalated)})
    return {"checked": len(open_grievances), "escalated": escalated}


@router.put("/{grievance_id}/status")
async def update_grievance_status(
    grievance_id: str,
    new_status: str,
    request: Request,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update grievance status. Restricted to officials."""
    if current_user.role not in OFFICIAL_ROLES:
        write_audit(
            db, current_user, "GRIEVANCE_STATUS_UPDATE_DENIED", request,
            resource_type="grievance", resource_id=grievance_id, status_value="FAILURE",
        )
        raise HTTPException(status_code=403, detail="Only officials may update grievance status")

    try:
        status_enum = GrievanceStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    grievance = GrievanceService.update_grievance_status(
        db, grievance_id, status_enum, resolution_notes
    )
    
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")

    write_audit(
        db, current_user, "GRIEVANCE_STATUS_UPDATED", request,
        resource_type="grievance", resource_id=grievance_id,
        details={"new_status": new_status},
    )

    return {
        "grievance_id": grievance.grievance_id,
        "status": grievance.status,
        "updated_at": grievance.updated_at,
    }


@router.post("/{grievance_id}/escalate")
async def escalate_grievance(
    grievance_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Escalate a grievance. Restricted to officials."""
    if current_user.role not in OFFICIAL_ROLES:
        write_audit(
            db, current_user, "GRIEVANCE_ESCALATE_DENIED", request,
            resource_type="grievance", resource_id=grievance_id, status_value="FAILURE",
        )
        raise HTTPException(status_code=403, detail="Only officials may escalate grievances")

    grievance = GrievanceService.escalate_grievance(db, grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")

    write_audit(
        db, current_user, "GRIEVANCE_ESCALATED", request,
        resource_type="grievance", resource_id=grievance_id,
    )

    return {
        "grievance_id": grievance.grievance_id,
        "is_escalated": True,
        "message": "Grievance escalated for priority review",
    }

