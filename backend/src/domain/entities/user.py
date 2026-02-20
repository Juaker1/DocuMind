from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class User:
    """
    Entidad del dominio que representa un usuario.
    Puede ser anónimo (sólo uuid) o registrado (uuid + email + password_hash).
    """
    uuid: str
    id: Optional[int] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    is_anonymous: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def is_registered(self) -> bool:
        return not self.is_anonymous and self.email is not None
