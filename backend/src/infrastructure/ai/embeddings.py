from typing import List
from src.infrastructure.ai.ollama_client import OllamaClient
from src.application.ports import EmbeddingServicePort

class EmbeddingService(EmbeddingServicePort):
    """
    Servicio para generar embeddings usando Ollama
    """
    
    def __init__(self):
        self.ollama_client = OllamaClient()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de textos
        
        Args:
            texts: Lista de textos a embedear
            
        Returns:
            Lista de vectores de embedding
        """
        embeddings = []
        
        for text in texts:
            if text.strip():  # Solo procesar textos no vacíos
                embedding = self.ollama_client.generate_embedding(text)
                embeddings.append(embedding)
            else:
                # Para textos vacíos, usar un vector de ceros
                embeddings.append([0.0] * 768)  # nomic-embed-text usa 768 dims
        
        return embeddings
    
    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para un solo texto
        
        Args:
            text: Texto a embedear
            
        Returns:
            Vector de embedding
        """
        if not text.strip():
            return [0.0] * 768
        
        return self.ollama_client.generate_embedding(text)
