from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.conversation import Conversation, Message

class ConversationRepository(ABC):
    """Interfaz del repositorio de conversaciones"""
    
    @abstractmethod
    async def save_conversation(self, conversation: Conversation) -> Conversation:
        """Guarda una nueva conversación"""
        pass
    
    @abstractmethod
    async def find_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Busca una conversación por ID"""
        pass
    
    @abstractmethod
    async def find_by_document_id(self, document_id: int) -> List[Conversation]:
        """Obtiene todas las conversaciones de un documento"""
        pass
    
    @abstractmethod
    async def save_message(self, message: Message) -> Message:
        """Guarda un mensaje en una conversación"""
        pass
    
    @abstractmethod
    async def get_messages(self, conversation_id: int) -> List[Message]:
        """Obtiene todos los mensajes de una conversación"""
        pass
    
    @abstractmethod
    async def delete_conversation(self, conversation_id: int) -> bool:
        """Elimina una conversación y todos sus mensajes"""
        pass
