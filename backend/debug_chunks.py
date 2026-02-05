"""
Script para debuggear los chunks de un documento
Muestra el contenido real guardado en la base de datos
"""
import asyncio
import sys
from sqlalchemy import select, text
from src.infrastructure.database.connection import AsyncSessionLocal
from src.infrastructure.database.models import DocumentChunkModel, DocumentModel

async def debug_document_chunks(document_id: int):
    """Ver los chunks de un documento"""
    async with AsyncSessionLocal() as session:
        # Obtener info del documento
        result = await session.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            print(f"❌ Documento {document_id} no encontrado")
            return
        
        print(f"\n📄 Documento: {doc.filename}")
        print(f"   Total páginas: {doc.total_pages}")
        print(f"   Procesado: {doc.processed}")
        print(f"   Ruta: {doc.file_path}")
        
        # Obtener chunks
        result = await session.execute(
            select(DocumentChunkModel)
            .where(DocumentChunkModel.document_id == document_id)
            .order_by(DocumentChunkModel.chunk_index)
            .limit(10)  # Solo primeros 10 chunks
        )
        chunks = result.scalars().all()
        
        if not chunks:
            print("\n❌ No hay chunks para este documento")
            return
        
        print(f"\n📝 Total chunks: ")
        result = await session.execute(
            text("SELECT COUNT(*) FROM document_chunks WHERE document_id = :doc_id"),
            {"doc_id": document_id}
        )
        total = result.scalar()
        print(f"   {total} chunks en total")
        
        print(f"\n🔍 Primeros 10 chunks:")
        print("=" * 80)
        
        for chunk in chunks:
            print(f"\nChunk #{chunk.chunk_index} (Página {chunk.page_number})")
            print(f"ID: {chunk.id}")
            print(f"Longitud contenido: {len(chunk.content)} caracteres")
            print(f"Tiene embedding: {chunk.embedding is not None}")
            print(f"\nContenido (primeros 200 chars):")
            print("-" * 80)
            print(chunk.content[:200])
            print("-" * 80)
            
            # Análisis del contenido
            if chunk.content.strip().replace(' ', '').replace('\n', '').isdigit():
                print("⚠️  WARNING: Este chunk solo contiene números!")
            
            # Mostrar primeras palabras
            words = chunk.content.split()[:20]
            print(f"\nPrimeras 20 palabras: {' '.join(words)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python debug_chunks.py <document_id>")
        print("Ejemplo: python debug_chunks.py 1")
        sys.exit(1)
    
    doc_id = int(sys.argv[1])
    asyncio.run(debug_document_chunks(doc_id))
