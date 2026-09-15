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
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.work import Work, WorkStatus
from ..models.grievance import Grievance, GrievanceStatus
from ..models.fund_release import FundReleaseRecord, ReleaseStatus
from ..auth.dependencies import get_current_user
from ..models.user import User, UserRole

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Work)
    if current_user.role == UserRole.MP and current_user.constituency:
        query = query.filter(Work.constituency == current_user.constituency)
    elif current_user.role == UserRole.STATE_OFFICIAL and current_user.state:
        query = query.filter(Work.state == current_user.state)
    elif current_user.role == UserRole.DISTRICT_OFFICIAL and current_user.district_id:
        query = query.filter(Work.district == current_user.district_id)
    elif current_user.role == UserRole.CITIZEN:
        if current_user.state:
            query = query.filter(Work.state == current_user.state)
        if current_user.district_id:
            query = query.filter(Work.district == current_user.district_id)
        if current_user.constituency:
            query = query.filter(Work.constituency == current_user.constituency)
    works = query.all()
    total = len(works)
    sanctioned = sum(work.status == WorkStatus.SANCTIONED for work in works)
    in_progress = sum(work.status == WorkStatus.ONGOING for work in works)
    completed = sum(work.status == WorkStatus.COMPLETED for work in works)
    total_allocation = sum(work.allocation_amount or 0 for work in works)
    total_expenditure = sum(work.expenditure_amount or 0 for work in works if work.expenditure_amount is not None)
    expenditure_records = sum(1 for work in works if work.expenditure_amount is not None)
    delayed = sum(
        1 for work in works
        if work.completion_date and work.recommended_date and (work.completion_date - work.recommended_date).days > 365
    )
    high_risk = sum(work.risk_level == "high" for work in works)
    medium_risk = sum(work.risk_level == "medium" for work in works)
    low_risk = sum(work.risk_level == "low" for work in works)

    work_ids = [work.work_id for work in works]
    grievance_query = db.query(Grievance).filter(Grievance.work_id.in_(work_ids)) if work_ids else db.query(Grievance).filter(False)
    open_grievances = grievance_query.filter(Grievance.status != GrievanceStatus.RESOLVED).count()
    escalated_grievances = grievance_query.filter(Grievance.is_escalated == True).count()  # noqa: E712

    blocked_releases = (
        db.query(FundReleaseRecord)
        .filter(FundReleaseRecord.status == ReleaseStatus.REJECTED)
        .filter(FundReleaseRecord.work_id.in_(work_ids) if work_ids else False)
        .count()
    )

    return {
        "total_projects": total,
        "sanctioned": sanctioned,
        "in_progress": in_progress,
        "completed": completed,
        "recommended": sum(work.status == WorkStatus.UNSANCTIONED for work in works),
        "total_allocation": total_allocation,
        "total_expenditure": total_expenditure,
        "expenditure_records": expenditure_records,
        "utilization_percentage": round(total_expenditure / total_allocation * 100, 2) if total_allocation else None,
        "delayed_works": delayed,
        "data_limitations": ["Expenditure is unavailable for source rows without an expenditure field."] if expenditure_records < total else [],
        "risk_breakdown": {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk,
        },
        "open_grievances": open_grievances,
        "escalated_grievances": escalated_grievances,
        "blocked_fund_releases": blocked_releases,
    }


@router.get("/status-distribution")
def status_distribution(db: Session = Depends(get_db)):
    rows = db.query(Work.status).all()
    counts = Counter(getattr(status, "value", status) for (status,) in rows)
    return [{"status": status, "count": count} for status, count in sorted(counts.items())]


@router.get("/state-distribution")
def state_distribution(db: Session = Depends(get_db)):
    rows = db.query(Work.state).all()
    counts = Counter(state for (state,) in rows if state)
    return [{"state": state, "count": count} for state, count in counts.most_common()]


@router.get("/states")
def available_states(db: Session = Depends(get_db)):
    rows = db.query(Work.state).distinct().order_by(Work.state).all()
    return {"states": [state for (state,) in rows if state]}


@router.get("/category-distribution")
def category_distribution(db: Session = Depends(get_db)):
    rows = db.query(Work.category).all()
    counts = Counter(getattr(category, "value", category) for (category,) in rows)
    return [{"category": category, "count": count} for category, count in counts.most_common()]


@router.get("/financial-summary")
def financial_summary(db: Session = Depends(get_db)):
    works = db.query(Work).all()
    return {
        "allocation": sum(work.allocation_amount or 0 for work in works),
        "expenditure": sum(work.expenditure_amount or 0 for work in works if work.expenditure_amount is not None),
        "expenditure_available_for": sum(1 for work in works if work.expenditure_amount is not None),
        "total_works": len(works),
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