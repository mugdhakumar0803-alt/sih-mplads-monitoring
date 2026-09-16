# Reference Data API endpoints
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.constituency import Constituency
from ..models.reference_data import (
    SectorReference, StateFinanceHistorical,
    YearlyFinanceHistorical, StateWorksHistorical
)

router = APIRouter(prefix="/reference", tags=["Reference Data"])


@router.get("/constituencies")
def list_constituencies(
    state: str = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all constituencies, optionally filtered by state"""
    query = db.query(Constituency)
    
    if state:
        query = query.filter(Constituency.state == state)
    
    total = query.count()
    results = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "constituencies": [
            {
                "id": str(c.id),
                "name": c.name,
                "state": c.state,
                "reservation_status": c.reservation_status,
                "electors_2024": c.electors_2024
            }
            for c in results
        ]
    }


@router.get("/constituencies/{constituency_id}")
def get_constituency(constituency_id: str, db: Session = Depends(get_db)):
    """Get specific constituency details"""
    const = db.query(Constituency).filter(
        Constituency.constituency_id == constituency_id
    ).first()
    
    if not const:
        raise HTTPException(status_code=404, detail="Constituency not found")
    
    return {
        "id": str(const.id),
        "constituency_id": const.constituency_id,
        "name": const.name,
        "state": const.state,
        "reservation_status": const.reservation_status,
        "electors_2024": const.electors_2024,
        "created_at": const.created_at
    }


@router.get("/sectors")
def list_sectors(db: Session = Depends(get_db)):
    """List all work sectors from historical reference"""
    sectors = db.query(SectorReference).order_by(SectorReference.sector).all()
    
    return {
        "total": len(sectors),
        "sectors": [
            {
                "sector": s.sector,
                "total_sanctioned_cost_lakh": s.total_sanctioned_cost_lakh,
                "total_works_sanctioned": s.total_works_sanctioned
            }
            for s in sectors
        ]
    }


@router.get("/state-finance-historical")
def get_state_finance_historical(
    state: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get historical state finance data (FY2016-17 baseline)"""
    query = db.query(StateFinanceHistorical)
    
    if state:
        query = query.filter(StateFinanceHistorical.state == state)
    
    results = query.all()
    
    return {
        "fiscal_year": 2016,
        "total_records": len(results),
        "data": [
            {
                "state": r.state,
                "total_funds_released_cr": r.total_funds_released_cr,
                "expenditure_incurred_cr": r.expenditure_incurred_cr,
                "unspent_balance_cr": r.unspent_balance_cr,
                "pct_utilisation": r.pct_utilisation_over_release
            }
            for r in results
        ]
    }


@router.get("/yearly-finance-historical")
def get_yearly_finance_historical(db: Session = Depends(get_db)):
    """Get yearly finance trends (1993-94 to 2016-17)"""
    results = db.query(YearlyFinanceHistorical).order_by(
        YearlyFinanceHistorical.fiscal_year.asc()
    ).all()
    
    return {
        "total_years": len(results),
        "data": [
            {
                "fiscal_year": r.fiscal_year,
                "total_funds_released_cr": r.total_funds_released_cr,
                "total_expenditure_cr": r.total_expenditure_cr,
                "unspent_balance_cr": r.unspent_balance_cr
            }
            for r in results
        ]
    }


@router.get("/state-works-historical")
def get_state_works_historical(
    state: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get historical state-wise work counts and costs (2019 baseline)"""
    query = db.query(StateWorksHistorical)
    
    if state:
        query = query.filter(StateWorksHistorical.state == state)
    
    results = query.all()
    
    return {
        "historical_year": 2019,
        "total_records": len(results),
        "data": [
            {
                "state": r.state,
                "work_count": r.work_count,
                "total_sanctioned_cost_lakh": r.total_sanctioned_cost_lakh,
                "avg_project_cost_lakh": r.avg_project_cost_lakh
            }
            for r in results
        ]
    }


@router.get("/states-list")
def get_states_list(db: Session = Depends(get_db)):
    """Get unique list of all states"""
    states = db.query(Constituency.state).distinct().order_by(Constituency.state).all()
    return {
        "total": len(states),
        "states": [s[0] for s in states if s[0]]
    }
