from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    """Response cuando se sube un documento"""
    id: int
    filename: str
    file_size: int
    total_pages: int
    upload_date: datetime
    processed: bool
    
    class Config:
        from_attributes = True

class DocumentListItem(BaseModel):
    """Item de documento para listados"""
    id: int
    filename: str
    file_size: int
    total_pages: int
    upload_date: datetime
    processed: bool
    has_conversation: bool = False
    
    class Config:
        from_attributes = True

class DocumentDetail(BaseModel):
    """Detalles completos de un documento"""
    id: int
    filename: str
    file_size: int
    total_pages: int
    upload_date: datetime
    processed: bool
    conversation_count: int = 0
    
    class Config:
        from_attributes = True
