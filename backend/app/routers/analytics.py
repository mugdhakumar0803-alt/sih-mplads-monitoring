from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Grievance, Rating, Work
from ..models.grievance import GrievanceStatus
from ..models.work import WorkStatus

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/fund-utilization")
def fund_utilization(db: Session = Depends(get_db)):
    return [{
        "work": work.work_title,
        "allocated": work.allocation_amount,
        "released": None,
        "utilized": work.expenditure_amount,
        "remaining": None if work.expenditure_amount is None else work.allocation_amount - work.expenditure_amount,
    } for work in db.query(Work).limit(20).all()]


@router.get("/progress-vs-utilization")
def progress_vs_utilization(db: Session = Depends(get_db)):
    return [{
        "work": work.work_title,
        "month": work.recommended_date.strftime("%Y-%m") if work.recommended_date else None,
        "physical_progress_pct": 100 if work.status == WorkStatus.COMPLETED else None,
        "financial_utilization_pct": (work.expenditure_amount / work.allocation_amount * 100) if work.expenditure_amount is not None and work.allocation_amount else None,
    } for work in db.query(Work).all()]


@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    counts = Counter(work.risk_level for work in db.query(Work).all() if work.risk_level)
    return [{"level": level, "count": count} for level, count in sorted(counts.items())]


@router.get("/constituency-ranking")
def constituency_ranking(metric: str = "completion", db: Session = Depends(get_db)):
    groups = {}
    for work in db.query(Work).all():
        groups.setdefault(work.constituency, []).append(work)
    rows = []
    for constituency, works in groups.items():
        completed = sum(work.status == WorkStatus.COMPLETED for work in works)
        rows.append({"constituency": constituency, "score": round(completed / len(works) * 100, 1) if works else None, "metric": metric})
    return sorted(rows, key=lambda row: row["score"] if row["score"] is not None else -1, reverse=True)[:10]


@router.get("/citizen-verification")
def citizen_verification(db: Session = Depends(get_db)):
    counts = Counter(getattr(grievance.status, "value", grievance.status) for grievance in db.query(Grievance).all())
    return [{"status": status, "count": count} for status, count in sorted(counts.items())]


@router.get("/rating-distribution")
def rating_distribution(db: Session = Depends(get_db)):
    counts = Counter(round(rating.overall_score) for rating in db.query(Rating).all())
    return [{"stars": stars, "count": count} for stars, count in sorted(counts.items())]


@router.get("/grievance-trend")
def grievance_trend(db: Session = Depends(get_db)):
    trend = {}
    for grievance in db.query(Grievance).order_by(Grievance.created_at).all():
        month = grievance.created_at.strftime("%Y-%m")
        row = trend.setdefault(month, {"month": month, "filed": 0, "resolved": 0})
        row["filed"] += 1
        if grievance.status == GrievanceStatus.RESOLVED:
            row["resolved"] += 1
    return list(trend.values())


@router.get("/compliance-score")
def compliance_score(db: Session = Depends(get_db)):
    works = db.query(Work).all()
    permissible = sum("religious" not in work.work_title.lower() for work in works)
    return [
        {"category": "Permissible work category", "score": round(permissible / len(works) * 100, 1) if works else None},
        {"category": "SC/ST allocation", "score": None, "status": "Data unavailable"},
        {"category": "National priority area", "score": None, "status": "Requires aggregate allocation input"},
    ]


@router.get("/risk-drivers/{work_id}")
def risk_drivers(work_id: str, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    return {"work_id": work_id, "risk_score": work.risk_score, "drivers": work.anomaly_drivers or [], "status": "Data unavailable" if work.risk_score is None else "calculated"}
