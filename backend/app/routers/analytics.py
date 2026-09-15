"""
Owner: Full-stack/Backend.
Location: backend/app/routers/analytics.py

REWRITTEN to match the REAL columns on your live models (work.py,
grievance.py, rating.py, fund_release.py). The previous version
referenced fields that don't exist anywhere in your schema
(w.name, w.allocated_amount, w.physical_progress_pct, w.released_amount,
w.utilized_amount, work.anomaly_explanations) — every one of those
would raise an AttributeError the moment real data existed, and
/compliance-score was hardcoded numbers with no database query at all.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from ..database import get_db
from ..models.work import Work, WorkStatus
from ..models.grievance import Grievance, GrievanceStatus
from ..models.rating import Rating
from ..models.fund_release import FundReleaseRecord, ReleaseStatus
from ..ml.compliance_engine import compute_priority_area_percent, PRIORITY_AREA_REQUIRED_PERCENT

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# 1. Fund Utilization by Work (stacked bar)
@router.get("/fund-utilization")
def fund_utilization(db: Session = Depends(get_db)):
    works = db.query(Work).limit(20).all()
    result = []
    for w in works:
        released = (
            db.query(func.coalesce(func.sum(FundReleaseRecord.released_amount), 0.0))
            .filter(
                FundReleaseRecord.work_id == w.work_id,
                FundReleaseRecord.status == ReleaseStatus.RELEASED,
            )
            .scalar()
        )
        result.append({
            "work": w.work_title,
            "allocated": w.allocation_amount,
            "released": released,
            "remaining": max(0.0, w.allocation_amount - released),
        })
    return result


# 2. Work Progress vs Fund Utilization (dual line)
@router.get("/progress-vs-utilization")
def progress_vs_utilization(db: Session = Depends(get_db)):
    # There's no physical_progress_pct column yet — approximate progress
    # from status until milestone-level tracking exists. Sanctioned = just
    # started, Ongoing = midway, Completed = done. Flag this as an
    # approximation, not a fabricated precise number.
    status_progress = {
        WorkStatus.UNSANCTIONED: 0,
        WorkStatus.SANCTIONED: 10,
        WorkStatus.ONGOING: 50,
        WorkStatus.COMPLETED: 100,
        WorkStatus.REJECTED: 0,
    }
    works = db.query(Work).all()
    result = []
    for w in works:
        released = (
            db.query(func.coalesce(func.sum(FundReleaseRecord.released_amount), 0.0))
            .filter(
                FundReleaseRecord.work_id == w.work_id,
                FundReleaseRecord.status == ReleaseStatus.RELEASED,
            )
            .scalar()
        )
        result.append({
            "work": w.work_title,
            "month": w.updated_at.strftime("%b") if w.updated_at else None,
            "physical_progress_pct_estimated": status_progress.get(w.status, 0),
            "financial_utilization_pct": round((released / w.allocation_amount) * 100, 1)
            if w.allocation_amount else 0,
        })
    return result


# 3. Risk Distribution (donut)
@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(Work.risk_level, func.count(Work.id))
        .group_by(Work.risk_level)
        .all()
    )
    return [{"level": level or "not assessed", "count": count} for level, count in rows]


# 4. Constituency Ranking (horizontal bar) — ranked by real completion rate
@router.get("/constituency-ranking")
def constituency_ranking(metric: str = "completion", db: Session = Depends(get_db)):
    rows = (
        db.query(
            Work.constituency,
            func.sum(case((Work.status == WorkStatus.COMPLETED, 1), else_=0)),
            func.count(Work.id),
        )
        .group_by(Work.constituency)
        .all()
    )
    scored = [
        {"constituency": c, "score": round((completed / total) * 100, 1) if total else 0}
        for c, completed, total in rows
    ]
    return sorted(scored, key=lambda r: r["score"], reverse=True)[:10]


# 5. Citizen Grievance status breakdown
@router.get("/citizen-verification")
def citizen_verification(db: Session = Depends(get_db)):
    rows = (
        db.query(Grievance.status, func.count(Grievance.id))
        .group_by(Grievance.status)
        .all()
    )
    return [{"status": getattr(s, "value", s), "count": c} for s, c in rows]


# 5b. Rating distribution (rounded to whole stars, 1-5)
@router.get("/rating-distribution")
def rating_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(func.round(Rating.overall_score).label("stars"), func.count(Rating.id))
        .group_by("stars")
        .order_by("stars")
        .all()
    )
    return [{"stars": int(stars), "count": count} for stars, count in rows]


# 6. Grievance Resolution Trend (monthly)
@router.get("/grievance-trend")
def grievance_trend(db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.to_char(Grievance.created_at, "Mon").label("month"),
            func.count(Grievance.id).label("filed"),
            func.sum(case((Grievance.status == GrievanceStatus.RESOLVED, 1), else_=0)).label("resolved"),
        )
        .group_by("month")
        .all()
    )
    return [{"month": m, "filed": f, "resolved": r or 0} for m, f, r in rows]


# 7. Compliance Score — REAL priority-area compliance, computed per MP from
# actual work categories/amounts. SC/ST honestly reported as not yet
# computable (see ml/compliance_engine.py) rather than faked.
@router.get("/compliance-score")
def compliance_score(db: Session = Depends(get_db)):
    works = db.query(Work).all()
    by_mp: dict[str, list[dict]] = {}
    for w in works:
        by_mp.setdefault(w.mp_name, []).append({
            "category": getattr(w.category, "value", w.category),
            "sanctioned_amount": w.allocation_amount,
        })

    if not works:
        return {
            "priority_area_avg_percent": None,
            "priority_area_required_percent": PRIORITY_AREA_REQUIRED_PERCENT,
            "sc_st_allocation": "not_computable_yet",
            "note": "No works in the database yet — import real data first.",
        }

    percentages = [compute_priority_area_percent(w) for w in by_mp.values()]
    avg_priority = round(sum(percentages) / len(percentages), 1) if percentages else 0.0

    return {
        "priority_area_avg_percent": avg_priority,
        "priority_area_required_percent": PRIORITY_AREA_REQUIRED_PERCENT,
        "sc_st_allocation": "not_computable_yet",
        "note": (
            "Priority-area compliance is computed live from real work "
            "categories and amounts. SC/ST allocation compliance needs a "
            "village/constituency SC-ST designation reference dataset "
            "that hasn't been sourced yet — reported honestly as pending, "
            "not faked."
        ),
    }


# 8. AI Risk Drivers for a single work (horizontal bar)
@router.get("/risk-drivers/{work_id}")
def risk_drivers(work_id: str, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if not work:
        return {"work_id": work_id, "risk_score": None, "drivers": []}
    return {
        "work_id": work_id,
        "risk_score": work.risk_score,
        "drivers": work.anomaly_drivers or [],
    }
