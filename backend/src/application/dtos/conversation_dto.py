from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    """Request para chatear con un documento"""
    document_id: int = Field(..., description="ID del documento")
    message: str = Field(..., min_length=1, max_length=5000, description="Mensaje del usuario")
    conversation_id: Optional[int] = Field(default=None, description="ID de conversación existente (None para nueva)")

class ChatResponse(BaseModel):
    """Response del chat"""
    conversation_id: int
    message_id: int
    response: str
    cited_pages: List[int] = Field(default_factory=list, description="Páginas citadas en la respuesta")
    
    class Config:
        from_attributes = True

class MessageDTO(BaseModel):
    """DTO para un mensaje individual"""
    id: int
    role: str  # "user" o "assistant"
    content: str
    created_at: datetime
    cited_pages: Optional[List[int]] = None
    
    class Config:
        from_attributes = True

class ConversationDTO(BaseModel):
    """DTO para una conversación"""
    id: int
    document_id: int
    created_at: datetime
    title: Optional[str] = None
    message_count: int = 0
    
    class Config:
        from_attributes = True

class ConversationDetailDTO(BaseModel):
    """DTO con detalles completos de una conversación"""
    id: int
    document_id: int
    document_filename: str
    created_at: datetime
    title: Optional[str] = None
    messages: List[MessageDTO] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
