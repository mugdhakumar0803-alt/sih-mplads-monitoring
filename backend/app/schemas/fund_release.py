from datetime import datetime
from pydantic import BaseModel
from ..models.fund_release import ReleaseStatus


class FundReleaseCreate(BaseModel):
	release_id: str
	work_id: str
	sanction_amount: float
	released_amount: float = 0.0
	release_number: int = 1
	requested_date: datetime


class FundReleaseResponse(FundReleaseCreate):
	status: ReleaseStatus
	eligibility_status: str | None = None
	eligibility_checks: dict | None = None
	compliance_score: float | None = None
