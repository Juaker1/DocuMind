from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    uuid: str = Field(min_length=1, max_length=64)  # Current anonymous UUID (from X-User-UUID header)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AuthUserInfo(BaseModel):
    id: int
    uuid: str
    email: Optional[str]
    is_anonymous: bool


class AuthResponse(BaseModel):
    token: str
    user: AuthUserInfo
