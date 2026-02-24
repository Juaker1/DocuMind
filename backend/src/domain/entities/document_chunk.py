from typing import Optional
from dataclasses import dataclass
from src.domain.value_objects.embedding_vector import EmbeddingVector


@dataclass
class DocumentChunk:
    """
    Entidad que representa un fragmento (chunk) de un documento
    
    Attributes:
        document_id: ID del documento al que pertenece
        content: Contenido textual del chunk
        page_number: Número de página del documento
        chunk_index: Índice del chunk dentro del documento
        id: Identificador único del chunk
        embedding: Vector de embedding (opcional, se setea en infraestructura)
    """
    document_id: int
    content: str
    page_number: int
    chunk_index: int
    id: Optional[int] = None
    embedding: Optional[EmbeddingVector] = None

    def has_embedding(self) -> bool:
        """Verifica si el chunk tiene embedding"""
        return self.embedding is not None and self.embedding.dimensions > 0
