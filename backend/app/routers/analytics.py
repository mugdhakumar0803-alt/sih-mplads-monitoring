from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.models import Work, Grievance, Rating
from app.models.work import WorkStatus
from app.models.grievance import GrievanceStatus

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# 1. Fund Utilization by Work (stacked bar)
@router.get("/fund-utilization")
def fund_utilization(db: Session = Depends(get_db)):
    works = db.query(Work).limit(20).all()
    return [
        {
            "work": w.work_title,
            "allocated": w.allocation_amount,
            "released": 0,
            "utilized": 0,
            "remaining": w.allocation_amount,
        }
        for w in works
    ]


# 2. Work Progress vs Fund Utilization (dual line, over time)
@router.get("/progress-vs-utilization")
def progress_vs_utilization(db: Session = Depends(get_db)):
    works = db.query(Work).all()
    return [
        {
            "work": w.work_title,
            "month": w.updated_at.strftime("%b") if w.updated_at else "N/A",
            "physical_progress_pct": 100 if w.status == WorkStatus.COMPLETED else 0,
            "financial_utilization_pct": 100 if w.status == WorkStatus.COMPLETED else 0,
        }
        for w in works
    ]


# 3. Risk Distribution (donut)
@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(Work.risk_level, func.count(Work.id))
        .group_by(Work.risk_level)
        .all()
    )
    return [{"level": level, "count": count} for level, count in rows]


# 4. Constituency / District Ranking (horizontal bar)
@router.get("/constituency-ranking")
def constituency_ranking(metric: str = "completion", db: Session = Depends(get_db)):
    # metric: completion | utilization | satisfaction | compliance
    rows = (
        db.query(Work.constituency, func.avg(
            case((Work.status == WorkStatus.COMPLETED, 100), else_=0)
        ).label("score"))
        .group_by(Work.constituency)
        .order_by(func.avg(Work.physical_progress_pct).desc())
        .limit(10)
        .all()
    )
    return [{"constituency": c, "score": round(score, 1)} for c, score in rows]


# 5. Citizen Verification status
@router.get("/citizen-verification")
def citizen_verification(db: Session = Depends(get_db)):
    rows = (
        db.query(Grievance.status, func.count(Grievance.id))
        .group_by(Grievance.status)
        .all()
    )
    return [{"status": s, "count": c} for s, c in rows]


# 5b. Rating distribution
@router.get("/rating-distribution")
def rating_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(Rating.overall_score, func.count(Rating.id))
        .group_by(Rating.overall_score)
        .all()
    )
    return [{"stars": score, "count": count} for score, count in rows]


# 6. Grievance Resolution Trend (line, monthly)
@router.get("/grievance-trend")
def grievance_trend(db: Session = Depends(get_db)):
    trend = {}
    grievances = db.query(Grievance).order_by(Grievance.created_at).all()
    for grievance in grievances:
        month = grievance.created_at.strftime("%Y-%m")
        summary = trend.setdefault(month, {"month": month, "filed": 0, "resolved": 0})
        summary["filed"] += 1
        if grievance.status == GrievanceStatus.RESOLVED:
            summary["resolved"] += 1
    return list(trend.values())


# 7. Compliance Score (bar)
@router.get("/compliance-score")
def compliance_score(db: Session = Depends(get_db)):
    # Adjust to however you currently compute each sub-score
    return [
        {"category": "SC/ST Allocation", "score": 82},
        {"category": "Priority Areas", "score": 75},
        {"category": "Fund Release Conditions", "score": 91},
        {"category": "Work Completion", "score": 68},
        {"category": "Documentation", "score": 88},
    ]


# 8. AI Risk Drivers for a single work (horizontal bar)
@router.get("/risk-drivers/{work_id}")
def risk_drivers(work_id: int, db: Session = Depends(get_db)):
    work = db.query(Work).get(work_id)
    # Pull directly from your anomaly model's explanation output
    return {
        "work_id": work_id,
        "risk_score": work.risk_score,
        "drivers": work.anomaly_explanations,  # e.g. [{"factor": "...", "impact": "High"}, ...]
    }