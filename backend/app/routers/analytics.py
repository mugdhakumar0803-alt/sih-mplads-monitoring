from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
            "released": None,
            "utilized": w.expenditure_amount,
            "remaining": None if w.expenditure_amount is None else w.allocation_amount - w.expenditure_amount,
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
            "month": w.recommended_date.strftime("%Y-%m") if w.recommended_date else None,
            "physical_progress_pct": 100 if w.status == WorkStatus.COMPLETED else None,
            "financial_utilization_pct": (w.expenditure_amount / w.allocation_amount * 100) if w.expenditure_amount is not None and w.allocation_amount else None,
        }
        for w in works
    ]


# 3. Risk Distribution (donut)
@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    counts = Counter(w.risk_level for w in db.query(Work).all() if w.risk_level)
    return [{"level": level, "count": count} for level, count in sorted(counts.items())]


# 4. Constituency / District Ranking (horizontal bar)
@router.get("/constituency-ranking")
def constituency_ranking(metric: str = "completion", db: Session = Depends(get_db)):
    # metric: completion | utilization | satisfaction | compliance
    groups = {}
    for work in db.query(Work).all():
        groups.setdefault(work.constituency, []).append(work)
    rows = []
    for constituency, works in groups.items():
        completed = sum(w.status == WorkStatus.COMPLETED for w in works)
        rows.append({"constituency": constituency, "score": round(completed / len(works) * 100, 1) if works else None, "metric": metric})
    return sorted(rows, key=lambda row: row["score"] if row["score"] is not None else -1, reverse=True)[:10]


# 5. Citizen Verification status
@router.get("/citizen-verification")
def citizen_verification(db: Session = Depends(get_db)):
    counts = Counter(getattr(g.status, "value", g.status) for g in db.query(Grievance).all())
    return [{"status": status, "count": count} for status, count in sorted(counts.items())]


# 5b. Rating distribution
@router.get("/rating-distribution")
def rating_distribution(db: Session = Depends(get_db)):
    counts = Counter(round(r.overall_score) for r in db.query(Rating).all())
    return [{"stars": stars, "count": count} for stars, count in sorted(counts.items())]


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
    works = db.query(Work).all()
    permissible = sum("religious" not in w.work_title.lower() for w in works)
    return [{"category": "Permissible work category", "score": round(permissible / len(works) * 100, 1) if works else None}, {"category": "SC/ST allocation", "score": None, "status": "Data unavailable"}, {"category": "National priority area", "score": None, "status": "Requires aggregate allocation input"}]


# 8. AI Risk Drivers for a single work (horizontal bar)
@router.get("/risk-drivers/{work_id}")
def risk_drivers(work_id: str, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    return {
        "work_id": work_id,
        "risk_score": work.risk_score,
        "drivers": work.anomaly_drivers or [],
        "status": "Data unavailable" if work.risk_score is None else "calculated",
    }