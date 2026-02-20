from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.user import User


class UserRepository(ABC):
    """Interfaz del repositorio de usuarios"""

    @abstractmethod
    async def find_by_uuid(self, uuid: str) -> Optional[User]:
        """Busca un usuario por su UUID anónimo"""
        ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por email (usuarios registrados)"""
        ...

    @abstractmethod
    async def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca un usuario por ID interno"""
        ...

    @abstractmethod
    async def create(self, uuid: str) -> User:
        """Crea un nuevo usuario anónimo"""
        ...

    @abstractmethod
    async def upgrade_to_registered(
        self, user_id: int, email: str, password_hash: str
    ) -> User:
        """Actualiza un usuario anónimo a registrado (in-place, preserva documentos)"""
        ...

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Elimina un usuario y en cascada sus documentos/conversaciones"""
        ...
