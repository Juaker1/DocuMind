from typing import Optional, List, Tuple, AsyncGenerator
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

    async def _prepare_context(
        self,
        document_id: int,
        user_message: str,
        conversation_id: Optional[int] = None,  # mantenido por compatibilidad pero ignorado
    ):
        """
        Lógica compartida: obtener/crear conversación, guardar msg usuario, recuperar chunks.
        SIEMPRE usa 1 conversación por documento — ignora conversation_id del frontend.
        """
        # Buscar conversación existente para este documento
        existing = await self.conversation_repository.find_by_document_id(document_id)
        if existing:
            conversation = existing[0]
            conversation_id = conversation.id
            print(f"💬 Reutilizando conversación existente: ID {conversation_id}")
        else:
            conversation = Conversation(document_id=document_id, created_at=datetime.now())
            conversation = await self.conversation_repository.save_conversation(conversation)
            conversation_id = conversation.id
            print(f"💬 Nueva conversación creada: ID {conversation_id}")

        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            created_at=datetime.now(),
        )
        await self.conversation_repository.save_message(user_msg)
        print("💾 Mensaje de usuario guardado")

        query_embedding = self.embedding_service.generate_single_embedding(user_message)
        print("🔢 Embedding de pregunta generado")

        relevant_chunks = await self.chunk_repository.search_similar(
            embedding=query_embedding,
            document_id=document_id,
            limit=5,
        )
        print(f"🔍 Encontrados {len(relevant_chunks)} chunks relevantes")

        if not relevant_chunks:
            raise ValueError("El documento no está procesado o no tiene contenido.")

        context_chunks: List[Tuple[str, int]] = [
            (chunk.content, chunk.page_number) for chunk in relevant_chunks
        ]
        cited_pages = sorted(list(set(chunk.page_number for chunk in relevant_chunks)))

        return conversation_id, context_chunks, cited_pages, relevant_chunks

    async def execute(
        self,
        document_id: int,
        user_message: str,
        conversation_id: Optional[int] = None
    ) -> Tuple[str, int, int, List[int]]:
        """
        Versión no-streaming (para el endpoint POST /api/chat/).
        Retorna la respuesta completa de una vez.
        """
        try:
            conv_id, context_chunks, cited_pages, relevant_chunks = await self._prepare_context(
                document_id, user_message, conversation_id
            )

            response = await self.ollama_client.generate_response(
                prompt=user_message,
                context_chunks=context_chunks,
            )
            print("🤖 Respuesta generada por LLM")

            assistant_msg = Message(
                conversation_id=conv_id,
                role="assistant",
                content=response,
                created_at=datetime.now(),
                cited_chunks=[chunk.id for chunk in relevant_chunks],
            )
            assistant_msg = await self.conversation_repository.save_message(assistant_msg)
            print("✅ Chat completado exitosamente")

            return response, conv_id, assistant_msg.id, cited_pages

        except ValueError as ve:
            print(f"❌ Error de validación en chat: {str(ve)}")
            raise
        except Exception as e:
            print(f"❌ Error inesperado en chat: {str(e)}")
            raise Exception(f"Error en el chat: {str(e)}")

    async def execute_stream(
        self,
        document_id: int,
        user_message: str,
        conversation_id: Optional[int] = None,
    ) -> AsyncGenerator:
        """
        Versión streaming: yields dicts con 'chunk' (token) y al final 'done' con metadatos.
        Los tokens vienen directamente de Ollama en tiempo real.
        """
        conv_id, context_chunks, cited_pages, relevant_chunks = await self._prepare_context(
            document_id, user_message, conversation_id
        )

        full_response = ""

        async def _generator():
            nonlocal full_response
            try:
                async for token in self.ollama_client.generate_response_stream(
                    prompt=user_message,
                    context_chunks=context_chunks,
                ):
                    full_response += token
                    yield {"chunk": token}

                # Guardar mensaje del asistente una vez completado
                assistant_msg = Message(
                    conversation_id=conv_id,
                    role="assistant",
                    content=full_response,
                    created_at=datetime.now(),
                    cited_chunks=[chunk.id for chunk in relevant_chunks],
                )
                assistant_msg = await self.conversation_repository.save_message(assistant_msg)
                print("✅ Chat streaming completado y guardado")

                yield {
                    "done": True,
                    "conversation_id": conv_id,
                    "message_id": assistant_msg.id,
                    "cited_pages": cited_pages,
                    "cited_snippets": [
                        {"page": c.page_number, "text": c.content[:250].strip()}
                        for c in sorted(relevant_chunks, key=lambda x: (x.page_number, x.chunk_index))
                    ],
                }
            except Exception as e:
                print(f"❌ Error en streaming: {str(e)}")
                yield {"error": str(e)}

        return _generator()
