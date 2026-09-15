from pydantic import BaseModel, ConfigDict
from ..models.grievance import GrievanceSeverity, GrievanceStatus


class GrievanceCreate(BaseModel):
	work_id: str | None = None
	citizen_name: str
	citizen_contact: str | None = None
	citizen_email: str | None = None
	description: str
	severity: GrievanceSeverity = GrievanceSeverity.MEDIUM


class GrievanceResponse(GrievanceCreate):
	model_config = ConfigDict(from_attributes=True)
	grievance_id: str
	status: GrievanceStatus
	is_escalated: bool
