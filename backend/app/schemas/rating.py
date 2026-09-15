from __future__ import annotations

from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    work_id: str

    quality_score: float = Field(ge=1, le=5)
    usefulness_score: float = Field(ge=1, le=5)
    timeliness_score: float = Field(ge=1, le=5)
    maintenance_score: float = Field(ge=1, le=5)
    satisfaction_score: float = Field(ge=1, le=5)

    comment: str | None = None