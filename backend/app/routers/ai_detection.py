from fastapi import APIRouter
from pydantic import BaseModel, Field
from ..ml.duplicates import DuplicatePair, find_duplicate_clusters

router = APIRouter(
    prefix="/ai",
    tags=["AI Detection"]
)


class WorkInput(BaseModel):
    work_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    category: str = Field(min_length=1)


class DuplicateDetectionRequest(BaseModel):
    works: list[WorkInput]


@router.post("/duplicates", response_model=list[DuplicatePair])
def detect_duplicate_works(request: DuplicateDetectionRequest) -> list[DuplicatePair]:
    """Return likely duplicate works from the submitted work records."""
    return find_duplicate_clusters(request.works)
