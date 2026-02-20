from fastapi import Depends, Header, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.connection import get_db
from src.infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from src.infrastructure.database.repositories.document_chunk_repository_impl import DocumentChunkRepositoryImpl
from src.infrastructure.database.repositories.conversation_repository_impl import ConversationRepositoryImpl
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.application.use_cases.upload_document import UploadDocumentUseCase
from src.application.use_cases.process_document import ProcessDocumentUseCase
from src.application.use_cases.chat_with_document import ChatWithDocumentUseCase
from src.application.use_cases.get_or_create_anonymous_user import GetOrCreateAnonymousUserUseCase
from src.application.use_cases.create_jwt import decode_access_token
from src.domain.entities.user import User

# ============================================================================
# Repository Dependencies
# ============================================================================

async def get_document_repository(
    db: AsyncSession = Depends(get_db)
) -> DocumentRepositoryImpl:
    return DocumentRepositoryImpl(db)

async def get_chunk_repository(
    db: AsyncSession = Depends(get_db)
) -> DocumentChunkRepositoryImpl:
    return DocumentChunkRepositoryImpl(db)

async def get_conversation_repository(
    db: AsyncSession = Depends(get_db)
) -> ConversationRepositoryImpl:
    return ConversationRepositoryImpl(db)

async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepositoryImpl:
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
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository),
    chunk_repo: DocumentChunkRepositoryImpl = Depends(get_chunk_repository)
) -> UploadDocumentUseCase:
    return UploadDocumentUseCase(document_repo, chunk_repo)

async def get_process_document_use_case(
    document_repo: DocumentRepositoryImpl = Depends(get_document_repository),
    chunk_repo: DocumentChunkRepositoryImpl = Depends(get_chunk_repository)
) -> ProcessDocumentUseCase:
    return ProcessDocumentUseCase(document_repo, chunk_repo)

async def get_chat_use_case(
    conversation_repo: ConversationRepositoryImpl = Depends(get_conversation_repository),
    chunk_repo: DocumentChunkRepositoryImpl = Depends(get_chunk_repository)
) -> ChatWithDocumentUseCase:
    return ChatWithDocumentUseCase(conversation_repo, chunk_repo)
