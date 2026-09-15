"""
Owner: Full-stack/Backend.
Location: backend/app/routers/leaderboard.py

Public accountability leaderboard, split by house since Lok Sabha and
Rajya Sabha MPs have different mandates and shouldn't be ranked against
each other in one mixed list.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..database import get_db
from ..models.grievance import Grievance, GrievanceStatus
from ..models.rating import Rating
from ..models.user import User
from ..models.work import Work, WorkStatus

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

WEIGHTS = {
    "completion": 0.25,
    "timeliness": 0.20,
    "utilization": 0.20,
    "grievance_resolution": 0.15,
    "compliance": 0.10,
    "risk_resolution": 0.10,
}


def _score(components: dict) -> Optional[float]:
    available = {name: value for name, value in components.items() if value is not None}
    if not available:
        return None
    total_weight = sum(WEIGHTS[name] for name in available)
    return round(sum(available[name] * WEIGHTS[name] for name in available) / total_weight, 1)


def _work_metrics(db: Session, works: list[Work]) -> dict:
    total = len(works)
    completed = sum(work.status == WorkStatus.COMPLETED for work in works)
    work_ids = [work.work_id for work in works]
    grievances = db.query(Grievance).filter(Grievance.work_id.in_(work_ids)).all() if work_ids else []
    resolved = sum(grievance.status in {GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED} for grievance in grievances)
    high_risk = sum(work.risk_level == "high" for work in works)
    assessed = sum(work.risk_level is not None for work in works)
    with_expenditure = [work for work in works if work.expenditure_amount is not None and work.allocation_amount]
    utilization = (
        sum(work.expenditure_amount for work in with_expenditure)
        / sum(work.allocation_amount for work in with_expenditure)
        * 100
    ) if with_expenditure else None
    components = {
        "completion": completed / total * 100 if total else None,
        "timeliness": None,
        "utilization": utilization,
        "grievance_resolution": resolved / len(grievances) * 100 if grievances else None,
        "compliance": None,
        "risk_resolution": (1 - high_risk / assessed) * 100 if assessed else None,
    }
    return {
        "projects": total,
        "completed_projects": completed,
        "completion_rate": round(components["completion"], 1) if components["completion"] is not None else None,
        "delayed_projects": None,
        "high_risk_projects": high_risk,
        "open_grievances": len(grievances) - resolved,
        "grievance_resolution_rate": round(components["grievance_resolution"], 1) if components["grievance_resolution"] is not None else None,
        "utilization": round(utilization, 1) if utilization is not None else None,
        "score": _score(components),
        "score_components": components,
    }


@router.get("")
async def mp_performance(
    house: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    groups = defaultdict(list)
    for work in db.query(Work).all():
        if state and work.state != state:
            continue
        groups[(work.mp_name, work.state, work.constituency)].append(work)
    rows = []
    for (mp_name, work_state, constituency), works in groups.items():
        metrics = _work_metrics(db, works)
        ratings = db.query(Rating).join(Work, Rating.work_id == Work.id).filter(Work.mp_name == mp_name).all()
        metrics["citizen_rating"] = round(sum(rating.overall_score for rating in ratings) / len(ratings), 2) if ratings else None
        metrics["citizen_rating_count"] = len(ratings)
        rows.append({"mp_name": mp_name, "house": house or "Data unavailable", "state": work_state, "constituency": constituency, **metrics})
    rows.sort(key=lambda row: row["score"] if row["score"] is not None else -1, reverse=True)
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return {"type": "mp", "weights": {name: value * 100 for name, value in WEIGHTS.items()}, "leaderboard": rows}


@router.get("/states")
async def state_performance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    groups = defaultdict(list)
    for work in db.query(Work).all():
        groups[work.state].append(work)
    rows = [{"state": state, **_work_metrics(db, works)} for state, works in groups.items()]
    rows.sort(key=lambda row: row["score"] if row["score"] is not None else -1, reverse=True)
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return {"type": "state", "leaderboard": rows}


@router.get("/districts")
async def district_performance(
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    groups = defaultdict(list)
    for work in db.query(Work).all():
        if state and work.state != state:
            continue
        groups[(work.district or "Data unavailable", work.state)].append(work)
    rows = [{"district": district, "state": district_state, **_work_metrics(db, works)} for (district, district_state), works in groups.items()]
    rows.sort(key=lambda row: row["score"] if row["score"] is not None else -1, reverse=True)
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return {"type": "district", "leaderboard": rows}
