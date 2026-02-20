from src.domain.entities.user import User
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl


class GetOrCreateAnonymousUserUseCase:
    """
    Dado un UUID (de la cabecera X-User-UUID), busca el usuario o lo crea.
    Siempre retorna un User con un ID válido en la BD.
    """

    def __init__(self, user_repo: UserRepositoryImpl):
        self.user_repo = user_repo

    async def execute(self, uuid: str) -> User:
        user = await self.user_repo.find_by_uuid(uuid)
        if user is None:
            user = await self.user_repo.create(uuid)
        return user
