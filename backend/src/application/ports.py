"""
Puertos de servicios externos para la capa de aplicación.

Define QUÉ necesitan los Use Cases de los servicios externos
(procesamiento de PDF, chunking, embeddings) sin depender de
ninguna implementación concreta de infraestructura.

Las implementaciones concretas viven en infrastructure/ e implementan
estas interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class PDFProcessorPort(ABC):
    """Puerto para extracción de texto desde PDFs."""

    @abstractmethod
    def process_pdf(
        self, pdf_path: str
    ) -> Tuple[str, int, List[Tuple[str, int]]]:
        """
        Procesa un PDF y extrae su contenido.

        Returns:
            Tuple con:
                - full_text: Texto completo
                - total_pages: Número de páginas
                - pages_content: Lista de (contenido, número_de_página)
        """
        ...


class TextChunkerPort(ABC):
    """Puerto para dividir texto en chunks."""

    @abstractmethod
    def chunk_pages(
        self, pages_content: List[Tuple[str, int]]
    ) -> List[Tuple[str, int, int]]:
        """
        Divide el contenido de páginas en chunks.

        Returns:
            Lista de (chunk_text, page_number, chunk_index)
        """
        ...


class EmbeddingServicePort(ABC):
    """Puerto para generar embeddings de texto."""

    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos."""
        ...

    @abstractmethod
    def generate_single_embedding(self, text: str) -> List[float]:
        """Genera embedding para un único texto."""
        ...


class LLMClientPort(ABC):
    """Puerto para el cliente de modelo de lenguaje (LLM)."""

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context_chunks: List[Tuple[str, int, int]],
    ) -> str:
        """
        Genera una respuesta completa (no streaming).

        Args:
            prompt: Pregunta del usuario
            context_chunks: Lista de (contenido, página, chunk_id)

        Returns:
            Respuesta completa del modelo
        """
        ...

    @abstractmethod
    async def generate_response_stream(
        self,
        prompt: str,
        context_chunks: List[Tuple[str, int, int]],
    ):
        """
        Genera una respuesta en streaming (token a token).

        Args:
            prompt: Pregunta del usuario
            context_chunks: Lista de (contenido, página, chunk_id)

        Yields:
            Fragmentos de texto conforme se generan
        """
        ...
