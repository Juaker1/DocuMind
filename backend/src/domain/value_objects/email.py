import re
from dataclasses import dataclass


_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
_MAX_EMAIL_LENGTH = 254  # RFC 5321


@dataclass(frozen=True)
class Email:
    """
    Value Object que representa una dirección de correo electrónico válida.

    Inmutable: una vez creado no puede cambiar.
    Garantiza que cualquier instancia de Email sea un email bien formado
    sin depender de Pydantic ni de la capa API.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("El email no puede estar vacío")

        normalized = self.value.strip().lower()
        # dataclass frozen=True no permite asignación directa; usamos object.__setattr__
        object.__setattr__(self, "value", normalized)

        if len(normalized) > _MAX_EMAIL_LENGTH:
            raise ValueError(
                f"El email supera los {_MAX_EMAIL_LENGTH} caracteres permitidos"
            )

        if not _EMAIL_PATTERN.match(normalized):
            raise ValueError(f"Formato de email inválido: '{normalized}'")

    def __str__(self) -> str:
        return self.value

    @property
    def domain(self) -> str:
        """Retorna el dominio del email (ej: 'gmail.com')."""
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Retorna la parte local del email (ej: 'usuario')."""
        return self.value.split("@")[0]
