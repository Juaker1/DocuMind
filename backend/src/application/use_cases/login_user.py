from fastapi import HTTPException
from passlib.context import CryptContext
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.application.dtos.user_dto import LoginRequest
from src.application.use_cases.create_jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginUserUseCase:
    def __init__(self, user_repo: UserRepositoryImpl):
        self.user_repo = user_repo

    async def execute(self, req: LoginRequest) -> dict:
        # 1. Find user by email
        user = await self.user_repo.find_by_email(req.email)
        if user is None:
            raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

        # 2. Verify password
        if not user.password_hash or not pwd_context.verify(req.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

        # 3. Return JWT
        token = create_access_token({"user_id": user.id, "uuid": user.uuid})
        return {"token": token, "user": user}
