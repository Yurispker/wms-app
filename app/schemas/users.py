from pydantic import BaseModel, ConfigDict, EmailStr, Field
from fastapi import Form
from app.schemas.enums import UserRole

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str
    password: str = Field(..., min_length=6, max_length=25)
    role: UserRole = UserRole.PICKER  # Default role is PICKER

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None