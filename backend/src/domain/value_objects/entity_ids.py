"""
Typed IDs para las entidades principales de DocuMind.

Envuelven un int (Primary Key de la BD) dándole semántica de tipo.
Evitan que se pase un DocumentId donde se espera un UserId, etc.

Son inmutables y comparables. Se integran en las firmas de métodos
de los repositorios y Use Cases — no en los campos de entidades ORM
(que deben permanecer como int para que SQLAlchemy los mapee sin fricción).

Uso:
    uid = UserId(42)
    doc = DocumentId(7)
    uid == doc  # False — son tipos distintos, mypy/pyright lo detectaría

    # Convertir de vuelta al int para el ORM:
    session.query(UserModel).filter_by(id=uid.value)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    """Identificador de un usuario en la base de datos."""

    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(f"UserId debe ser un entero positivo, recibido: {self.value}")

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True)
class DocumentId:
    """Identificador de un documento en la base de datos."""

    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(f"DocumentId debe ser un entero positivo, recibido: {self.value}")

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True)
class ConversationId:
    """Identificador de una conversación en la base de datos."""

    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(
                f"ConversationId debe ser un entero positivo, recibido: {self.value}"
            )

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value
