from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..schemas.rating import RatingCreate
from ..services.rating_service import RatingService


router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"],
)


@router.post("/")
async def create_rating(
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rating, error = RatingService.create_rating(
        db,
        current_user.id,
        data,
    )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error,
        )

    return {
        "message": "Rating submitted successfully",
        "overall_score": rating.overall_score,
    }


@router.get("/leaderboard")
async def leaderboard(
    level: str = "national",
    state: str | None = None,
    constituency: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if level not in {"national", "state", "constituency"}:
        raise HTTPException(
            status_code=400,
            detail="level must be national, state, or constituency",
        )

    if level == "state" and not state:
        raise HTTPException(
            status_code=400,
            detail="state is required for state leaderboard",
        )

    if level == "constituency" and not constituency:
        raise HTTPException(
            status_code=400,
            detail="constituency is required for constituency leaderboard",
        )

    rankings = RatingService.get_mp_rankings(
        db,
        state=state if level in {"state", "constituency"} else None,
        constituency=constituency if level == "constituency" else None,
    )

    return {
        "level": level,
        "rankings": rankings,
    }