from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class Document:
    """
    Entidad del dominio que representa un documento PDF
    
    Attributes:
        id: Identificador único del documento
        filename: Nombre del archivo original
        file_path: Ruta donde se guardó el archivo
        file_size: Tamaño del archivo en bytes
        total_pages: Número total de páginas del PDF
        upload_date: Fecha y hora de carga
        processed: Indica si el documento ya fue procesado
        user_id: ID del usuario que subió el documento (opcional)
    """
    filename: str
    file_path: str
    file_size: int
    total_pages: int
    id: Optional[int] = None
    upload_date: datetime = field(default_factory=datetime.now)
    processed: bool = False
    user_id: Optional[int] = None
    
    def mark_as_processed(self) -> None:
        """Marca el documento como procesado"""
        self.processed = True
    
    def is_valid_size(self, max_size: int) -> bool:
        """
        Verifica si el tamaño del documento es válido
        
        Args:
            max_size: Tamaño máximo permitido en bytes
            
        Returns:
            bool: True si el tamaño es válido
        """
        return self.file_size <= max_size
