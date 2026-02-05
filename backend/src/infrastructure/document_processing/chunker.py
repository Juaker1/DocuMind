from typing import List, Tuple
from src.config.settings import get_settings

settings = get_settings()

class TextChunker:
    """
    Divide texto en chunks con overlap para embeddings
    """
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def chunk_text(
        self, 
        text: str, 
        page_number: int
    ) -> List[Tuple[str, int]]:
        """
        Divide el texto en chunks con overlap
        
        Args:
            text: Texto a dividir
            page_number: Número de página de origen
            
        Returns:
            Lista de tuplas (chunk_text, page_number)
        """
        if not text or len(text.strip()) == 0:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Determinar el final del chunk
            end = start + self.chunk_size
            
            # Si no es el último chunk, intentar cortar en un espacio o punto
            if end < text_length:
                # Buscar el último espacio o punto antes del límite
                chunk_text = text[start:end]
                
                # Buscar último espacio, punto o salto de línea
                last_break = max(
                    chunk_text.rfind(' '),
                    chunk_text.rfind('.'),
                    chunk_text.rfind('\n')
                )
                
                if last_break > self.chunk_overlap:
                    end = start + last_break + 1
            else:
                end = text_length
            
            chunk = text[start:end].strip()
            
            if chunk:  # Solo agregar chunks no vacíos
                chunks.append((chunk, page_number))
            
            # Mover el inicio con overlap
            start = end - self.chunk_overlap
            
            # Evitar loops infinitos
            if start >= text_length or (end >= text_length and start < end):
                break
        
        return chunks
    
    def chunk_pages(
        self, 
        pages_content: List[Tuple[str, int]]
    ) -> List[Tuple[str, int, int]]:
        """
        Divide múltiples páginas en chunks
        
        Args:
            pages_content: Lista de tuplas (contenido, número_de_página)
            
        Returns:
            Lista de tuplas (chunk_text, page_number, chunk_index)
        """
        all_chunks = []
        chunk_index = 0
        
        for page_text, page_number in pages_content:
            page_chunks = self.chunk_text(page_text, page_number)
            
            for chunk_text, page_num in page_chunks:
                all_chunks.append((chunk_text, page_num, chunk_index))
                chunk_index += 1
        
        return all_chunks
