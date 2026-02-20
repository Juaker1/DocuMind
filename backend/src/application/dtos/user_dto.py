from typing import Optional
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    uuid: str  # Current anonymous UUID (from X-User-UUID header)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthUserInfo(BaseModel):
    id: int
    uuid: str
    email: Optional[str]
    is_anonymous: bool


class AuthResponse(BaseModel):
    token: str
    user: AuthUserInfo
