import re
import ollama
from typing import AsyncGenerator
from typing import List, Tuple
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
    
    @staticmethod
    def parse_citations(response: str) -> Tuple[str, List[int]]:
        """
        Extrae los IDs de chunks declarados por el LLM y devuelve el texto limpio.
        Busca el marcador @@FUENTES:[id1,id2,...]@@ en la respuesta.
        También limpia patrones residuales de páginas que el LLM pueda haber añadido
        (como '[Página 5, Página 12]' al final del texto).

        Returns:
            Tuple[str, List[int]]: (texto_limpio, lista_de_ids_usados)
            Si no hay marcador, devuelve el texto sin patrones residuales y lista vacía.
        """
        pattern = r'@@FUENTES:\[([^\]]*)\]@@'
        match = re.search(pattern, response)
        if match:
            ids_str = match.group(1)
            try:
                used_ids = [int(x.strip()) for x in ids_str.split(',') if x.strip()]
            except ValueError:
                used_ids = []
            clean = re.sub(pattern, '', response).strip()
        else:
            used_ids = []
            clean = response

        # Red de seguridad: eliminar patrones de resumen de páginas al final del texto
        # Ejemplos: '[Página 5]', '[Página 5, Página 12]', '[Páginas 5 y 12]'
        clean = re.sub(r'\[\s*[Pp][áa]gina[s]?[\s\d,yaAY-]+\]', '', clean)
        clean = clean.strip()

        return clean, used_ids

    async def generate_response(
        self, 
        prompt: str, 
        context_chunks: List[tuple[str, int, int]] = None
    ) -> str:
        """
        Genera una respuesta usando el modelo de Ollama
        
        Args:
            prompt: Pregunta del usuario
            context_chunks: Lista de tuplas (contenido, página, chunk_id) con contexto relevante
            
        Returns:
            str: Respuesta generada por el modelo (incluye marcador @@FUENTES:[]@@ al final)
        """
        system_prompt = """Eres un asistente experto en análisis de documentos PDF.
Tu trabajo es responder preguntas basándote ÚNICAMENTE en el contexto proporcionado del documento.

REGLAS IMPORTANTES:
1. Solo usa información del contexto proporcionado
2. Si la información no está en el contexto, di claramente que no puedes responder
3. Sé preciso y conciso en tus respuestas
4. NO agregues resúmenes de páginas al final de tu respuesta
5. NO menciones los IDs de los chunks en el texto de la respuesta. Escribe SOLO el texto de la respuesta.
6. Al TERMINAR tu respuesta, en la ÚLTIMA línea escribe EXACTAMENTE el marcador de fuentes con los IDs de los fragmentos que realmente usaste:
   @@FUENTES:[id1,id2,...]@@
   Ejemplo: @@FUENTES:[3,7]@@
   IMPORTANTE: escribe SOLO los IDs que realmente contienen información útil para tu respuesta. Nada más después de ese marcador."""
        
        if context_chunks and len(context_chunks) > 0:
            context_str = "\n\n".join([
                f"[ID:{chunk_id} | Página:{page}]\n{content}" 
                for content, page, chunk_id in context_chunks
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
    
    async def generate_response_stream(
        self, 
        prompt: str, 
        context_chunks: List[tuple[str, int, int]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Genera una respuesta en streaming usando Ollama (token por token)
        
        Args:
            prompt: Pregunta del usuario
            context_chunks: Lista de tuplas (contenido, página, chunk_id) con contexto relevante
            
        Yields:
            str: Fragmentos de texto conforme se generan (incluye marcador @@FUENTES:[]@@ al final)
        """
        system_prompt = """Eres un asistente experto en análisis de documentos PDF.
Tu trabajo es responder preguntas basándote ÚNICAMENTE en el contexto proporcionado del documento.

REGLAS IMPORTANTES:
1. Solo usa información del contexto proporcionado
2. Si la información no está en el contexto, di claramente que no puedes responder
3. Sé preciso y conciso en tus respuestas
4. NO agregues resúmenes de páginas al final de tu respuesta
5. NO menciones los IDs de los chunks en el texto de la respuesta. Escribe SOLO el texto de la respuesta.
6. Al TERMINAR tu respuesta, en la ÚLTIMA línea escribe EXACTAMENTE el marcador de fuentes con los IDs de los fragmentos que realmente usaste:
   @@FUENTES:[id1,id2,...]@@
   Ejemplo: @@FUENTES:[3,7]@@
   IMPORTANTE: escribe SOLO los IDs que realmente contienen información útil para tu respuesta. Nada más después de ese marcador."""
        
        if context_chunks and len(context_chunks) > 0:
            context_str = "\n\n".join([
                f"[ID:{chunk_id} | Página:{page}]\n{content}" 
                for content, page, chunk_id in context_chunks
            ])
            full_prompt = f"Contexto del documento:\n\n{context_str}\n\n---\n\nPregunta del usuario: {prompt}"
        else:
            full_prompt = f"No hay contexto disponible.\n\nPregunta: {prompt}"
        
        try:
            import asyncio
            import queue as sync_queue

            # Use a thread-safe queue to bridge sync Ollama stream → async generator
            q: asyncio.Queue = asyncio.Queue()
            loop = asyncio.get_event_loop()

            def _run_stream():
                try:
                    stream = self.client.chat(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": full_prompt},
                        ],
                        stream=True,
                    )
                    for chunk in stream:
                        token = chunk['message']['content']
                        if token:
                            loop.call_soon_threadsafe(q.put_nowait, token)
                except Exception as e:
                    loop.call_soon_threadsafe(q.put_nowait, Exception(str(e)))
                finally:
                    loop.call_soon_threadsafe(q.put_nowait, None)  # Sentinel

            # Run blocking Ollama call in a thread
            thread_task = asyncio.to_thread(_run_stream)
            asyncio.create_task(thread_task)

            # Yield tokens as they arrive
            while True:
                item = await q.get()
                if item is None:
                    break
                if isinstance(item, Exception):
                    raise item
                yield item

        except Exception as e:
            raise Exception(f"Error al generar respuesta streaming con Ollama: {str(e)}")

    
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
