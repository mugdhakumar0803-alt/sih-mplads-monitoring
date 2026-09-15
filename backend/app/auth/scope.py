from fastapi import HTTPException, status
from ..models.user import User, UserRole
from ..models.work import Work


def work_is_in_scope(work: Work, user: User) -> bool:
    if user.role in (UserRole.ADMIN, UserRole.MINISTRY):
        return True
    if user.role == UserRole.CITIZEN:
        return True  # all currently exposed work data is public
    if user.role == UserRole.MP:
        return (
            bool(user.constituency_id)
            and work.constituency_id == user.constituency_id
        )
    if user.role == UserRole.DISTRICT_OFFICIAL:
        return bool(user.district_id) and work.district_id == user.district_id
    if user.role == UserRole.STATE_OFFICIAL:
        return bool(user.state_id) and work.state_id == user.state_id
    return False


def require_work_scope(work: Work, user: User) -> None:
    if not work_is_in_scope(work, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this work",
        )