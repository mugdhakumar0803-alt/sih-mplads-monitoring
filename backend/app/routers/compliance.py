from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.work import Work
from ..ml.compliance_engine import ComplianceEngine

router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"]
)


@router.get("/check/{work_id}")
async def check_work_compliance(
    work_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check compliance status of a work."""
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    # Perform compliance check
    engine = ComplianceEngine()
    compliance_result = engine.check_compliance(work)
    
    return {
        "work_id": work.work_id,
        "compliance_status": compliance_result.get("status", "pending"),
        "score": compliance_result.get("score", 0),
        "violations": compliance_result.get("violations", []),
        "recommendations": compliance_result.get("recommendations", []),
    }


@router.get("/dashboard")
async def compliance_dashboard(
    state: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get compliance dashboard summary."""
    query = db.query(Work)
    if state:
        query = query.filter(Work.state == state)
    
    works = query.all()
    
    # Calculate statistics
    total_works = len(works)
    high_risk = sum(1 for w in works if w.risk_level == "high")
    medium_risk = sum(1 for w in works if w.risk_level == "medium")
    low_risk = sum(1 for w in works if w.risk_level == "low")
    
    avg_risk_score = sum(w.risk_score or 0 for w in works) / total_works if total_works > 0 else 0
    
    return {
        "total_works": total_works,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "average_risk_score": round(avg_risk_score, 2),
        "compliance_rate": round((low_risk + medium_risk) / total_works * 100, 2) if total_works > 0 else 0,
    }


@router.post("/batch-check")
async def batch_compliance_check(
    work_ids: list,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check compliance for multiple works."""
    engine = ComplianceEngine()
    results = []
    
    for work_id in work_ids:
        work = db.query(Work).filter(Work.work_id == work_id).first()
        if work:
            compliance_result = engine.check_compliance(work)
            results.append({
                "work_id": work.work_id,
                "status": compliance_result.get("status", "pending"),
                "score": compliance_result.get("score", 0),
            })
    
    return {"checked": len(results), "results": results}
