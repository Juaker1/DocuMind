from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    uuid: str = Field(min_length=1, max_length=64)  # Current anonymous UUID (from X-User-UUID header)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class AuthUserInfo(BaseModel):
    id: int
    uuid: str
    email: Optional[str]
    is_anonymous: bool


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: AuthUserInfo


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
