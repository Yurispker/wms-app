from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.users.models import User
from app.users.schemas import UserCreate, UserResponse
from app.security import get_password_hash, verify_password

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Hash the password
    hashed_pwd = get_password_hash(user.password)

    # Create the database user instance
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user