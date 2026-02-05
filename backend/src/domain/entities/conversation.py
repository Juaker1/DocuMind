from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class Conversation:
    """
    Entidad que representa una conversación sobre un documento
    
    Attributes:
        document_id: ID del documento sobre el que se conversa
        id: Identificador único de la conversación
        created_at: Fecha de creación
        title: Título opcional de la conversación
    """
    document_id: int
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    title: Optional[str] = None


@dataclass
class Message:
    """
    Entidad que representa un mensaje en una conversación
    
    Attributes:
        conversation_id: ID de la conversación
        role: Rol del mensaje ('user' o 'assistant')
        content: Contenido del mensaje
        id: Identificador único del mensaje
        created_at: Fecha de creación
        cited_chunks: IDs de los chunks citados (opcional)
    """
    conversation_id: int
    role: str  # "user" o "assistant"
    content: str
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    cited_chunks: Optional[list[int]] = None
    
    def is_user_message(self) -> bool:
        """Verifica si el mensaje es del usuario"""
        return self.role == "user"
    
    def is_assistant_message(self) -> bool:
        """Verifica si el mensaje es del asistente"""
        return self.role == "assistant"
