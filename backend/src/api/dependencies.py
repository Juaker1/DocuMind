from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.connection import get_db
from src.infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from src.infrastructure.database.repositories.document_chunk_repository_impl import DocumentChunkRepositoryImpl
from src.infrastructure.database.repositories.conversation_repository_impl import ConversationRepositoryImpl
from src.application.use_cases.upload_document import UploadDocumentUseCase
from src.application.use_cases.process_document import ProcessDocumentUseCase
from src.application.use_cases.chat_with_document import ChatWithDocumentUseCase

# ============================================================================
# Repository Dependencies
# ============================================================================

async def get_document_repository(
    db: AsyncSession = Depends(get_db)
) -> DocumentRepositoryImpl:
    """Dependency para obtener el repositorio de documentos"""
    return DocumentRepositoryImpl(db)

async def get_chunk_repository(
    db: AsyncSession = Depends(get_db)
) -> DocumentChunkRepositoryImpl:
    """Dependency para obtener el repositorio de chunks"""
    return DocumentChunkRepositoryImpl(db)

async def get_conversation_repository(
    db: AsyncSession = Depends(get_db)
) -> ConversationRepositoryImpl:
    """Dependency para obtener el repositorio de conversaciones"""
    return ConversationRepositoryImpl(db)

# ============================================================================
# Use Case Dependencies
# ============================================================================

async def get_upload_document_use_case(
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository),
    chunk_repo: DocumentChunkRepositoryImpl = Depends(get_chunk_repository)
) -> UploadDocumentUseCase:
    """Dependency para obtener el caso de uso de upload document"""
    return UploadDocumentUseCase(document_repo, chunk_repo)

async def get_process_document_use_case(
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository),
    chunk_repo: DocumentChunkRepositoryImpl = Depends(get_chunk_repository)
) -> ProcessDocumentUseCase:
    """Dependency para obtener el caso de uso de process document"""
    return ProcessDocumentUseCase(document_repo, chunk_repo)

async def get_chat_use_case(
    conversation_repo: ConversationRepositoryImpl = Depends(get_conversation_repository),
    chunk_repo: DocumentChunkRepositoryImpl = Depends(get_chunk_repository)
) -> ChatWithDocumentUseCase:
    """Dependency para obtener el caso de uso de chat"""
    return ChatWithDocumentUseCase(conversation_repo, chunk_repo)
