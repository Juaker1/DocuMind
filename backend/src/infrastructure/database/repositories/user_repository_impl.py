from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        uuid=model.uuid,
        email=model.email,
        password_hash=model.password_hash,
        is_anonymous=model.is_anonymous,
        created_at=model.created_at,
    )


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_uuid(self, uuid: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.uuid == uuid)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, uuid: str) -> User:
        model = UserModel(uuid=uuid, is_anonymous=True)
        self.session.add(model)
        await self.session.flush()  # populate id
        await self.session.refresh(model)
        return _to_entity(model)

    async def upgrade_to_registered(
        self, user_id: int, email: str, password_hash: str
    ) -> User:
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(email=email, password_hash=password_hash, is_anonymous=False)
        )
        await self.session.flush()
        return await self.find_by_id(user_id)

    async def delete(self, user_id: int) -> bool:
        result = await self.session.execute(
            delete(UserModel).where(UserModel.id == user_id)
        )
        await self.session.flush()
        return result.rowcount > 0
