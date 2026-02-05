"""
Script para inicializar la base de datos
Crea todas las tablas necesarias
"""
import asyncio
from src.infrastructure.database.connection import init_db, Base, engine

async def main():
    print("Iniciando creación de tablas...")
    
    # Importar todos los modelos para que SQLAlchemy los registre
    from src.infrastructure.database.models import (
        DocumentModel,
        DocumentChunkModel,
        ConversationModel,
        MessageModel
    )
    
    # Crear todas las tablas
    await init_db()
    
    print("✅ Tablas creadas exitosamente!")
    print("\nTablas creadas:")
    print("  - documents")
    print("  - document_chunks (con soporte de vector)")
    print("  - conversations")
    print("  - messages")

if __name__ == "__main__":
    asyncio.run(main())
