from passlib.context import CryptContext
from src.domain.repositories.user_repository import UserRepository
from src.domain.exceptions import InvalidCredentialsError
from src.domain.value_objects.email import Email
from src.application.dtos.user_dto import LoginRequest
from src.application.use_cases.create_jwt import create_access_token, create_refresh_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, req: LoginRequest) -> dict:
        # 0. Validar formato de email a nivel de dominio
        email = Email(req.email)

        # 1. Find user by email
        user = await self.user_repo.find_by_email(email.value)
        if user is None:
            raise InvalidCredentialsError()

        # 2. Verify password
        if not user.password_hash or not pwd_context.verify(req.password, user.password_hash):
            raise InvalidCredentialsError()

        # 3. Return both tokens
        claims = {"user_id": user.id, "uuid": user.uuid}
        access_token = create_access_token(claims)
        refresh_token = create_refresh_token(claims)
        return {"access_token": access_token, "refresh_token": refresh_token, "user": user}
