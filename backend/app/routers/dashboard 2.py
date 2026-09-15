"""
Owner: Full-stack/Backend.
Location: backend/app/routers/dashboard.py

Real, database-backed summary stats — this is what stops the frontend
from ever showing a hardcoded number. Field names below match what's
actually in your live models/work.py and models/grievance.py
(work_id, work_title, state, status, allocation_amount, risk_score,
risk_level — confirmed from your real fund_release.py and chatbot.py).

If your Work.status / Grievance.status are Enum columns rather than
plain strings, SQLAlchemy handles the comparison the same way either
side — no change needed unless you see a type error, in which case
compare against the Enum member instead of the raw string.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.work import Work
from ..models.grievance import Grievance
from ..models.fund_release import FundReleaseRecord, ReleaseStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    total = db.query(Work).count()
    sanctioned = db.query(Work).filter(Work.status == "sanctioned").count()
    in_progress = db.query(Work).filter(Work.status == "in_progress").count()
    completed = db.query(Work).filter(Work.status == "completed").count()

    high_risk = db.query(Work).filter(Work.risk_level == "high").count()
    medium_risk = db.query(Work).filter(Work.risk_level == "medium").count()
    low_risk = db.query(Work).filter(Work.risk_level == "low").count()

    open_grievances = db.query(Grievance).filter(Grievance.status != "resolved").count()
    escalated_grievances = db.query(Grievance).filter(Grievance.is_escalated == True).count()  # noqa: E712

    blocked_releases = (
        db.query(FundReleaseRecord)
        .filter(FundReleaseRecord.status == ReleaseStatus.REJECTED)
        .count()
    )

    return {
        "total_projects": total,
        "sanctioned": sanctioned,
        "in_progress": in_progress,
        "completed": completed,
        "risk_breakdown": {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk,
        },
        "open_grievances": open_grievances,
        "escalated_grievances": escalated_grievances,
        "blocked_fund_releases": blocked_releases,
    }


@router.get("/top-risk-projects")
def top_risk_projects(limit: int = 5, db: Session = Depends(get_db)):
    """Feeds the 'Top Risk Projects' panel on the homepage dashboard."""
    works = (
        db.query(Work)
        .filter(Work.risk_score.isnot(None))
        .order_by(Work.risk_score.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "work_id": w.work_id,
            "title": w.work_title,
            "state": w.state,
            "risk_score": w.risk_score,
            "risk_level": w.risk_level,
        }
        for w in works
    ]