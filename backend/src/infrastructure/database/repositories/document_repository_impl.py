from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, exists
from src.domain.entities.document import Document
from src.domain.repositories.document_repository import DocumentRepository
from src.infrastructure.database.models import DocumentModel

class DocumentRepositoryImpl(DocumentRepository):
    """Implementación del repositorio de documentos usando SQLAlchemy"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, document: Document) -> Document:
        """Guarda un documento en la base de datos"""
        db_document = DocumentModel(
            filename=document.filename,
            file_path=document.file_path,
            file_size=document.file_size,
            total_pages=document.total_pages,
            upload_date=document.upload_date,
            processed=document.processed,
            user_id=document.user_id
        )
        
        self.session.add(db_document)
        await self.session.flush()
        await self.session.refresh(db_document)
        
        # Mapear de vuelta a entidad de dominio
        return self._to_entity(db_document)
    
    async def find_by_id(self, document_id: int) -> Optional[Document]:
        """Busca un documento por su ID"""
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        db_document = result.scalar_one_or_none()
        
        if db_document:
            return self._to_entity(db_document)
        return None
    
    async def find_all(self, user_id: Optional[int] = None) -> List[Document]:
        """Obtiene todos los documentos, opcionalmente filtrados por usuario"""
        query = select(DocumentModel)
        
        if user_id is not None:
            query = query.where(DocumentModel.user_id == user_id)
        
        result = await self.session.execute(query)
        db_documents = result.scalars().all()
        
        return [self._to_entity(doc) for doc in db_documents]
    
    async def delete(self, document_id: int) -> bool:
        """Elimina un documento"""
        result = await self.session.execute(
            delete(DocumentModel).where(DocumentModel.id == document_id)
        )
        await self.session.flush()
        
        return result.rowcount > 0
    
    async def update(self, document: Document) -> Document:
        """Actualiza un documento existente"""
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == document.id)
        )
        db_document = result.scalar_one_or_none()
        
        if not db_document:
            raise ValueError(f"Document with id {document.id} not found")
        
        db_document.filename = document.filename
        db_document.file_path = document.file_path
        db_document.file_size = document.file_size
        db_document.total_pages = document.total_pages
        db_document.processed = document.processed
        db_document.user_id = document.user_id
        
        await self.session.flush()
        await self.session.refresh(db_document)
        
        return self._to_entity(db_document)
    
    def _to_entity(self, db_document: DocumentModel) -> Document:
        """Convierte un modelo de base de datos a entidad de dominio"""
        return Document(
            id=db_document.id,
            filename=db_document.filename,
            file_path=db_document.file_path,
            file_size=db_document.file_size,
            total_pages=db_document.total_pages,
            upload_date=db_document.upload_date,
            processed=db_document.processed,
            user_id=db_document.user_id
        )

    async def find_with_conversation_status(
        self, user_id: int
    ) -> List[Tuple[Document, bool]]:
        """Devuelve documentos del usuario con flag de si tienen conversación."""
        from src.infrastructure.database.models import ConversationModel

        conv_exists = (
            select(ConversationModel.id)
            .where(ConversationModel.document_id == DocumentModel.id)
            .correlate(DocumentModel)
            .exists()
        )
        stmt = (
            select(DocumentModel, conv_exists.label("has_conversation"))
            .where(DocumentModel.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [(self._to_entity(doc), bool(has_conv)) for doc, has_conv in rows]
