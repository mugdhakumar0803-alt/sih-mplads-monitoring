from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .security import decode_token
from ..database import get_db
from ..models.user import User, UserRole
from ..models.audit import AuditLog
import uuid
import json


security = HTTPBearer(auto_error=False)


def write_audit(
    db: Session,
    user: User | None,
    action: str,
    request: Request | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    status_value: str = "SUCCESS",
    details: dict | None = None,
):
    client = request.client if request else None
    db.add(
        AuditLog(
            id=str(uuid.uuid4()),
            user_id=str(user.id) if user else None,
            username=user.username if user else None,
            role=user.role.value if user else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=client.host if client else None,
            user_agent=request.headers.get("user-agent") if request else None,
            status=status_value,
            details=json.dumps(details or {}, default=str),
        )
    )
    db.commit()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = decode_token(credentials.credentials)

    if token_data is None:
        write_audit(
            db, None, "AUTH_TOKEN_INVALID", request,
            status_value="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None or not user.is_active:
        write_audit(
            db, user, "AUTH_USER_INVALID", request,
            status_value="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


def require_role(*roles: UserRole):
    async def role_checker(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if current_user.role not in roles:
            write_audit(
                db,
                current_user,
                "AUTHORIZATION_DENIED",
                request,
                status_value="FAILURE",
                details={"required_roles": [r.value for r in roles]},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker
