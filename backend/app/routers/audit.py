from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User, UserRole
from ..models.audit import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("/logs")
async def get_audit_logs(
    request: Request,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.ADMIN, UserRole.MINISTRY}:
        raise HTTPException(status_code=403, detail="Audit logs are restricted")

    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(min(limit, 500))
        .all()
    )

    return {
        "total": len(logs),
        "logs": [
            {
                "id": x.id,
                "user_id": x.user_id,
                "username": x.username,
                "role": x.role,
                "action": x.action,
                "resource_type": x.resource_type,
                "resource_id": x.resource_id,
                "ip_address": x.ip_address,
                "status": x.status,
                "details": x.details,
                "timestamp": x.timestamp,
            }
            for x in logs
        ],
    }
