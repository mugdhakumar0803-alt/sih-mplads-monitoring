from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.work import Work
from ..models.grievance import Grievance, GrievanceStatus
from ..models.fund_release import FundReleaseRecord
from ..models.user import UserRole
import re

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"]
)


class ChatMessage(BaseModel):
    """Chat message from citizen."""
    message: str


class ChatResponse(BaseModel):
    """Chatbot response."""
    response: str
    sources: list = []
    confidence: float = 0.8


@router.post("/ask", response_model=ChatResponse)
async def chat_with_bot(
    query: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask the citizen assistance chatbot."""
    terms = {term for term in re.findall(r"[a-z0-9-]+", query.message.lower()) if len(term) > 2}
    work_query = db.query(Work)
    if current_user.role == UserRole.MP and current_user.constituency:
        work_query = work_query.filter(Work.constituency == current_user.constituency)
    elif current_user.role == UserRole.STATE_OFFICIAL and current_user.state:
        work_query = work_query.filter(Work.state == current_user.state)
    if {"grievance", "grievances", "complaint", "complaints"} & terms:
        count = db.query(Grievance).filter(Grievance.status != GrievanceStatus.RESOLVED).count()
        return ChatResponse(response=f"There are {count} unresolved grievances in your permitted view.", sources=["Verified grievance records"], confidence=0.9)
    if {"fund", "funds", "release", "releases"} & terms:
        count = db.query(FundReleaseRecord).count()
        return ChatResponse(response=f"There are {count} fund release records in the system.", sources=["Verified fund release records"], confidence=0.9)
    works = work_query.all()
    ranked = sorted(
        works,
        key=lambda work: len(terms & set(re.findall(r"[a-z0-9-]+", f"{work.work_id} {work.work_title} {work.state}".lower()))),
        reverse=True,
    )
    match = ranked[0] if ranked and terms & set(re.findall(r"[a-z0-9-]+", f"{ranked[0].work_id} {ranked[0].work_title} {ranked[0].state}".lower())) else None
    if match:
        response = f"{match.work_title} ({match.work_id}) is {getattr(match.status, 'value', match.status)} in {match.state}. Allocation: ₹{match.allocation_amount:,.0f}. Risk: {match.risk_level or 'not assessed'} ({match.risk_score or 0:.2f})."
        sources = [f"Verified work record {match.work_id}"]
        confidence = 0.95
    else:
        response = "No matching verified project record was found. Try a work ID, project title, or state."
        sources = []
        confidence = 0.0
    return ChatResponse(
        response=response,
        sources=sources,
        confidence=confidence,
    )


@router.post("/search")
async def search_works(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search verified work records for grounded assistant retrieval."""
    
    from ..models.work import Work
    
    # Simple text search for now
    work_query = db.query(Work)
    if current_user.role == UserRole.MP and current_user.constituency:
        work_query = work_query.filter(Work.constituency == current_user.constituency)
    elif current_user.role == UserRole.STATE_OFFICIAL and current_user.state:
        work_query = work_query.filter(Work.state == current_user.state)
    works = work_query.filter(
        (Work.work_title.ilike(f"%{query}%")) |
        (Work.state.ilike(f"%{query}%")) |
        (Work.work_id.ilike(f"%{query}%"))
    ).limit(10).all()
    
    return {
        "query": query,
        "results_count": len(works),
        "results": [
            {
                "work_id": w.work_id,
                "title": w.work_title,
                "state": w.state,
                "status": w.status,
            }
            for w in works
        ]
    }
