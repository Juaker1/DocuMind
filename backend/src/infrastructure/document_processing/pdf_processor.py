from typing import List, Tuple
from docling.document_converter import DocumentConverter
from pypdf import PdfReader
import os
from src.config.settings import get_settings

settings = get_settings()

class PDFProcessor:
    """
    Procesador de documentos PDF usando Docling como primario y pypdf como fallback
    Extrae texto, detecta estructura (títulos, tablas, etc.)
    """
    
    def __init__(self):
        self.converter = DocumentConverter()
    
    def process_pdf(self, pdf_path: str) -> Tuple[str, int, List[Tuple[str, int]]]:
        """
        Procesa un PDF y extrae su contenido
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Tuple con:
                - full_text: Texto completo del documento
                - total_pages: Número total de páginas
                - pages_content: Lista de tuplas (contenido, número_de_página)
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")
        
        # Primero intentar con pypdf (más confiable para texto simple)
        try:
            print("📖 Intentando extracción con pypdf...")
            return self._process_with_pypdf(pdf_path)
        except Exception as e:
            print(f"⚠️  pypdf falló: {str(e)}, intentando con Docling...")
            
            # Fallback a Docling
            try:
                return self._process_with_docling(pdf_path)
            except Exception as e2:
                raise Exception(f"Error al procesar PDF con ambos métodos. pypdf: {str(e)}, Docling: {str(e2)}")
    
    def _process_with_pypdf(self, pdf_path: str) -> Tuple[str, int, List[Tuple[str, int]]]:
        """Procesa PDF usando pypdf (simple y confiable)"""
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        pages_content = []
        full_text_parts = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            
            # Limpiar texto
            text = text.strip()
            
            if text:  # Solo agregar páginas con contenido
                pages_content.append((text, page_num))
                full_text_parts.append(text)
                print(f"  Página {page_num}: {len(text)} caracteres")
        
        full_text = "\n\n".join(full_text_parts)
        
        print(f"✅ pypdf: {total_pages} páginas, {len(full_text)} caracteres totales")
        
        return full_text, total_pages, pages_content
    
    def _process_with_docling(self, pdf_path: str) -> Tuple[str, int, List[Tuple[str, int]]]:
        """Procesa PDF usando Docling (detecta estructura avanzada)"""
        result = self.converter.convert(pdf_path)
        
        # Extraer texto completo
        full_text = result.document.export_to_markdown()
        
        pages_content = []
        
        # Iterar sobre las páginas del documento
        if hasattr(result.document, 'pages'):
            for page_num, page in enumerate(result.document.pages, start=1):
                # Exportar el contenido de cada página
                page_text = page.export_to_markdown() if hasattr(page, 'export_to_markdown') else str(page)
                if page_text.strip():
                    pages_content.append((page_text, page_num))
        else:
            # Si no hay separación por páginas, usar el texto completo
            pages_content.append((full_text, 1))
        
        total_pages = len(pages_content) if pages_content else 1
        
        print(f"✅ Docling: {total_pages} páginas")
        
        return full_text, total_pages, pages_content
    
    def extract_metadata(self, pdf_path: str) -> dict:
        """
        Extrae metadatos del PDF
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            dict: Diccionario con metadatos
        """
        try:
            reader = PdfReader(pdf_path)
            metadata = reader.metadata
            
            return {
                "title": metadata.get('/Title', None) if metadata else None,
                "author": metadata.get('/Author', None) if metadata else None,
                "creation_date": metadata.get('/CreationDate', None) if metadata else None,
                "page_count": len(reader.pages)
            }
        except Exception:
            # Fallback a Docling para metadatos
            result = self.converter.convert(pdf_path)
            return {
                "title": getattr(result.document, 'title', None),
                "author": getattr(result.document, 'author', None),
                "creation_date": getattr(result.document, 'creation_date', None),
            }

