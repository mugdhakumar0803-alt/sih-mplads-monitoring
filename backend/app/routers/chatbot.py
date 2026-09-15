from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import re

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.work import Work
from ..models.grievance import Grievance

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"]
)


class ChatMessage(BaseModel):
    """Chat message from any logged-in user."""
    message: str


class ChatResponse(BaseModel):
    """Chatbot response."""
    response: str
    sources: list = []
    confidence: float = 0.8


def _scope_works(db: Session, user: User):
    """
    Role-aware scoping — an MP asking a question should be answered about
    THEIR OWN constituency's works by default, a district official about
    their district, a state official about their state. Ministry/admin see
    everything. Citizens see everything too (this platform is public/
    transparency-focused for citizens).
    """
    query = db.query(Work)
    if user.role == "mp" and user.constituency:
        query = query.filter(Work.constituency == user.constituency)
    elif user.role in ("district_official", "state_official") and user.state:
        query = query.filter(Work.state == user.state)
    return query


@router.post("/ask", response_model=ChatResponse)
async def chat_with_bot(
    query: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask the assistant — available to every role, scoped to what that
    role should see."""
    message_lower = query.message.lower()
    terms = {term for term in re.findall(r"[a-z0-9-]+", message_lower) if len(term) > 2}

    works_query = _scope_works(db, current_user)

    # "How many grievances / risky works / how am I doing" style summary
    # questions — answer with real numbers instead of only work lookup.
    summary_keywords = {"how many", "summary", "overview", "status", "performance", "how am i doing", "grievance"}
    if any(kw in message_lower for kw in summary_keywords):
        works = works_query.all()
        work_ids = [w.work_id for w in works]
        total = len(works)
        completed = sum(1 for w in works if getattr(w.status, "value", w.status) == "Completed")
        high_risk = sum(1 for w in works if w.risk_level == "high")
        open_grievances = (
            db.query(Grievance)
            .filter(Grievance.work_id.in_(work_ids), Grievance.status != "resolved")
            .count()
            if work_ids else 0
        )
        scope_label = current_user.constituency or current_user.state or "the system"
        response = (
            f"In {scope_label}: {total} works on record, {completed} completed, "
            f"{high_risk} flagged high-risk, {open_grievances} grievances still open."
        )
        return ChatResponse(response=response, sources=[f"{total} live work records"], confidence=0.9)

    works = works_query.all()
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
        response = "No matching verified project record was found in your scope. Try a work ID, project title, or ask for a summary/overview."
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
    """Search verified work records for grounded assistant retrieval, scoped
    to the current user's role."""
    works = (
        _scope_works(db, current_user)
        .filter(
            (Work.work_title.ilike(f"%{query}%"))
            | (Work.state.ilike(f"%{query}%"))
            | (Work.work_id.ilike(f"%{query}%"))
        )
        .limit(10)
        .all()
    )

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
