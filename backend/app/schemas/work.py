from datetime import datetime
from pydantic import BaseModel, ConfigDict
from ..models.work import WorkCategory, WorkStatus


class WorkCreate(BaseModel):
	work_id: str
	mp_name: str
	work_title: str
	category: WorkCategory
	state: str
	constituency: str
	allocation_amount: float
	recommended_date: datetime
	location: str | None = None


class WorkResponse(WorkCreate):
	model_config = ConfigDict(from_attributes=True)
	status: WorkStatus
	risk_score: float | None = None
	risk_level: str | None = None
	anomaly_drivers: list[str] | None = None
