from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..database import get_db
from ..models.alert import Alert, AlertSeverity
from ..models.grievance import Grievance, GrievanceStatus
from ..models.user import User, UserRole
from ..models.work import Work

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def _visible_work_query(db: Session, user: User):
    query = db.query(Work)
    if user.role == UserRole.MP:
        return query.filter(Work.constituency == user.constituency) if user.constituency else query.filter(Work.mp_name == user.username)
    if user.role == UserRole.STATE_OFFICIAL and user.state:
        return query.filter(Work.state == user.state)
    if user.role == UserRole.DISTRICT_OFFICIAL and user.district_id:
        return query.filter(Work.district == user.district_id)
    if user.role == UserRole.CITIZEN and user.state:
        return query.filter(Work.state == user.state)
    return query


@router.get("")
def list_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    works = _visible_work_query(db, current_user).all()
    work_ids = [work.work_id for work in works]
    alerts = db.query(Alert).filter(Alert.work_id.in_(work_ids) if work_ids else False).order_by(Alert.created_at.desc()).limit(100).all()
    grievances = db.query(Grievance).filter(Grievance.work_id.in_(work_ids), Grievance.status.notin_([GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED])).all() if work_ids else []
    existing = {(alert.alert_type, alert.work_id) for alert in alerts}
    generated = []
    for work in works:
        if work.risk_level == "high" and ("HIGH_RISK", work.work_id) not in existing:
            generated.append(Alert(severity=AlertSeverity.HIGH, alert_type="HIGH_RISK", work_id=work.work_id, mp_name=work.mp_name, message="High-risk project requires verification."))
    for grievance in grievances:
        key = ("OPEN_GRIEVANCE", grievance.work_id)
        if key not in existing:
            generated.append(Alert(severity=AlertSeverity.WARNING, alert_type="OPEN_GRIEVANCE", work_id=grievance.work_id, message="An unresolved citizen grievance is linked to this project."))
    if generated:
        db.add_all(generated)
        db.commit()
        alerts.extend(generated)
    return {"alerts": [{"alert_id": str(alert.id), "severity": alert.severity.value, "type": alert.alert_type, "work_id": alert.work_id, "message": alert.message, "is_read": alert.is_read, "created_at": alert.created_at} for alert in alerts]}


@router.post("/{alert_id}/read")
def mark_read(alert_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return {"updated": False}
    alert.is_read = True
    db.commit()
    return {"updated": True}
