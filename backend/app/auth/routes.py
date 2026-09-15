# Authentication API routes
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .schemas import UserLogin, UserRegister, Token
from .security import verify_password, get_password_hash, create_access_token
from .dependencies import get_current_user
from ..database import get_db
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"id": str(new_user.id), "username": new_user.username, "email": new_user.email}


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30),
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=dict)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }
