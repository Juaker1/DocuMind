from typing import List, Optional
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from src.domain.entities.conversation import Conversation, Message
from src.domain.repositories.conversation_repository import ConversationRepository
from src.infrastructure.database.models import ConversationModel, MessageModel

class ConversationRepositoryImpl(ConversationRepository):
    """Implementación del repositorio de conversaciones"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_conversation(self, conversation: Conversation) -> Conversation:
        """Guarda una nueva conversación"""
        db_conversation = ConversationModel(
            document_id=conversation.document_id,
            created_at=conversation.created_at,
            title=conversation.title
        )
        
        self.session.add(db_conversation)
        await self.session.flush()
        await self.session.refresh(db_conversation)
        
        return self._conversation_to_entity(db_conversation)
    
    async def find_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Busca una conversación por ID"""
        result = await self.session.execute(
            select(ConversationModel).where(ConversationModel.id == conversation_id)
        )
        db_conversation = result.scalar_one_or_none()
        
        if db_conversation:
            return self._conversation_to_entity(db_conversation)
        return None
    
    async def find_by_document_id(self, document_id: int) -> List[Conversation]:
        """Obtiene todas las conversaciones de un documento"""
        result = await self.session.execute(
            select(ConversationModel)
            .where(ConversationModel.document_id == document_id)
            .order_by(ConversationModel.created_at.desc())
        )
        db_conversations = result.scalars().all()
        
        return [self._conversation_to_entity(conv) for conv in db_conversations]
    
    async def save_message(self, message: Message) -> Message:
        """Guarda un mensaje en una conversación"""
        # Serializar cited_chunks a JSON si existe
        cited_chunks_json = None
        if message.cited_chunks:
            cited_chunks_json = json.dumps(message.cited_chunks)
        
        db_message = MessageModel(
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
            cited_chunks=cited_chunks_json
        )
        
        self.session.add(db_message)
        await self.session.flush()
        await self.session.refresh(db_message)
        
        return self._message_to_entity(db_message)
    
    async def get_messages(self, conversation_id: int) -> List[Message]:
        """Obtiene todos los mensajes de una conversación"""
        result = await self.session.execute(
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at)
        )
        db_messages = result.scalars().all()
        
        return [self._message_to_entity(msg) for msg in db_messages]
    
    async def delete_conversation(self, conversation_id: int) -> bool:
        """Elimina una conversación y todos sus mensajes"""
        result = await self.session.execute(
            delete(ConversationModel).where(ConversationModel.id == conversation_id)
        )
        await self.session.flush()
        
        return result.rowcount > 0
    
    def _conversation_to_entity(self, db_conversation: ConversationModel) -> Conversation:
        """Convierte un modelo de conversación a entidad de dominio"""
        return Conversation(
            id=db_conversation.id,
            document_id=db_conversation.document_id,
            created_at=db_conversation.created_at,
            title=db_conversation.title
        )
    
    def _message_to_entity(self, db_message: MessageModel) -> Message:
        """Convierte un modelo de mensaje a entidad de dominio"""
        # Deserializar cited_chunks de JSON si existe
        cited_chunks = None
        if db_message.cited_chunks:
            try:
                cited_chunks = json.loads(db_message.cited_chunks)
            except json.JSONDecodeError:
                cited_chunks = None
        
        return Message(
            id=db_message.id,
            conversation_id=db_message.conversation_id,
            role=db_message.role,
            content=db_message.content,
            created_at=db_message.created_at,
            cited_chunks=cited_chunks
        )
