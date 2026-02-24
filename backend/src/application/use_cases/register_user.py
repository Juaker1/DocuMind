from passlib.context import CryptContext
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.exceptions import EmailAlreadyRegisteredError
from src.domain.value_objects.email import Email
from src.application.dtos.user_dto import RegisterRequest
from src.application.use_cases.create_jwt import create_access_token, create_refresh_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterUserUseCase:
    """
    Convierte un usuario anónimo en registrado (upgrade in-place).
    Los documentos/conversaciones ya vinculados al user_id se preservan sin migración.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, req: RegisterRequest) -> dict:
        # 0. Validar formato de email a nivel de dominio (independiente de Pydantic/API)
        email = Email(req.email)

        # 1. Check email not taken
        existing = await self.user_repo.find_by_email(email.value)
        if existing is not None:
            raise EmailAlreadyRegisteredError(email.value)

        # 2. Find the anonymous user by UUID
        user = await self.user_repo.find_by_uuid(req.uuid)
        if user is None:
            # Edge case: fresh device with no prior anonymous session
            user = await self.user_repo.create(req.uuid)

        # 3. Hash password
        hashed = pwd_context.hash(req.password)

        # 4. Upgrade in-place (same user_id → all docs preserved automatically)
        user = await self.user_repo.upgrade_to_registered(user.id, email.value, hashed)

        # 5. Return both tokens
        claims = {"user_id": user.id, "uuid": user.uuid}
        access_token = create_access_token(claims)
        refresh_token = create_refresh_token(claims)
        return {"access_token": access_token, "refresh_token": refresh_token, "user": user}
