from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from src.domain.entities.document import Document

class DocumentRepository(ABC):
    """
    Interfaz del repositorio de documentos (Port)
    Define las operaciones de persistencia para documentos
    """
    
    @abstractmethod
    async def save(self, document: Document) -> Document:
        """
        Guarda un documento en la base de datos
        
        Args:
            document: Entidad Document a guardar
            
        Returns:
            Document: El documento guardado con su ID asignado
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, document_id: int) -> Optional[Document]:
        """
        Busca un documento por su ID
        
        Args:
            document_id: ID del documento
            
        Returns:
            Optional[Document]: El documento si existe, None si no
        """
        pass
    
    @abstractmethod
    async def find_all(self, user_id: Optional[int] = None) -> List[Document]:
        """
        Obtiene todos los documentos, opcionalmente filtrados por usuario
        
        Args:
            user_id: ID del usuario (opcional)
            
        Returns:
            List[Document]: Lista de documentos
        """
        pass
    
    @abstractmethod
    async def delete(self, document_id: int) -> bool:
        """
        Elimina un documento
        
        Args:
            document_id: ID del documento a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """

    @abstractmethod
    async def find_with_conversation_status(
        self, user_id: int
    ) -> List[Tuple["Document", bool]]:
        """
        Devuelve todos los documentos del usuario junto con un flag
        que indica si ya tiene al menos una conversación creada.

        Args:
            user_id: ID del usuario propietario

        Returns:
            List of (Document, has_conversation)
        """
        pass
        pass
    
    @abstractmethod
    async def update(self, document: Document) -> Document:
        """
        Actualiza un documento existente
        
        Args:
            document: Entidad Document con los datos actualizados
            
        Returns:
            Document: El documento actualizado
        """
        pass
