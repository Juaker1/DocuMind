from fastapi import HTTPException
from passlib.context import CryptContext
from src.domain.entities.user import User
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.application.dtos.user_dto import RegisterRequest
from src.application.use_cases.create_jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterUserUseCase:
    """
    Convierte un usuario anónimo en registrado (upgrade in-place).
    Los documentos/conversaciones ya vinculados al user_id se preservan sin migración.
    """

    def __init__(self, user_repo: UserRepositoryImpl):
        self.user_repo = user_repo

    async def execute(self, req: RegisterRequest) -> dict:
        # 1. Check email not taken
        existing = await self.user_repo.find_by_email(req.email)
        if existing is not None:
            raise HTTPException(status_code=409, detail="El email ya está registrado")

        # 2. Find the anonymous user by UUID
        user = await self.user_repo.find_by_uuid(req.uuid)
        if user is None:
            # Edge case: fresh device with no prior anonymous session
            user = await self.user_repo.create(req.uuid)

        # 3. Hash password
        hashed = pwd_context.hash(req.password)

        # 4. Upgrade in-place (same user_id → all docs preserved automatically)
        user = await self.user_repo.upgrade_to_registered(user.id, req.email, hashed)

        # 5. Return JWT
        token = create_access_token({"user_id": user.id, "uuid": user.uuid})
        return {"token": token, "user": user}
