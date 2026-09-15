import re

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..database import get_db
from ..models.fund_release import FundReleaseRecord
from ..models.grievance import Grievance, GrievanceStatus
from ..models.user import User, UserRole
from ..models.work import Work

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    sources: list = []
    confidence: float = 0.8


def _scope_works(db: Session, user: User):
    query = db.query(Work)
    if user.role == UserRole.MP:
        return query.filter(Work.constituency == user.constituency) if user.constituency else query.filter(Work.mp_name == user.username)
    if user.role == UserRole.STATE_OFFICIAL and user.state:
        return query.filter(Work.state == user.state)
    if user.role == UserRole.DISTRICT_OFFICIAL and user.district_id:
        return query.filter(Work.district == user.district_id)
    if user.role == UserRole.CITIZEN and user.state:
        return query.filter(Work.state == user.state)
    return query


@router.post("/ask", response_model=ChatResponse)
async def chat_with_bot(query: ChatMessage, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    message = query.message.lower()
    terms = {term for term in re.findall(r"[a-z0-9-]+", message) if len(term) > 2}
    works_query = _scope_works(db, current_user)

    if {"grievance", "grievances", "complaint", "complaints"} & terms:
        work_ids = [work.work_id for work in works_query.all()]
        count = db.query(Grievance).filter(Grievance.work_id.in_(work_ids), Grievance.status.notin_([GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED])).count() if work_ids else 0
        return ChatResponse(response=f"There are {count} unresolved grievances in your permitted view.", sources=["Verified grievance records"], confidence=0.9)

    if {"fund", "funds", "release", "releases"} & terms:
        count = db.query(FundReleaseRecord).count()
        return ChatResponse(response=f"There are {count} fund release records in the system.", sources=["Verified fund release records"], confidence=0.9)

    if any(keyword in message for keyword in ("how many", "summary", "overview", "performance")):
        works = works_query.all()
        completed = sum(1 for work in works if getattr(work.status, "value", work.status) == "Completed")
        high_risk = sum(1 for work in works if work.risk_level == "high")
        scope_label = current_user.constituency or current_user.state or "the system"
        return ChatResponse(response=f"In {scope_label}: {len(works)} works on record, {completed} completed, and {high_risk} high-risk works.", sources=[f"{len(works)} live work records"], confidence=0.9)

    works = works_query.all()
    ranked = sorted(works, key=lambda work: len(terms & set(re.findall(r"[a-z0-9-]+", f"{work.work_id} {work.work_title} {work.state}".lower()))), reverse=True)
    match = ranked[0] if ranked and terms & set(re.findall(r"[a-z0-9-]+", f"{ranked[0].work_id} {ranked[0].work_title} {ranked[0].state}".lower())) else None
    if not match:
        return ChatResponse(response="No matching verified project record was found in your scope.", sources=[], confidence=0.0)
    return ChatResponse(response=f"{match.work_title} ({match.work_id}) is {getattr(match.status, 'value', match.status)} in {match.state}. Allocation: ₹{match.allocation_amount:,.0f}. Risk: {match.risk_level or 'not assessed'}.", sources=[f"Verified work record {match.work_id}"], confidence=0.95)


@router.post("/search")
async def search_works(query: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pattern = f"%{query}%"
    works = _scope_works(db, current_user).filter((Work.work_title.ilike(pattern)) | (Work.state.ilike(pattern)) | (Work.work_id.ilike(pattern))).limit(10).all()
    return {"query": query, "results_count": len(works), "results": [{"work_id": work.work_id, "title": work.work_title, "state": work.state, "status": getattr(work.status, "value", work.status)} for work in works]}
