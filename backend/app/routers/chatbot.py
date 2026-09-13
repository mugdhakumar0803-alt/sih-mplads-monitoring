from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User

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
    # TODO: Integrate with RAG system for real responses
    # This is a placeholder that returns template responses
    
    message = query.message.lower()
    
    # Simple rule-based responses for common queries
    if "grievance" in message or "complain" in message:
        response = (
            "You can file a grievance by providing details about the work and your concern. "
            "Please include work ID, description, and contact information. "
            "Our team will review and respond within 7 days."
        )
    elif "fund" in message or "release" in message or "money" in message:
        response = (
            "Fund releases follow the compliance and eligibility criteria. "
            "Check the compliance dashboard to see your work's status. "
            "Funds are typically released monthly for eligible works."
        )
    elif "photo" in message or "verification" in message:
        response = (
            "Progress photos help us verify work completion. "
            "Please upload recent photos showing current work status. "
            "Photos should have date stamp and GPS metadata if possible."
        )
    elif "status" in message or "progress" in message:
        response = (
            "You can check work status by entering your work ID in the dashboard. "
            "Status includes allocation, released funds, and completion percentage."
        )
    else:
        response = (
            "I'm here to help with questions about MPLADS works, fund releases, grievances, and progress tracking. "
            "Please ask about any of these topics or visit the dashboard for more details."
        )
    
    return ChatResponse(
        response=response,
        sources=["FAQ Database", "Policy Guidelines"],
        confidence=0.85,
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
