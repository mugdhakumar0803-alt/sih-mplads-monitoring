"""
Owner: Full-stack/Backend.
Location: backend/app/routers/leaderboard.py

Public accountability leaderboard, split by house since Lok Sabha and
Rajya Sabha MPs have different mandates and shouldn't be ranked against
each other in one mixed list.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.work import Work
from ..models.grievance import Grievance
from ..models.user import User, ParliamentHouse

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


def _compute_mp_scores(db: Session, house: ParliamentHouse | None = None):
    mp_query = db.query(User).filter(User.role == "mp", User.approval_status == "approved")
    if house:
        mp_query = mp_query.filter(User.house == house)
    mps = mp_query.all()

    results = []
    for mp in mps:
        works = db.query(Work).filter(Work.constituency == mp.constituency).all()
        if not works:
            continue

        total_works = len(works)
        completed_works = sum(1 for w in works if getattr(w.status, "value", w.status) == "completed")
        avg_risk_score = sum(w.risk_score or 0 for w in works) / total_works

        work_ids = [w.work_id for w in works]
        total_grievances = db.query(Grievance).filter(Grievance.work_id.in_(work_ids)).count()
        resolved_grievances = (
            db.query(Grievance)
            .filter(Grievance.work_id.in_(work_ids), Grievance.status == "resolved")
            .count()
        )
        resolution_rate = (resolved_grievances / total_grievances) if total_grievances else 1.0

        # Simple composite score — higher is better. Completion rate and
        # grievance resolution count positively; average risk counts
        # negatively (lower risk works are better).
        completion_rate = completed_works / total_works
        performance_score = round(
            (completion_rate * 0.4) + (resolution_rate * 0.3) + ((1 - avg_risk_score) * 0.3),
            3,
        )

        results.append({
            "mp_name": mp.username,
            "constituency": mp.constituency,
            "state": mp.state,
            "house": mp.house,
            "total_works": total_works,
            "completion_rate": round(completion_rate, 3),
            "avg_risk_score": round(avg_risk_score, 3),
            "grievance_resolution_rate": round(resolution_rate, 3),
            "performance_score": performance_score,
        })

    return sorted(results, key=lambda r: r["performance_score"], reverse=True)


@router.get("")
async def get_leaderboard(
    house: ParliamentHouse | None = Query(None, description="Filter to lok_sabha or rajya_sabha only"),
    db: Session = Depends(get_db),
):
    """Public endpoint — no login required, this is meant to be visible to everyone."""
    return {
        "leaderboard": _compute_mp_scores(db, house),
        "note": "Ranked by a composite of completion rate, grievance resolution, and average risk score. Lower risk and higher resolution/completion rate rank higher.",
    }