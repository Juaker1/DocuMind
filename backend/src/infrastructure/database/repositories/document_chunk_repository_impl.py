from typing import List
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
from src.domain.entities.document_chunk import DocumentChunk
from src.domain.repositories.document_chunk_repository import DocumentChunkRepository
from src.domain.value_objects.embedding_vector import EmbeddingVector
from src.infrastructure.database.models import DocumentChunkModel

class DocumentChunkRepositoryImpl(DocumentChunkRepository):
    """Implementación del repositorio de chunks usando SQLAlchemy + pgvector"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Guarda múltiples chunks de un documento"""
        db_chunks = []
        
        for chunk in chunks:
            db_chunk = DocumentChunkModel(
                document_id=chunk.document_id,
                content=chunk.content,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                embedding=chunk.embedding.to_list() if chunk.embedding else None
            )
            db_chunks.append(db_chunk)
            self.session.add(db_chunk)
        
        await self.session.flush()
        
        # Refrescar para obtener IDs
        for db_chunk in db_chunks:
            await self.session.refresh(db_chunk)
        
        return [self._to_entity(chunk) for chunk in db_chunks]
    
    async def find_by_document_id(self, document_id: int) -> List[DocumentChunk]:
        """Obtiene todos los chunks de un documento"""
        result = await self.session.execute(
            select(DocumentChunkModel)
            .where(DocumentChunkModel.document_id == document_id)
            .order_by(DocumentChunkModel.chunk_index)
        )
        db_chunks = result.scalars().all()
        
        return [self._to_entity(chunk) for chunk in db_chunks]

    async def find_by_ids(self, ids: List[int]) -> List[DocumentChunk]:
        """Obtiene chunks por sus IDs para resolver citas del historial"""
        if not ids:
            return []
        result = await self.session.execute(
            select(DocumentChunkModel).where(DocumentChunkModel.id.in_(ids))
        )
        db_chunks = result.scalars().all()
        return [self._to_entity(chunk) for chunk in db_chunks]

    async def search_similar(
        self,
        embedding: EmbeddingVector,
        document_id: int,
        limit: int = 5
    ) -> List[DocumentChunk]:
        """
        Busca los chunks más similares usando búsqueda vectorial con pgvector
        Utiliza el operador <=> para calcular distancia L2
        """
        # Serializar EmbeddingVector al formato que espera pgvector
        embedding_str = embedding.to_db_string()
        
        # Query usando pgvector para búsqueda de similaridad
        # IMPORTANTE: usar bindparam con literal_column para evitar conflictos de placeholders
        query = text("""
            SELECT id, document_id, content, page_number, chunk_index, embedding
            FROM document_chunks
            WHERE document_id = :document_id
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)
        
        result = await self.session.execute(
            query,
            {
                "document_id": document_id,
                "embedding": embedding_str,
                "limit": limit
            }
        )
        
        rows = result.fetchall()
        chunks = []
        
        for row in rows:
            # Convertir embedding a lista si existe
            # PostgreSQL con text() devuelve el vector como string: "[1.0,2.0,3.0,...]"
            embedding_value = None
            if row[5] is not None:
                try:
                    # Si row[5] es un string (común con text() queries), parsearlo
                    if isinstance(row[5], str):
                        # Parsear string JSON a lista
                        embedding_value = json.loads(row[5])
                    else:
                        # Si es un objeto pgvector, convertir directamente
                        embedding_value = [float(x) for x in row[5]]
                except (ValueError, TypeError, json.JSONDecodeError) as e:
                    print(f"⚠️ Error al parsear embedding: {e}")
                    embedding_value = None
            
            chunk = DocumentChunk(
                id=row[0],
                document_id=row[1],
                content=row[2],
                page_number=row[3],
                chunk_index=row[4],
                embedding=EmbeddingVector.from_list(embedding_value) if embedding_value else None
            )
            chunks.append(chunk)
        
        return chunks
    
    async def delete_by_document_id(self, document_id: int) -> bool:
        """Elimina todos los chunks de un documento"""
        result = await self.session.execute(
            delete(DocumentChunkModel).where(
                DocumentChunkModel.document_id == document_id
            )
        )
        await self.session.flush()
        
        return result.rowcount > 0
    
    def _to_entity(self, db_chunk: DocumentChunkModel) -> DocumentChunk:
        """Convierte un modelo de base de datos a entidad de dominio"""
        # Convertir embedding a lista si existe
        embedding_value = None
        if db_chunk.embedding is not None:
            try:
                if isinstance(db_chunk.embedding, str):
                    # Si es string, parsear JSON
                    embedding_value = json.loads(db_chunk.embedding)
                else:
                    # Si es objeto pgvector, convertir
                    embedding_value = [float(x) for x in db_chunk.embedding]
            except (ValueError, TypeError, json.JSONDecodeError):
                embedding_value = None
        
        return DocumentChunk(
            id=db_chunk.id,
            document_id=db_chunk.document_id,
            content=db_chunk.content,
            page_number=db_chunk.page_number,
            chunk_index=db_chunk.chunk_index,
            embedding=EmbeddingVector.from_list(embedding_value) if embedding_value else None
        )
