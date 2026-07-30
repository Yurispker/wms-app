from pydantic import BaseModel, EmailStr
from fastapi import Form

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class cleanLoginForm(BaseModel):
    username: str
    password: str
    # Cleaning up the login form
    @classmethod
    def as_form(
        cls,
        username: str = Form(..., description="The username of the user"),
        password: str = Form(..., description="The password of the user")
    ):
        return cls(username=username, password=password)