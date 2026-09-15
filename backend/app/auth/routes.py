from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .schemas import UserLogin, UserRegister, Token
from .security import verify_password, get_password_hash, create_access_token
from .dependencies import get_current_user, write_audit
from ..database import get_db
from ..models.user import User, UserRole
from ..config import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        role = UserRole(user_data.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Do not allow public self-registration as privileged roles.
    if role in {
        UserRole.ADMIN,
        UserRole.MP,
        UserRole.DISTRICT,
        UserRole.STATE,
        UserRole.MINISTRY,
    }:
        raise HTTPException(
            status_code=403,
            detail="Privileged accounts must be provisioned by an administrator",
        )

    existing_user = db.query(User).filter(
        (User.username == user_data.username)
        | (User.email == str(user_data.email))
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered",
        )

    new_user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=get_password_hash(user_data.password),
        role=role,
        constituency_id=user_data.constituency_id,
        district_id=user_data.district_id,
        state_id=user_data.state_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    write_audit(db, new_user, "REGISTER_SUCCESS", request)

    return {
        "id": str(new_user.id),
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role.value,
    }


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(
        credentials.password, user.hashed_password
    ):
        write_audit(
            db, user, "LOGIN_FAILURE", request,
            status_value="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        write_audit(
            db, user, "LOGIN_INACTIVE", request,
            status_value="FAILURE",
        )
        raise HTTPException(
            status_code=403,
            detail="User is inactive",
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "user_id": str(user.id),
            "role": user.role.value,
            "constituency_id": user.constituency_id,
            "district_id": user.district_id,
            "state_id": user.state_id,
        },
        expires_delta=timedelta(
            minutes=settings.access_token_expire_minutes
        ),
    )

    write_audit(db, user, "LOGIN_SUCCESS", request)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "constituency_id": user.constituency_id,
            "district_id": user.district_id,
            "state_id": user.state_id,
        },
    }


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # JWT access tokens are stateless; the client discards its token.
    # The server records the logout event for the audit trail.
    write_audit(db, current_user, "LOGOUT", request)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=dict)
async def get_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "constituency_id": current_user.constituency_id,
        "district_id": current_user.district_id,
        "state_id": current_user.state_id,
    }
