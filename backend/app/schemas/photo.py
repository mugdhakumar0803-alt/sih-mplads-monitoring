from datetime import datetime
from pydantic import BaseModel


class PhotoResponse(BaseModel):
	photo_id: str
	work_id: str
	status: str
	verification_score: float | None = None


class PhotoMetadata(BaseModel):
	work_id: str
	capture_date: datetime | None = None
