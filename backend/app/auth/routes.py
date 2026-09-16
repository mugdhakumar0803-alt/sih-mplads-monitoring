from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from .schemas import (
    UserLogin,
    UserRegister,
    Token,
)
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
)
from .dependencies import (
    get_current_user,
    write_audit,
)
from ..database import get_db
from ..models.user import (
    User,
    UserRole,
    ApprovalStatus,
    ParliamentHouse,
)
from ..models.revoked_token import RevokedToken
from ..config import settings


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", response_model=dict)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
):

    role_aliases = {
        "district": UserRole.DISTRICT_OFFICIAL,
        "state": UserRole.STATE_OFFICIAL,
    }
    try:
        role = role_aliases[user_data.role] if user_data.role in role_aliases else UserRole(user_data.role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid role",
        )

    house = None
    if user_data.house:
        try:
            house = ParliamentHouse(user_data.house)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid parliament house")

    existing_user = (
        db.query(User)
        .filter(
            (User.username == user_data.username)
            | (User.email == str(user_data.email))
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered",
        )

    new_user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=get_password_hash(
            user_data.password
        ),
        role=role,
        approval_status=ApprovalStatus.APPROVED,
        constituency_id=user_data.constituency_id,
        district_id=user_data.district_id,
        state_id=user_data.state_id,
        state=user_data.state,
        constituency=user_data.constituency,
        house=house,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    write_audit(
        db,
        new_user,
        "REGISTER_SUCCESS",
        request,
        resource_type="user",
        resource_id=str(new_user.id),
    )

    return {
        "id": str(new_user.id),
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role.value,
        "approval_status": new_user.approval_status.value,
    }


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(
            User.username == credentials.username
        )
        .first()
    )

    if not user or not verify_password(
        credentials.password,
        user.hashed_password,
    ):

        write_audit(
            db,
            user,
            "LOGIN_FAILURE",
            request,
            status_value="FAILURE",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:

        write_audit(
            db,
            user,
            "LOGIN_INACTIVE",
            request,
            status_value="FAILURE",
        )

        raise HTTPException(
            status_code=403,
            detail="User is inactive",
        )

    if not user.is_approved():

        write_audit(
            db,
            user,
            "LOGIN_NOT_APPROVED",
            request,
            status_value="FAILURE",
            details={
                "approval_status":
                    user.approval_status.value
            },
        )

        raise HTTPException(
            status_code=403,
            detail="Account is awaiting approval",
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role.value,
            "constituency_id":
                user.constituency_id,
            "district_id":
                user.district_id,
            "state_id":
                user.state_id,
        },
        expires_delta=timedelta(
            minutes=settings.access_token_expire_minutes
        ),
    )

    write_audit(
        db,
        user,
        "LOGIN_SUCCESS",
        request,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in":
            settings.access_token_expire_minutes * 60,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "constituency_id":
                user.constituency_id,
            "district_id":
                user.district_id,
            "state_id":
                user.state_id,
        },
    }


@router.post("/logout")
async def logout(
    request: Request,
    credentials=None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    authorization = request.headers.get(
        "Authorization"
    )

    token = authorization.split(
        " ",
        1,
    )[1]

    token_data = decode_token(token)

    if token_data is not None:

        revoked = RevokedToken(
            jti=token_data.jti,
            user_id=str(current_user.id),
            expires_at=datetime.now(
                timezone.utc
            ) + timedelta(
                minutes=settings.access_token_expire_minutes
            ),
        )

        db.add(revoked)

    write_audit(
        db,
        current_user,
        "LOGOUT",
        request,
    )

    db.commit()

    return {
        "message": "Logged out successfully"
    }


@router.get("/me", response_model=dict)
async def get_profile(
    current_user: User = Depends(
        get_current_user
    ),
):

    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "approval_status":
            current_user.approval_status.value,
        "is_active":
            current_user.is_active,
        "constituency_id":
            current_user.constituency_id,
        "district_id":
            current_user.district_id,
        "state_id":
            current_user.state_id,
        "state": current_user.state,
        "constituency": current_user.constituency,
        "house": current_user.house.value if current_user.house else None,
    }