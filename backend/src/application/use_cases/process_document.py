from typing import List
from src.domain.entities.document import Document
from src.domain.entities.document_chunk import DocumentChunk
from src.domain.repositories.document_repository import DocumentRepository
from src.domain.repositories.document_chunk_repository import DocumentChunkRepository
from src.infrastructure.document_processing.pdf_processor import PDFProcessor
from src.infrastructure.document_processing.chunker import TextChunker
from src.infrastructure.ai.embeddings import EmbeddingService

class ProcessDocumentUseCase:
    """Caso de uso para procesar un documento y generar embeddings"""
    
    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: DocumentChunkRepository
    ):
        self.document_repository = document_repository
        self.chunk_repository = chunk_repository
        self.pdf_processor = PDFProcessor()
        self.chunker = TextChunker()
        self.embedding_service = EmbeddingService()
    
    async def execute(self, document_id: int) -> List[DocumentChunk]:
        """
        Procesa un documento: extrae texto, crea chunks y genera embeddings
        
        Args:
            document_id: ID del documento a procesar
            
        Returns:
            List[DocumentChunk]: Lista de chunks creados
        """
        try:
            # Obtener documento
            document = await self.document_repository.find_by_id(document_id)
            if not document:
                raise ValueError(f"Documento con ID {document_id} no encontrado")
            
            if document.processed:
                raise ValueError("El documento ya fue procesado")
            
            print(f"📄 Procesando documento: {document.filename}")
            
            # Procesar PDF
            try:
                full_text, total_pages, pages_content = self.pdf_processor.process_pdf(
                    document.file_path
                )
                print(f"✅ PDF procesado: {total_pages} páginas")
            except Exception as e:
                raise Exception(f"Error al procesar PDF: {str(e)}")
            
            # Dividir en chunks
            chunks_data = self.chunker.chunk_pages(pages_content)
            print(f"📝 Creados {len(chunks_data)} chunks de texto")
            
            if not chunks_data:
                raise ValueError("No se pudieron extraer chunks del documento")
            
            # Generar embeddings para todos los chunks
            try:
                chunk_texts = [chunk_text for chunk_text, _, _ in chunks_data]
                embeddings = self.embedding_service.generate_embeddings(chunk_texts)
                print(f"🔢 Generados {len(embeddings)} embeddings")
            except Exception as e:
                raise Exception(f"Error al generar embeddings: {str(e)}")
            
            # Crear entidades DocumentChunk
            chunks = []
            for (chunk_text, page_number, chunk_index), embedding in zip(chunks_data, embeddings):
                chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk_text,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    embedding=embedding
                )
                chunks.append(chunk)
            
            # Guardar chunks en base de datos
            try:
                saved_chunks = await self.chunk_repository.save_chunks(chunks)
                print(f"💾 Guardados {len(saved_chunks)} chunks en BD")
            except Exception as e:
                raise Exception(f"Error al guardar chunks en BD: {str(e)}")
            
            # Marcar documento como procesado
            document.mark_as_processed()
            await self.document_repository.update(document)
            
            print(f"✅ Documento procesado exitosamente")
            
            return saved_chunks
            
        except ValueError as ve:
            # Errores de validación esperados
            print(f"❌ Error de validación: {str(ve)}")
            raise
        except Exception as e:
            # Errores inesperados
            print(f"❌ Error inesperado al procesar documento: {str(e)}")
            raise Exception(f"Error al procesar documento: {str(e)}")
