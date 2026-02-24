from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import json
from src.application.use_cases.chat_with_document import ChatWithDocumentUseCase
from src.application.dtos.conversation_dto import (
    ChatRequest,
    ChatResponse,
    ConversationDTO,
    ConversationDetailDTO,
    MessageDTO,
    CitedSnippet,
)
from src.api.dependencies import (
    get_chat_use_case,
    get_conversation_repository,
    get_chunk_repository,
    get_current_user,
    get_user_repository,
    get_document_repository,
    get_document_for_current_user,
)
from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.repositories.document_chunk_repository import DocumentChunkRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.document_repository import DocumentRepository
from src.domain.entities.user import User
from src.domain.entities.document import Document

router = APIRouter()

@router.get("/stream")
async def stream_chat(
    document_id: int,
    message: str,
    # SSE via EventSource no puede enviar headers — tokens van por query param
    token: str = None,
    user_uuid: str = None,
    chat_use_case: ChatWithDocumentUseCase = Depends(get_chat_use_case),
    user_repo: UserRepository = Depends(get_user_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
):
    """
    Endpoint de streaming SSE para chat en tiempo real.
    Usa 1 conversación por documento — no requiere conversation_id.
    """
    from src.application.use_cases.create_jwt import decode_access_token
    from src.application.use_cases.get_or_create_anonymous_user import GetOrCreateAnonymousUserUseCase

    # 1. Resolver usuario desde query params (EventSource no soporta headers)
    user = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("user_id")
            if user_id:
                user = await user_repo.find_by_id(int(user_id))

    if user is None and user_uuid:
        anon_use_case = GetOrCreateAnonymousUserUseCase(user_repo)
        user = await anon_use_case.execute(user_uuid)

    if user is None:
        raise HTTPException(status_code=401, detail="Autenticación requerida")

    # 2. Verificar ownership ANTES de iniciar el stream
    #    (una vez abierto el stream no podemos devolver códigos HTTP)
    document = await document_repo.find_by_id(document_id)
    if not document or document.user_id != user.id:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    async def event_generator():
        try:
            gen = await chat_use_case.execute_stream(
                document_id=document_id,
                user_message=message,
            )
            async for event in gen:
                yield f"data: {json.dumps(event)}\n\n"
        except ValueError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        except Exception:
            yield f"data: {json.dumps({'error': 'Error interno en el servidor'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest,
    document: Document = Depends(get_document_for_current_user),
    chat_use_case: ChatWithDocumentUseCase = Depends(get_chat_use_case)
):
    """
    Envía un mensaje para chatear con un documento.
    La dependencia get_document_for_current_user verifica autenticación y ownership.
    """
    try:
        response, conversation_id, message_id, cited_pages = await chat_use_case.execute(
            document_id=document.id,
            user_message=request.message,
            conversation_id=request.conversation_id
        )

        return ChatResponse(
            conversation_id=conversation_id,
            message_id=message_id,
            response=response,
            cited_pages=cited_pages
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/conversations/{conversation_id}", response_model=ConversationDetailDTO)
async def get_conversation(
    conversation_id: int,
    conversation_repo: ConversationRepository = Depends(get_conversation_repository),
    chunk_repo: DocumentChunkRepository = Depends(get_chunk_repository),
):
    """
    Obtiene el historial completo de una conversación, incluyendo citas de páginas.
    """
    try:
        conversation = await conversation_repo.find_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        messages = await conversation_repo.get_messages(conversation_id)

        message_dtos = []
        for msg in messages:
            cited_pages = None
            cited_snippets = None

            if msg.cited_chunks:
                chunks = await chunk_repo.find_by_ids(msg.cited_chunks)
                # Ordenar por página para presentación consistente
                chunks_sorted = sorted(chunks, key=lambda c: (c.page_number, c.chunk_index))
                cited_pages = sorted(set(c.page_number for c in chunks_sorted))
                cited_snippets = [
                    CitedSnippet(page=c.page_number, text=c.content[:250].strip())
                    for c in chunks_sorted
                ]

            message_dtos.append(
                MessageDTO(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at,
                    cited_pages=cited_pages,
                    cited_snippets=cited_snippets,
                )
            )

        return ConversationDetailDTO(
            id=conversation.id,
            document_id=conversation.document_id,
            document_filename="",
            created_at=conversation.created_at,
            title=conversation.title,
            messages=message_dtos
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener conversación: {str(e)}")

@router.get("/documents/{document_id}/conversations", response_model=List[ConversationDTO])
async def get_document_conversations(
    document: Document = Depends(get_document_for_current_user),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository),
):
    """
    Obtiene todas las conversaciones de un documento (solo si pertenece al usuario actual).
    """
    conversations = await conversation_repo.find_by_document_id(document.id)

    result = []
    for conv in conversations:
        messages = await conversation_repo.get_messages(conv.id)
        result.append(
            ConversationDTO(
                id=conv.id,
                document_id=conv.document_id,
                created_at=conv.created_at,
                title=conv.title,
                message_count=len(messages)
            )
        )

    return result

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Elimina una conversación y todos sus mensajes.
    """
    try:
        conversation = await conversation_repo.find_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        success = await conversation_repo.delete_conversation(conversation_id)
        
        if success:
            return {"message": "Conversación eliminada exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar conversación")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar conversación: {str(e)}")


@router.delete("/documents/{document_id}/conversation")
async def reset_document_conversation(
    document: Document = Depends(get_document_for_current_user),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository),
):
    """
    Resetea (borra) la única conversación de un documento.
    El próximo mensaje creará una conversación nueva desde cero.
    """
    conversations = await conversation_repo.find_by_document_id(document.id)
    if not conversations:
        return {"message": "No hay conversación activa para este documento"}

    await conversation_repo.delete_conversation(conversations[0].id)
    return {"message": "Chat reiniciado exitosamente"}
