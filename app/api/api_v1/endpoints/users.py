from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User, UserRole
from app.schemas.users import UserCreate, UserResponse, Token
from app.security import get_password_hash, verify_password, create_access_token, get_current_user, RequireRole

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code= 201)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(RequireRole([UserRole.ADMIN]))
    ):

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code= 400,
            detail="Username already registered",
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code= 400,
            detail="Email already registered",
        )
    
    hashed_pwd = get_password_hash(user.password)

    # Creating user in database
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd,
        role = user.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(f"User '{user.username}' created by admin: {current_user.get('username')}")

    return new_user

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Look up user
    user = db.query(User).filter(User.username == form_data.username).first()

    # Validate user existence and password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code= 401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    # Generate access token
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role.value if hasattr(user.role, 'value') else user.role
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"logged_in_as": current_user}

