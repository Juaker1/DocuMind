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
    MessageDTO
)
from src.api.dependencies import get_chat_use_case, get_conversation_repository
from src.infrastructure.database.repositories.conversation_repository_impl import ConversationRepositoryImpl

router = APIRouter()

@router.get("/stream")
async def stream_chat(
    document_id: int,
    message: str,
    chat_use_case: ChatWithDocumentUseCase = Depends(get_chat_use_case)
):
    """
    Endpoint de streaming SSE para chat en tiempo real.
    Usa 1 conversación por documento — no requiere conversation_id.
    """
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
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Error interno: {str(e)}'})}\n\n"

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
    chat_use_case: ChatWithDocumentUseCase = Depends(get_chat_use_case)
):
    """
    Envía un mensaje para chatear con un documento
    
    - **document_id**: ID del documento
    - **message**: Mensaje del usuario
    - **conversation_id**: (Opcional) ID de conversación existente
    
    Utiliza RAG (Retrieval-Augmented Generation) para responder basándose en el contenido del documento.
    """
    try:
        response, conversation_id, message_id, cited_pages = await chat_use_case.execute(
            document_id=request.document_id,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el chat: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=ConversationDetailDTO)
async def get_conversation(
    conversation_id: int,
    conversation_repo: ConversationRepositoryImpl = Depends(get_conversation_repository)
):
    """
    Obtiene el historial completo de una conversación
    
    - **conversation_id**: ID de la conversación
    """
    try:
        # Obtener conversación
        conversation = await conversation_repo.find_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        # Obtener mensajes
        messages = await conversation_repo.get_messages(conversation_id)
        
        # Convertir a DTOs
        message_dtos = [
            MessageDTO(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at,
                cited_pages=None  # cited_chunks son IDs de chunks, no números de página
            )
            for msg in messages
        ]
        
        return ConversationDetailDTO(
            id=conversation.id,
            document_id=conversation.document_id,
            document_filename="",  # TODO: Obtener desde documento
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
    document_id: int,
    conversation_repo: ConversationRepositoryImpl = Depends(get_conversation_repository)
):
    """
    Obtiene todas las conversaciones de un documento
    
    - **document_id**: ID del documento
    """
    try:
        conversations = await conversation_repo.find_by_document_id(document_id)
        
        conversation_dtos = []
        for conv in conversations:
            # Contar mensajes
            messages = await conversation_repo.get_messages(conv.id)
            
            conversation_dtos.append(
                ConversationDTO(
                    id=conv.id,
                    document_id=conv.document_id,
                    created_at=conv.created_at,
                    title=conv.title,
                    message_count=len(messages)
                )
            )
        
        return conversation_dtos
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener conversaciones: {str(e)}")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    conversation_repo: ConversationRepositoryImpl = Depends(get_conversation_repository)
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
    document_id: int,
    conversation_repo: ConversationRepositoryImpl = Depends(get_conversation_repository)
):
    """
    Resetea (borra) la única conversación de un documento.
    El próximo mensaje creará una conversación nueva desde cero.
    """
    try:
        conversations = await conversation_repo.find_by_document_id(document_id)
        if not conversations:
            # Nada que borrar — devolvemos ok igual
            return {"message": "No hay conversación activa para este documento"}
        
        conv = conversations[0]
        await conversation_repo.delete_conversation(conv.id)
        return {"message": "Chat reiniciado exitosamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al resetear conversación: {str(e)}")
