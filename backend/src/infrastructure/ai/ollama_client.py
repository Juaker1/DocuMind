import ollama
from typing import List
from src.config.settings import get_settings

settings = get_settings()

class OllamaClient:
    """
    Cliente para interactuar con Ollama
    Maneja la generación de respuestas y embeddings
    """
    
    def __init__(self):
        """Inicializa el cliente de Ollama"""
        self.client = ollama.Client(host=settings.ollama_host)
        self.model = settings.ollama_model
        self.embedding_model = settings.ollama_embedding_model
    
    async def generate_response(
        self, 
        prompt: str, 
        context_chunks: List[tuple[str, int]] = None
    ) -> str:
        """
        Genera una respuesta usando el modelo de Ollama
        
        Args:
            prompt: Pregunta del usuario
            context_chunks: Lista de tuplas (contenido, página) con contexto relevante
            
        Returns:
            str: Respuesta generada por el modelo
        """
        system_prompt = """Eres un asistente experto en análisis de documentos PDF.
Tu trabajo es responder preguntas basándote ÚNICAMENTE en el contexto proporcionado del documento.

REGLAS IMPORTANTES:
1. Solo usa información del contexto proporcionado
2. SIEMPRE cita la página de donde obtuviste la información usando el formato: [Página X]
3. Si la información no está en el contexto, di claramente que no puedes responder
4. Sé preciso y conciso en tus respuestas
5. Si citas múltiples páginas, menciona todas"""
        
        if context_chunks and len(context_chunks) > 0:
            context_str = "\n\n".join([
                f"[Página {page}]\n{content}" 
                for content, page in context_chunks
            ])
            full_prompt = f"Contexto del documento:\n\n{context_str}\n\n---\n\nPregunta del usuario: {prompt}"
        else:
            full_prompt = f"No hay contexto disponible.\n\nPregunta: {prompt}"
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            return response['message']['content']
        except Exception as e:
            raise Exception(f"Error al generar respuesta con Ollama: {str(e)}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para un texto usando nomic-embed-text
        
        Args:
            text: Texto a embedear
            
        Returns:
            List[float]: Vector de embedding (768 dimensiones)
        """
        try:
            response = self.client.embeddings(
                model=self.embedding_model,
                prompt=text
            )
            
            return response['embedding']
        except Exception as e:
            raise Exception(f"Error al generar embedding: {str(e)}")
    
    def is_available(self) -> bool:
        """
        Verifica si Ollama está disponible y funcionando
        
        Returns:
            bool: True si está disponible
        """
        try:
            # Intenta listar los modelos para verificar conexión
            self.client.list()
            return True
        except Exception:
            return False
