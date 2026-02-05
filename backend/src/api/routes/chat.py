from fastapi import APIRouter, Depends, HTTPException
from typing import List
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
                cited_pages=msg.cited_chunks  # Será una lista de IDs de chunks
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
    Elimina una conversación y todos sus mensajes
    
    - **conversation_id**: ID de la conversación
    """
    try:
        # Verificar que existe
        conversation = await conversation_repo.find_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        # Eliminar
        success = await conversation_repo.delete_conversation(conversation_id)
        
        if success:
            return {"message": "Conversación eliminada exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar conversación")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar conversación: {str(e)}")
