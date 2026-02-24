from typing import List
from src.infrastructure.ai.ollama_client import OllamaClient
from src.application.ports import EmbeddingServicePort
from src.domain.value_objects.embedding_vector import EmbeddingVector

class EmbeddingService(EmbeddingServicePort):
    """
    Servicio para generar embeddings usando Ollama
    """
    
    def __init__(self):
        self.ollama_client = OllamaClient()
    
    def generate_embeddings(self, texts: List[str]) -> List[EmbeddingVector]:
        """
        Genera embeddings para una lista de textos
        
        Args:
            texts: Lista de textos a embedear
            
        Returns:
            Lista de EmbeddingVector
        """
        embeddings = []
        
        for text in texts:
            if text.strip():  # Solo procesar textos no vacíos
                raw = self.ollama_client.generate_embedding(text)
                embeddings.append(EmbeddingVector.from_list(raw))
            else:
                # Para textos vacíos, usar un vector de ceros
                embeddings.append(EmbeddingVector.zeros(768))  # nomic-embed-text usa 768 dims
        
        return embeddings
    
    def generate_single_embedding(self, text: str) -> EmbeddingVector:
        """
        Genera embedding para un solo texto
        
        Args:
            text: Texto a embedear
            
        Returns:
            EmbeddingVector
        """
        if not text.strip():
            return EmbeddingVector.zeros(768)
        
        raw = self.ollama_client.generate_embedding(text)
        return EmbeddingVector.from_list(raw)
