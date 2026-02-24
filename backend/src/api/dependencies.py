from fastapi import Depends, Header, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.connection import get_db
from src.infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from src.infrastructure.database.repositories.document_chunk_repository_impl import DocumentChunkRepositoryImpl
from src.infrastructure.database.repositories.conversation_repository_impl import ConversationRepositoryImpl
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.document_processing.pdf_processor import PDFProcessor
from src.infrastructure.document_processing.chunker import TextChunker
from src.infrastructure.ai.embeddings import EmbeddingService
from src.infrastructure.ai.ollama_client import OllamaClient
from src.domain.repositories.document_repository import DocumentRepository
from src.domain.repositories.document_chunk_repository import DocumentChunkRepository
from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.repositories.user_repository import UserRepository
from src.application.use_cases.upload_document import UploadDocumentUseCase
from src.application.use_cases.process_document import ProcessDocumentUseCase
from src.application.use_cases.chat_with_document import ChatWithDocumentUseCase
from src.application.use_cases.get_or_create_anonymous_user import GetOrCreateAnonymousUserUseCase
from src.application.use_cases.create_jwt import decode_access_token
from src.domain.entities.user import User
from src.domain.entities.document import Document

# ============================================================================
# Repository Dependencies
# ============================================================================

async def get_document_repository(
    db: AsyncSession = Depends(get_db)
) -> DocumentRepository:
    return DocumentRepositoryImpl(db)

async def get_chunk_repository(
    db: AsyncSession = Depends(get_db)
) -> DocumentChunkRepository:
    return DocumentChunkRepositoryImpl(db)

async def get_conversation_repository(
    db: AsyncSession = Depends(get_db)
) -> ConversationRepository:
    return ConversationRepositoryImpl(db)

async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    return UserRepositoryImpl(db)

# ============================================================================
# Auth Dependency — resolves current user from JWT or anonymous UUID
# ============================================================================

async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    x_user_uuid: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Priority order:
    1. Authorization: Bearer <jwt>  → registered user from token
    2. X-User-UUID: <uuid>          → anonymous user (created if first visit)
    3. Neither                      → 401
    """
    user_repo = UserRepositoryImpl(db)

    # --- JWT path ---
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token malformado")
        user = await user_repo.find_by_id(int(user_id))
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user

    # --- Anonymous UUID path ---
    if x_user_uuid:
        use_case = GetOrCreateAnonymousUserUseCase(user_repo)
        user = await use_case.execute(x_user_uuid)
        await db.commit()  # commit the potential new user row
        return user

    raise HTTPException(
        status_code=401,
        detail="Se requiere autenticación (Bearer token o X-User-UUID header)"
    )

# ============================================================================
# Use Case Dependencies
# ============================================================================

async def get_upload_document_use_case(
    document_repo: DocumentRepository = Depends(get_document_repository),
    chunk_repo: DocumentChunkRepository = Depends(get_chunk_repository)
) -> UploadDocumentUseCase:
    return UploadDocumentUseCase(
        document_repo,
        chunk_repo,
        PDFProcessor(),
        TextChunker(),
        EmbeddingService(),
    )

async def get_process_document_use_case(
    document_repo: DocumentRepository = Depends(get_document_repository),
    chunk_repo: DocumentChunkRepository = Depends(get_chunk_repository)
) -> ProcessDocumentUseCase:
    return ProcessDocumentUseCase(
        document_repo,
        chunk_repo,
        PDFProcessor(),
        TextChunker(),
        EmbeddingService(),
    )

async def get_chat_use_case(
    conversation_repo: ConversationRepository = Depends(get_conversation_repository),
    chunk_repo: DocumentChunkRepository = Depends(get_chunk_repository)
) -> ChatWithDocumentUseCase:
    return ChatWithDocumentUseCase(
        conversation_repo,
        chunk_repo,
        OllamaClient(),
        EmbeddingService(),
    )

# ============================================================================
# Ownership — verifica que el documento exista Y pertenezca al usuario actual
# ============================================================================

async def get_document_for_current_user(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_repo: DocumentRepository = Depends(get_document_repository),
) -> Document:
    """
    Dependencia reutilizable de ownership:
    1. Busca el documento por ID.
    2. Si no existe → 404.
    3. Si existe pero no pertenece al usuario → 404 (no 403).
       Un 403 confirmaría que el recurso existe; un 404 no revela nada.

    Uso: document: Document = Depends(get_document_for_current_user)
    """
    document = await document_repo.find_by_id(document_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return document
