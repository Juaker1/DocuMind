from typing import Optional, List, Tuple
from datetime import datetime
from src.domain.entities.conversation import Conversation, Message
from src.domain.repositories.conversation_repository import ConversationRepository
from src.domain.repositories.document_chunk_repository import DocumentChunkRepository
from src.infrastructure.ai.ollama_client import OllamaClient
from src.infrastructure.ai.embeddings import EmbeddingService

class ChatWithDocumentUseCase:
    """Caso de uso para chatear con un documento usando RAG"""
    
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        chunk_repository: DocumentChunkRepository
    ):
        self.conversation_repository = conversation_repository
        self.chunk_repository = chunk_repository
        self.ollama_client = OllamaClient()
        self.embedding_service = EmbeddingService()
    
    async def execute(
        self,
        document_id: int,
        user_message: str,
        conversation_id: Optional[int] = None
    ) -> Tuple[str, int, int, List[int]]:
        """
        Procesa un mensaje del usuario y genera una respuesta basada en el documento
        
        Args:
            document_id: ID del documento
            user_message: Mensaje del usuario
            conversation_id: ID de conversación existente (None para crear nueva)
            
        Returns:
            Tuple con:
                - response: Respuesta del asistente
                - conversation_id: ID de la conversación
                - message_id: ID del mensaje del asistente
                - cited_pages: Lista de páginas citadas
        """
        try:
            # Obtener o crear conversación
            # Tratar None, 0 y valores negativos como nueva conversación
            if conversation_id is None or conversation_id <= 0:
                conversation = Conversation(
                    document_id=document_id,
                    created_at=datetime.now()
                )
                conversation = await self.conversation_repository.save_conversation(conversation)
                conversation_id = conversation.id
                print(f"💬 Nueva conversación creada: ID {conversation_id}")
            else:
                # Verificar que la conversación exista
                conversation = await self.conversation_repository.find_by_id(conversation_id)
                if not conversation:
                    raise ValueError(f"Conversación con ID {conversation_id} no encontrada")
                print(f"💬 Continuando conversación: ID {conversation_id}")
            
            # Guardar mensaje del usuario
            user_msg = Message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
                created_at=datetime.now()
            )
            await self.conversation_repository.save_message(user_msg)
            print(f"💾 Mensaje de usuario guardado")
            
            # Generar embedding de la pregunta
            try:
                query_embedding = self.embedding_service.generate_single_embedding(user_message)
                print(f"🔢 Embedding de pregunta generado")
            except Exception as e:
                raise Exception(f"Error al generar embedding de pregunta: {str(e)}")
            
            # Buscar chunks relevantes usando búsqueda vectorial
            try:
                relevant_chunks = await self.chunk_repository.search_similar(
                    embedding=query_embedding,
                    document_id=document_id,
                    limit=5  # Top 5 chunks más relevantes
                )
                print(f"🔍 Encontrados {len(relevant_chunks)} chunks relevantes")
            except Exception as e:
                raise Exception(f"Error en búsqueda vectorial: {str(e)}")
            
            if not relevant_chunks:
                # Si no hay chunks, el documento no está procesado
                raise ValueError("El documento no está procesado o no tiene contenido.")
            
            # Preparar contexto para el LLM
            context_chunks: List[Tuple[str, int]] = [
                (chunk.content, chunk.page_number)
                for chunk in relevant_chunks
            ]
            
            # Obtener páginas citadas (únicas)
            cited_pages = sorted(list(set(chunk.page_number for chunk in relevant_chunks)))
            
            # Generar respuesta con Ollama
            try:
                response = await self.ollama_client.generate_response(
                    prompt=user_message,
                    context_chunks=context_chunks
                )
                print(f"🤖 Respuesta generada por LLM")
            except Exception as e:
                raise Exception(f"Error al generar respuesta con Ollama: {str(e)}")
            
            # Guardar mensaje del asistente
            assistant_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=response,
                created_at=datetime.now(),
                cited_chunks=[chunk.id for chunk in relevant_chunks]
            )
            assistant_msg = await self.conversation_repository.save_message(assistant_msg)
            print(f"✅ Chat completado exitosamente")
            
            return response, conversation_id, assistant_msg.id, cited_pages
            
        except ValueError as ve:
            # Errores de validación esperados
            print(f"❌ Error de validación en chat: {str(ve)}")
            raise
        except Exception as e:
            # Errores inesperados
            print(f"❌ Error inesperado en chat: {str(e)}")
            raise Exception(f"Error en el chat: {str(e)}")
