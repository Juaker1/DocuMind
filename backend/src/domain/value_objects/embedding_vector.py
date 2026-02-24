from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class EmbeddingVector:
    """
    Value Object que representa un vector de embedding de dimensión fija.

    - Inmutable: garantiza que el vector no cambie después de ser generado.
    - Valida que no esté vacío en construcción.
    - Expone helpers de uso frecuente en RAG (dimensiones, serialización).

    Uso típico:
        vector = EmbeddingVector.from_list([0.1, 0.2, ...])
        serialized = vector.to_db_string()   # para pgvector
    """

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise ValueError("EmbeddingVector no puede estar vacío")

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @classmethod
    def from_list(cls, values: List[float]) -> "EmbeddingVector":
        """Crea un EmbeddingVector desde una lista de floats."""
        return cls(values=tuple(values))

    @classmethod
    def zeros(cls, dimensions: int) -> "EmbeddingVector":
        """Crea un vector nulo de `dimensions` dimensiones (fallback para texto vacío)."""
        if dimensions <= 0:
            raise ValueError("Las dimensiones deben ser un entero positivo")
        return cls(values=tuple(0.0 for _ in range(dimensions)))

    # ------------------------------------------------------------------
    # Propiedades
    # ------------------------------------------------------------------

    @property
    def dimensions(self) -> int:
        """Número de dimensiones del vector."""
        return len(self.values)

    # ------------------------------------------------------------------
    # Serialización / interoperabilidad
    # ------------------------------------------------------------------

    def to_list(self) -> List[float]:
        """Convierte a lista de floats (compat. con SQLAlchemy / pgvector)."""
        return list(self.values)

    def to_db_string(self) -> str:
        """Serializa al formato que espera pgvector: '[f1,f2,...]'."""
        return f"[{','.join(map(str, self.values))}]"

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def magnitude(self) -> float:
        """Norma euclidiana del vector."""
        return math.sqrt(sum(v * v for v in self.values))
