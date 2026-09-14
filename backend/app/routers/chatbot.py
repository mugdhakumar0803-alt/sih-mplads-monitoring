from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.work import Work
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
    works = db.query(Work).all()
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
    """Search MPLADS works using RAG chatbot."""
    # TODO: Integrate with semantic search and RAG model
    
    from ..models.work import Work
    
    # Simple text search for now
    works = db.query(Work).filter(
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
