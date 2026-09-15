from __future__ import annotations

from datetime import datetime
import json
import uuid
import hashlib

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from .security import decode_token
from ..database import get_db
from ..models.user import (
    User,
    UserRole,
)
from ..models.audit import AuditLog
from ..models.revoked_token import RevokedToken


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

    last_log = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .first()
    )

    previous_hash = (
        last_log.entry_hash
        if last_log
        else "GENESIS"
    )

    timestamp = datetime.utcnow()

    payload = json.dumps(
        {
            "previous_hash": previous_hash,
            "user_id":
                str(user.id) if user else None,
            "username":
                user.username if user else None,
            "role":
                user.role.value if user else None,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status": status_value,
            "details": details or {},
            "timestamp":
                timestamp.isoformat(),
        },
        sort_keys=True,
        default=str,
    )

    entry_hash = hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()

    db.add(
        AuditLog(
            id=str(uuid.uuid4()),
            user_id=str(user.id) if user else None,
            username=user.username if user else None,
            role=user.role.value if user else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=(
                client.host
                if client
                else None
            ),
            user_agent=(
                request.headers.get(
                    "user-agent"
                )
                if request
                else None
            ),
            status=status_value,
            details=json.dumps(
                details or {},
                default=str,
            ),
            timestamp=timestamp,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
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
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    token_data = decode_token(
        credentials.credentials
    )

    if token_data is None:
        write_audit(
            db,
            None,
            "AUTH_TOKEN_INVALID",
            request,
            status_value="FAILURE",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    revoked = (
        db.query(RevokedToken)
        .filter(
            RevokedToken.jti == token_data.jti
        )
        .first()
    )

    if revoked:
        write_audit(
            db,
            None,
            "AUTH_TOKEN_REVOKED",
            request,
            status_value="FAILURE",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    user = (
        db.query(User)
        .filter(User.id == token_data.user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        write_audit(
            db,
            user,
            "AUTH_USER_INACTIVE",
            request,
            status_value="FAILURE",
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if not user.is_approved():
        write_audit(
            db,
            user,
            "AUTH_APPROVAL_REQUIRED",
            request,
            status_value="FAILURE",
            details={
                "approval_status":
                    user.approval_status.value
            },
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has not been approved",
        )

    return user


def require_role(*roles: UserRole):

    async def role_checker(
        request: Request,
        current_user: User = Depends(
            get_current_user
        ),
        db: Session = Depends(get_db),
    ) -> User:

        if current_user.role not in roles:

            write_audit(
                db,
                current_user,
                "AUTHORIZATION_DENIED",
                request,
                status_value="FAILURE",
                details={
                    "required_roles": [
                        role.value
                        for role in roles
                    ],
                    "actual_role":
                        current_user.role.value,
                },
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker