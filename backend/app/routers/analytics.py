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


# State-level aggregations
@router.get("/state-stats")
def state_statistics(db: Session = Depends(get_db)):
    """Get statistics aggregated by state"""
    states = db.query(Work.state).distinct().filter(Work.state != None).all()
    results = []
    
    for (state_name,) in states:
        works = db.query(Work).filter(Work.state == state_name).all()
        if not works:
            continue
            
        results.append({
            "state": state_name,
            "total_projects": len(works),
            "sanctioned": sum(1 for w in works if w.status == WorkStatus.SANCTIONED),
            "in_progress": sum(1 for w in works if w.status == WorkStatus.ONGOING),
            "completed": sum(1 for w in works if w.status == WorkStatus.COMPLETED),
            "total_allocation": sum(w.allocation_amount or 0 for w in works),
            "total_expenditure": sum(w.expenditure_amount or 0 for w in works if w.expenditure_amount),
            "utilization_percentage": round(
                sum(w.expenditure_amount or 0 for w in works if w.expenditure_amount) / 
                sum(w.allocation_amount or 0 for w in works) * 100, 2
            ) if sum(w.allocation_amount or 0 for w in works) > 0 else 0,
            "high_risk_count": sum(1 for w in works if w.risk_level == "high"),
            "open_grievances": sum(1 for w in works for g in db.query(Grievance).filter(Grievance.work_id == w.work_id) if g.status != GrievanceStatus.RESOLVED)
        })
    
    return {"total_states": len(results), "states": sorted(results, key=lambda x: x["state"])}


@router.get("/state-stats/{state}")
def state_statistics_detailed(state: str, db: Session = Depends(get_db)):
    """Get detailed statistics for a specific state"""
    works = db.query(Work).filter(Work.state == state).all()
    
    if not works:
        raise HTTPException(status_code=404, detail="No projects found in this state")
    
    # Group by district
    districts = {}
    for work in works:
        dist = work.district or "Unknown"
        if dist not in districts:
            districts[dist] = []
        districts[dist].append(work)
    
    district_stats = []
    for dist, dist_works in districts.items():
        district_stats.append({
            "district": dist,
            "total_projects": len(dist_works),
            "sanctioned": sum(1 for w in dist_works if w.status == WorkStatus.SANCTIONED),
            "completed": sum(1 for w in dist_works if w.status == WorkStatus.COMPLETED),
            "total_allocation": sum(w.allocation_amount or 0 for w in dist_works),
            "total_expenditure": sum(w.expenditure_amount or 0 for w in dist_works if w.expenditure_amount)
        })
    
    return {
        "state": state,
        "total_projects": len(works),
        "sanctioned": sum(1 for w in works if w.status == WorkStatus.SANCTIONED),
        "in_progress": sum(1 for w in works if w.status == WorkStatus.ONGOING),
        "completed": sum(1 for w in works if w.status == WorkStatus.COMPLETED),
        "total_allocation": sum(w.allocation_amount or 0 for w in works),
        "total_expenditure": sum(w.expenditure_amount or 0 for w in works if w.expenditure_amount),
        "utilization_percentage": round(
            sum(w.expenditure_amount or 0 for w in works if w.expenditure_amount) / 
            sum(w.allocation_amount or 0 for w in works) * 100, 2
        ) if sum(w.allocation_amount or 0 for w in works) > 0 else 0,
        "risk_breakdown": {
            "high": sum(1 for w in works if w.risk_level == "high"),
            "medium": sum(1 for w in works if w.risk_level == "medium"),
            "low": sum(1 for w in works if w.risk_level == "low")
        },
        "districts": sorted(district_stats, key=lambda x: x["district"])
    }


@router.get("/district-stats/{state}/{district}")
def district_statistics(state: str, district: str, db: Session = Depends(get_db)):
    """Get detailed statistics for a specific district"""
    works = db.query(Work).filter(
        Work.state == state,
        Work.district == district
    ).all()
    
    if not works:
        raise HTTPException(status_code=404, detail="No projects found in this district")
    
    return {
        "state": state,
        "district": district,
        "total_projects": len(works),
        "sanctioned": sum(1 for w in works if w.status == WorkStatus.SANCTIONED),
        "in_progress": sum(1 for w in works if w.status == WorkStatus.ONGOING),
        "completed": sum(1 for w in works if w.status == WorkStatus.COMPLETED),
        "total_allocation": sum(w.allocation_amount or 0 for w in works),
        "total_expenditure": sum(w.expenditure_amount or 0 for w in works if w.expenditure_amount),
        "utilization_percentage": round(
            sum(w.expenditure_amount or 0 for w in works if w.expenditure_amount) / 
            sum(w.allocation_amount or 0 for w in works) * 100, 2
        ) if sum(w.allocation_amount or 0 for w in works) > 0 else 0,
        "categories": Counter(w.category.value if hasattr(w.category, 'value') else w.category for w in works).most_common(5)
    }


@router.get("/mp-stats/{constituency}")
def mp_statistics(constituency: str, db: Session = Depends(get_db)):
    """Get detailed statistics for an MP's constituency"""
    works = db.query(Work).filter(Work.constituency == constituency).all()
    
    if not works:
        raise HTTPException(status_code=404, detail="No projects found in this constituency")
    
    return {
        "constituency": constituency,
        "total_projects": len(works),
        "sanctioned": sum(1 for w in works if w.status == WorkStatus.SANCTIONED),
        "in_progress": sum(1 for w in works if w.status == WorkStatus.ONGOING),
        "completed": sum(1 for w in works if w.status == WorkStatus.COMPLETED),
        "total_allocation": sum(w.allocation_amount or 0 for w in works),
        "total_expenditure": sum(w.expenditure_amount or 0 for w in works if w.expenditure_amount),
        "utilization_percentage": round(
            sum(w.expenditure_amount or 0 for w in works if w.expenditure_amount) / 
            sum(w.allocation_amount or 0 for w in works) * 100, 2
        ) if sum(w.allocation_amount or 0 for w in works) > 0 else 0,
        "avg_completion_time_days": round(
            sum((w.completion_date - w.recommended_date).days for w in works 
                if w.completion_date and w.recommended_date) / len([w for w in works if w.completion_date and w.recommended_date])
        ) if any(w.completion_date and w.recommended_date for w in works) else None,
        "citizen_grievances": sum(w.citizen_grievance_count or 0 for w in works)
    }


@router.get("/category-stats")
def category_statistics(db: Session = Depends(get_db)):
    """Get statistics by work category"""
    categories = db.query(Work.category).distinct().filter(Work.category != None).all()
    results = []
    
    for (category,) in categories:
        works = db.query(Work).filter(Work.category == category).all()
        if not works:
            continue
            
        results.append({
            "category": category.value if hasattr(category, 'value') else category,
            "total_projects": len(works),
            "completed": sum(1 for w in works if w.status == WorkStatus.COMPLETED),
            "total_allocation": sum(w.allocation_amount or 0 for w in works),
            "total_expenditure": sum(w.expenditure_amount or 0 for w in works if w.expenditure_amount)
        })
    
    return {"total_categories": len(results), "categories": sorted(results, key=lambda x: x["total_projects"], reverse=True)}
