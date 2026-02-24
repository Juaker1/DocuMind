from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional
from src.application.dtos.user_dto import RegisterRequest, LoginRequest, AuthResponse, AuthUserInfo
from src.application.use_cases.register_user import RegisterUserUseCase
from src.application.use_cases.login_user import LoginUserUseCase
from src.domain.repositories.user_repository import UserRepository
from src.domain.exceptions import InvalidCredentialsError, EmailAlreadyRegisteredError
from src.api.dependencies import get_user_repository, get_current_user
from src.domain.entities.user import User

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Registra un usuario con email y contraseña.
    Si ya tenía documentos como anónimo (via uuid), los preserva automáticamente.
    """
    try:
        use_case = RegisterUserUseCase(user_repo)
        result = await use_case.execute(body)
    except EmailAlreadyRegisteredError as e:
        raise HTTPException(status_code=409, detail=str(e))
    user = result["user"]
    return AuthResponse(
        token=result["token"],
        user=AuthUserInfo(
            id=user.id,
            uuid=user.uuid,
            email=user.email,
            is_anonymous=user.is_anonymous,
        )
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """Inicia sesión con email y contraseña, devuelve JWT."""
    try:
        use_case = LoginUserUseCase(user_repo)
        result = await use_case.execute(body)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))
    user = result["user"]
    return AuthResponse(
        token=result["token"],
        user=AuthUserInfo(
            id=user.id,
            uuid=user.uuid,
            email=user.email,
            is_anonymous=user.is_anonymous,
        )
    )


@router.get("/me", response_model=AuthUserInfo)
async def me(current_user: User = Depends(get_current_user)):
    """Devuelve información del usuario actual (anónimo o registrado)."""
    return AuthUserInfo(
        id=current_user.id,
        uuid=current_user.uuid,
        email=current_user.email,
        is_anonymous=current_user.is_anonymous,
    )


@router.delete("/account", status_code=204)
async def delete_account(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Elimina la cuenta del usuario y en cascada todos sus documentos,
    chunks, conversaciones y mensajes.
    """
    if current_user.is_anonymous:
        raise HTTPException(status_code=400, detail="Los usuarios anónimos no tienen cuenta que eliminar")
    await user_repo.delete(current_user.id)
