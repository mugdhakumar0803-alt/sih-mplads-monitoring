from statistics import median
from difflib import SequenceMatcher
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.work import Work, WorkStatus
from ..models.grievance import Grievance, GrievanceStatus
from ..ml.compliance_engine import ComplianceEngine
from ..ml.duplicates import DuplicatePair, find_duplicate_clusters

router = APIRouter(
    prefix="/ai",
    tags=["AI Detection"]
)


class WorkInput(BaseModel):
    work_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    category: str = Field(min_length=1)


class DuplicateDetectionRequest(BaseModel):
    works: list[WorkInput]


@router.post("/duplicates", response_model=list[DuplicatePair])
def detect_duplicate_works(request: DuplicateDetectionRequest) -> list[DuplicatePair]:
    """Return likely duplicate works from the submitted work records."""
    return find_duplicate_clusters(request.works)


def _risk_for_work(work: Work, db: Session) -> dict:
    peers = db.query(Work).filter(
        Work.state == work.state,
        Work.category == work.category,
        Work.id != work.id,
    ).all()
    peer_amounts = [peer.allocation_amount for peer in peers if peer.allocation_amount]
    peer_median = median(peer_amounts) if peer_amounts else None
    cost_ratio = (work.allocation_amount / peer_median) if peer_median else None
    cost_risk = min(1.0, max(0.0, (cost_ratio - 1) / 2)) if cost_ratio else 0.0
    age_days = max(0, (datetime.utcnow() - work.recommended_date).days) if work.recommended_date else 0
    delay_risk = min(1.0, max(0.0, (age_days - 365) / 365)) if work.status != WorkStatus.COMPLETED else 0.0
    open_grievances = db.query(Grievance).filter(
        Grievance.work_id == work.work_id,
        Grievance.status.notin_([GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED]),
    ).count()
    grievance_risk = min(1.0, open_grievances / 3)
    compliance = ComplianceEngine().check_compliance(work)
    compliance_risk = 1.0 if compliance["status"] != "compliant" else 0.0
    similar = []
    normalized_title = work.work_title.casefold()
    for peer in peers:
        similarity = SequenceMatcher(None, normalized_title, peer.work_title.casefold()).ratio()
        if similarity >= 0.8:
            similar.append({"work_id": peer.work_id, "similarity": round(similarity, 3)})
    duplicate_risk = min(1.0, max((item["similarity"] for item in similar), default=0.0))
    score = round(cost_risk * 0.3 + delay_risk * 0.2 + duplicate_risk * 0.2 + grievance_risk * 0.1 + compliance_risk * 0.2, 3)
    level = "high" if score >= 0.75 else "medium" if score >= 0.45 else "low"
    signals = []
    if cost_ratio and cost_ratio > 1.5:
        signals.append({"type": "cost", "value": round(cost_ratio, 2), "reason": f"Allocation is {cost_ratio:.1f}x the peer median."})
    if delay_risk:
        signals.append({"type": "delay", "value": round(delay_risk, 2), "reason": f"Work has been open for {age_days} days without a completed status."})
    if similar:
        signals.append({"type": "duplicate_candidate", "value": duplicate_risk, "reason": "A similar work description exists in the same state and category."})
    if open_grievances:
        signals.append({"type": "grievance", "value": grievance_risk, "reason": f"{open_grievances} unresolved grievance(s) are linked to this work."})
    if compliance_risk:
        signals.append({"type": "compliance", "value": compliance_risk, "reason": "; ".join(compliance["violations"])})
    return {"work_id": work.work_id, "risk_score": score, "risk_level": level, "signals": signals, "model_version": "peer-rules-v1", "limitations": ["Risk indicates a potential irregularity and is not a fraud finding."], "peer_median_allocation": peer_median, "duplicate_candidates": similar}


@router.get("/risk/{work_id}")
def work_risk(work_id: str, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    return _risk_for_work(work, db)


@router.get("/cost-anomalies")
def cost_anomalies(state: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Work)
    if state:
        query = query.filter(Work.state == state)
    if category:
        query = query.filter(Work.category == category)
    results = []
    for work in query.all():
        risk = _risk_for_work(work, db)
        cost_signal = next((signal for signal in risk["signals"] if signal["type"] == "cost"), None)
        if cost_signal:
            results.append({"work_id": work.work_id, "state": work.state, "category": getattr(work.category, "value", work.category), "allocation_amount": work.allocation_amount, "peer_median_allocation": risk["peer_median_allocation"], "deviation_ratio": cost_signal["value"], "risk_level": risk["risk_level"], "reason": cost_signal["reason"]})
    return results