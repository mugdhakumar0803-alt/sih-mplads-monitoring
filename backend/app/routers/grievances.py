from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.grievance import Grievance, GrievanceStatus, GrievanceSeverity
from ..services.grievance_service import GrievanceService

router = APIRouter(
    prefix="/grievances",
    tags=["Grievances"]
)


@router.get("/")
async def list_grievances(
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
        db, work_id=work_id, status=grievance_status, skip=skip, limit=limit
    )
    
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific grievance."""
    grievance = GrievanceService.get_grievance_by_id(db, grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """File a new grievance."""
    grievance = GrievanceService.create_grievance(db, grievance_data)
    return {
        "grievance_id": grievance.grievance_id,
        "status": "registered",
        "message": "Grievance filed successfully",
    }


@router.put("/{grievance_id}/status")
async def update_grievance_status(
    grievance_id: str,
    new_status: str,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update grievance status."""
    try:
        status_enum = GrievanceStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    grievance = GrievanceService.update_grievance_status(
        db, grievance_id, status_enum, resolution_notes
    )
    
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    
    return {
        "grievance_id": grievance.grievance_id,
        "status": grievance.status,
        "updated_at": grievance.updated_at,
    }


@router.post("/{grievance_id}/escalate")
async def escalate_grievance(
    grievance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Escalate a grievance."""
    grievance = GrievanceService.escalate_grievance(db, grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    
    return {
        "grievance_id": grievance.grievance_id,
        "is_escalated": True,
        "message": "Grievance escalated for priority review",
    }

