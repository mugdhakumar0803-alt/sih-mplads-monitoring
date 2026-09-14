from pydantic import BaseModel, ConfigDict, EmailStr
from ..models.user import UserRole


class UserCreate(BaseModel):
	username: str
	email: EmailStr
	password: str
	role: UserRole = UserRole.CITIZEN


class UserResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: str
	username: str
	email: EmailStr
	role: UserRole
	is_active: bool
