"""
JWT creation and verification utilities.
Uses python-jose with HS256 algorithm.

Two token types:
  access  — corto plazo (settings.access_token_expire_minutes)
             enviado en cada request como Bearer token.
  refresh — largo plazo (settings.refresh_token_expire_days)
             solo se usa en POST /auth/refresh para obtener un nuevo access token.
             se almacena su hash en BD para permitir revocación.
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from src.config.settings import get_settings

settings = get_settings()

ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    """Genera un access token JWT de corto plazo."""
    to_encode = data.copy()
    to_encode["type"] = "access"
    to_encode["exp"] = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Genera un refresh token JWT de largo plazo."""
    to_encode = data.copy()
    to_encode["type"] = "refresh"
    to_encode["exp"] = datetime.utcnow() + timedelta(
        days=settings.refresh_token_expire_days
    )
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica y valida un access token. Retorna None si es inválido/expirado."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    """Decodifica y valida un refresh token. Retorna None si es inválido/expirado."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """SHA-256 del token para almacenar en BD sin guardar el valor real."""
    return hashlib.sha256(token.encode()).hexdigest()

