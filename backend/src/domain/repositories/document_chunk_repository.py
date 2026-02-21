from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.document_chunk import DocumentChunk

class DocumentChunkRepository(ABC):
    """
    Interfaz del repositorio de chunks de documentos
    """
    
    @abstractmethod
    async def save_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Guarda múltiples chunks de un documento
        
        Args:
            chunks: Lista de chunks a guardar
            
        Returns:
            List[DocumentChunk]: Chunks guardados con sus IDs
        """
        pass
    
    @abstractmethod
    async def find_by_document_id(self, document_id: int) -> List[DocumentChunk]:
        """
        Obtiene todos los chunks de un documento
        
        Args:
            document_id: ID del documento
            
        Returns:
            List[DocumentChunk]: Lista de chunks del documento
        """
        pass

    @abstractmethod
    async def find_by_ids(self, ids: List[int]) -> List[DocumentChunk]:
        """
        Obtiene chunks por sus IDs (para resolver citas del historial).

        Args:
            ids: Lista de IDs de chunks

        Returns:
            List[DocumentChunk]: Chunks encontrados
        """
        pass
    
    @abstractmethod
    async def search_similar(
        self, 
        embedding: List[float], 
        document_id: int,
        limit: int = 5
    ) -> List[DocumentChunk]:
        """
        Busca los chunks más similares usando búsqueda vectorial
        
        Args:
            embedding: Vector de embedding de la consulta
            document_id: ID del documento donde buscar
            limit: Número máximo de resultados
            
        Returns:
            List[DocumentChunk]: Chunks más relevantes ordenados por similaridad
        """
        pass
    
    @abstractmethod
    async def delete_by_document_id(self, document_id: int) -> bool:
        """
        Elimina todos los chunks de un documento
        
        Args:
            document_id: ID del documento
            
        Returns:
            bool: True si se eliminaron correctamente
        """
        pass
