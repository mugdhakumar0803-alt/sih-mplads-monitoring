from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db          # adjust import to your actual db session
from models import Work, Grievance, CitizenFeedback  # adjust to your actual models

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# 1. Fund Utilization by Work (stacked bar)
@router.get("/fund-utilization")
def fund_utilization(db: Session = Depends(get_db)):
    works = db.query(Work).limit(20).all()   # or filter by constituency/MP
    return [
        {
            "work": w.name,
            "allocated": w.allocated_amount,
            "released": w.released_amount,
            "utilized": w.utilized_amount,
            "remaining": w.allocated_amount - w.utilized_amount,
        }
        for w in works
    ]


# 2. Work Progress vs Fund Utilization (dual line, over time)
@router.get("/progress-vs-utilization")
def progress_vs_utilization(db: Session = Depends(get_db)):
    works = db.query(Work).all()
    return [
        {
            "work": w.name,
            "month": w.last_updated.strftime("%b"),
            "physical_progress_pct": w.physical_progress_pct,
            "financial_utilization_pct": (w.utilized_amount / w.allocated_amount) * 100
            if w.allocated_amount else 0,
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
        db.query(Work.constituency, func.avg(Work.physical_progress_pct).label("score"))
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
        db.query(CitizenFeedback.status, func.count(CitizenFeedback.id))
        .group_by(CitizenFeedback.status)
        .all()
    )
    return [{"status": s, "count": c} for s, c in rows]


# 5b. Rating distribution
@router.get("/rating-distribution")
def rating_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(CitizenFeedback.rating, func.count(CitizenFeedback.id))
        .group_by(CitizenFeedback.rating)
        .all()
    )
    return [{"stars": r, "count": c} for r, c in rows]


# 6. Grievance Resolution Trend (line, monthly)
@router.get("/grievance-trend")
def grievance_trend(db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.to_char(Grievance.filed_on, 'Mon').label("month"),
            func.count(Grievance.id).label("filed"),
            func.sum(func.cast(Grievance.status == "resolved", func.Integer())).label("resolved"),
        )
        .group_by("month")
        .all()
    )
    return [{"month": m, "filed": f, "resolved": r or 0} for m, f, r in rows]


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