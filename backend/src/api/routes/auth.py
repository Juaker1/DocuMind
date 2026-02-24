from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.application.dtos.user_dto import (
    RegisterRequest, LoginRequest,
    RefreshRequest, LogoutRequest,
    AuthResponse, AuthUserInfo, RefreshResponse,
)
from src.application.use_cases.register_user import RegisterUserUseCase
from src.application.use_cases.login_user import LoginUserUseCase
from src.application.use_cases.create_jwt import (
    decode_refresh_token, hash_token, create_access_token, create_refresh_token,
)
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.refresh_token_repository import RefreshTokenRepository
from src.domain.exceptions import InvalidCredentialsError, EmailAlreadyRegisteredError
from src.api.dependencies import (
    get_user_repository, get_refresh_token_repository,
    get_current_user,
)
from src.api.limiter import limiter
from src.config.settings import get_settings
from src.domain.entities.user import User
from src.infrastructure.database.connection import get_db

router = APIRouter()
settings = get_settings()


# ---------------------------------------------------------------------------
# Helper — persiste el hash del refresh token y hace commit
# ---------------------------------------------------------------------------
async def _persist_refresh_token(
    user_id: int,
    refresh_token: str,
    rt_repo: RefreshTokenRepository,
    db: AsyncSession,
) -> None:
    token_hash = hash_token(refresh_token)
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    await rt_repo.save(user_id, token_hash, expires_at)
    await db.commit()


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------
@router.post("/register", response_model=AuthResponse, status_code=201)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository),
    rt_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
    db: AsyncSession = Depends(get_db),
):
    """
    Registra un usuario con email y contraseña.
    Si ya tenía documentos como anónimo (via uuid), los preserva automáticamente.
    Devuelve access_token (corto plazo) + refresh_token (largo plazo).
    """
    use_case = RegisterUserUseCase(user_repo)
    result = await use_case.execute(body)

    await _persist_refresh_token(result["user"].id, result["refresh_token"], rt_repo, db)

    user = result["user"]
    return AuthResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user=AuthUserInfo(id=user.id, uuid=user.uuid, email=user.email, is_anonymous=user.is_anonymous),
    )


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------
@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository),
    rt_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
    db: AsyncSession = Depends(get_db),
):
    """Inicia sesión con email y contraseña, devuelve access_token + refresh_token."""
    use_case = LoginUserUseCase(user_repo)
    result = await use_case.execute(body)

    await _persist_refresh_token(result["user"].id, result["refresh_token"], rt_repo, db)

    user = result["user"]
    return AuthResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user=AuthUserInfo(id=user.id, uuid=user.uuid, email=user.email, is_anonymous=user.is_anonymous),
    )


# ---------------------------------------------------------------------------
# POST /refresh  — renueva el access token usando el refresh token
# ---------------------------------------------------------------------------
@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    body: RefreshRequest,
    user_repo: UserRepository = Depends(get_user_repository),
    rt_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh token rotation:
    1. Valida la firma y expiración del refresh token.
    2. Verifica que no esté revocado en BD.
    3. Revoca el token usado.
    4. Emite un nuevo par access + refresh.
    """
    # 1. Validar JWT del refresh token
    payload = decode_refresh_token(body.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    # 2. Buscar en BD por hash
    token_hash = hash_token(body.refresh_token)
    record = await rt_repo.find_by_hash(token_hash)
    if not record or record.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revocado")

    # 3. Verificar que el usuario sigue existiendo
    user = await user_repo.find_by_id(int(payload["user_id"]))
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    # 4. Revocar el token usado (rotation — no se puede reutilizar)
    await rt_repo.revoke(token_hash)

    # 5. Generar nuevo par y persisitir el nuevo refresh token
    claims = {"user_id": user.id, "uuid": user.uuid}
    new_access = create_access_token(claims)
    new_refresh = create_refresh_token(claims)
    await _persist_refresh_token(user.id, new_refresh, rt_repo, db)

    return RefreshResponse(access_token=new_access, refresh_token=new_refresh)


# ---------------------------------------------------------------------------
# POST /logout  — revoca el refresh token del dispositivo actual
# ---------------------------------------------------------------------------
@router.post("/logout", status_code=204)
async def logout(
    body: LogoutRequest,
    rt_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoca el refresh token enviado. El access token expirará solo.
    Para logout total en todos los dispositivos, llama a /logout-all.
    """
    token_hash = hash_token(body.refresh_token)
    await rt_repo.revoke(token_hash)
    await db.commit()


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------
@router.get("/me", response_model=AuthUserInfo)
async def me(current_user: User = Depends(get_current_user)):
    """Devuelve información del usuario actual (anónimo o registrado)."""
    return AuthUserInfo(
        id=current_user.id,
        uuid=current_user.uuid,
        email=current_user.email,
        is_anonymous=current_user.is_anonymous,
    )


# ---------------------------------------------------------------------------
# DELETE /account
# ---------------------------------------------------------------------------
@router.delete("/account", status_code=204)
async def delete_account(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
    rt_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
    db: AsyncSession = Depends(get_db),
):
    """
    Elimina la cuenta del usuario y en cascada todos sus documentos,
    chunks, conversaciones, mensajes y refresh tokens.
    """
    if current_user.is_anonymous:
        raise HTTPException(status_code=400, detail="Los usuarios anónimos no tienen cuenta que eliminar")
    # Revocar todos los refresh tokens antes de eliminar (CASCADE los elimina igual, pero es explícito)
    await rt_repo.revoke_all_for_user(current_user.id)
    await user_repo.delete(current_user.id)
    await db.commit()

