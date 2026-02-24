from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
    RefreshTokenRecord,
)
from src.infrastructure.database.models import RefreshTokenModel


def _to_record(model: RefreshTokenModel) -> RefreshTokenRecord:
    return RefreshTokenRecord(
        id=model.id,
        user_id=model.user_id,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
        revoked=model.revoked,
        created_at=model.created_at,
    )


class RefreshTokenRepositoryImpl(RefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user_id: int, token_hash: str, expires_at: datetime) -> None:
        """Persiste un nuevo refresh token (hash SHA-256)."""
        record = RefreshTokenModel(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False,
        )
        self.session.add(record)
        await self.session.flush()  # el commit lo hace el caller (route handler)

    async def find_by_hash(self, token_hash: str) -> Optional[RefreshTokenRecord]:
        """Busca un refresh token por su hash SHA-256."""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        return _to_record(model) if model else None

    async def revoke(self, token_hash: str) -> None:
        """Marca un token como revocado sin eliminarlo (auditoría)."""
        await self.session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
            .values(revoked=True)
        )

    async def revoke_all_for_user(self, user_id: int) -> None:
        """Logout total: revoca todos los tokens activos de un usuario."""
        await self.session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked == False,  # noqa: E712
            )
            .values(revoked=True)
        )
