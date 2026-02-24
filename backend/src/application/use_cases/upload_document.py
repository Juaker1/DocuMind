import os
import shutil
from datetime import datetime
from typing import BinaryIO
from src.domain.entities.document import Document
from src.domain.entities.document_chunk import DocumentChunk
from src.domain.repositories.document_repository import DocumentRepository
from src.domain.repositories.document_chunk_repository import DocumentChunkRepository
from src.application.ports import PDFProcessorPort, TextChunkerPort, EmbeddingServicePort
from src.config.settings import get_settings

settings = get_settings()

class UploadDocumentUseCase:
    """Caso de uso para subir y procesar un documento PDF"""
    
    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: DocumentChunkRepository,
        pdf_processor: PDFProcessorPort,
        chunker: TextChunkerPort,
        embedding_service: EmbeddingServicePort,
    ):
        self.document_repository = document_repository
        self.chunk_repository = chunk_repository
        self.pdf_processor = pdf_processor
        self.chunker = chunker
        self.embedding_service = embedding_service
    
    async def execute(
        self,
        file: BinaryIO,
        filename: str,
        file_size: int,
        user_id: int = None,
    ) -> Document:
        """
        Ejecuta el caso de uso de subir un documento
        
        Args:
            file: Archivo PDF
            filename: Nombre del archivo
            file_size: Tamaño del archivo
            
        Returns:
            Document: El documento creado
        """
        # Validar tamaño
        if file_size > settings.max_file_size:
            raise ValueError(f"Archivo demasiado grande. Máximo: {settings.max_file_size} bytes")
        
        # Validar extensión
        if not filename.lower().endswith('.pdf'):
            raise ValueError("Solo se permiten archivos PDF")
        
        # Crear directorio de uploads si no existe
        upload_dir = settings.upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file, buffer)
        
        # Procesar PDF para obtener número de páginas
        try:
            _, total_pages, _ = self.pdf_processor.process_pdf(file_path)
        except Exception as e:
            # Si falla el procesamiento, eliminar archivo y lanzar error
            os.remove(file_path)
            raise Exception(f"Error al procesar PDF: {str(e)}")
        
        # Crear entidad Document
        document = Document(
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            total_pages=total_pages,
            upload_date=datetime.now(),
            processed=False,
            user_id=user_id,
        )
        
        # Guardar en base de datos
        document = await self.document_repository.save(document)
        
        return document
