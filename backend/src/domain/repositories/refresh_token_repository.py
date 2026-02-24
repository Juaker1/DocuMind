"""
Interfaz de repositorio para refresh tokens.
Permite almacenar, buscar y revocar refresh tokens de forma agnóstica a la BD.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RefreshTokenRecord:
    """Representa un refresh token almacenado en BD (sin el valor original)."""
    id: int
    user_id: int
    token_hash: str
    expires_at: datetime
    revoked: bool
    created_at: datetime


class RefreshTokenRepository(ABC):
    """Interfaz para operaciones CRUD sobre refresh tokens."""

    @abstractmethod
    async def save(self, user_id: int, token_hash: str, expires_at: datetime) -> None:
        """Persiste un nuevo refresh token (como hash SHA-256)."""
        ...

    @abstractmethod
    async def find_by_hash(self, token_hash: str) -> Optional[RefreshTokenRecord]:
        """Busca un refresh token por su hash. Retorna None si no existe."""
        ...

    @abstractmethod
    async def revoke(self, token_hash: str) -> None:
        """Marca un token como revocado (refresh token rotation)."""
        ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: int) -> None:
        """Revoca todos los refresh tokens de un usuario (logout total)."""
        ...
