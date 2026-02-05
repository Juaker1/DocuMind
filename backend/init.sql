-- Extensión pgvector para búsqueda de similitud vectorial
CREATE EXTENSION IF NOT EXISTS vector;

-- Índice para búsqueda vectorial en document_chunks
-- Este índice se creará automáticamente cuando las tablas sean creadas
-- y haya datos en la tabla de chunks