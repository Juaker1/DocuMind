"""
Migración: agrega la tabla refresh_tokens para el sistema de JWT refresh.
Ejecutar UNA sola vez en bases de datos ya existentes.

  conda run -n documind python backend/migrate_refresh_tokens.py
"""
import asyncio
from sqlalchemy import text
from src.infrastructure.database.connection import engine

# asyncpg no admite múltiples sentencias en un solo execute() — una por llamada
_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id         SERIAL PRIMARY KEY,
        user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_hash VARCHAR(64) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        revoked    BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS ix_refresh_tokens_user_id    ON refresh_tokens(user_id)",
    "CREATE INDEX IF NOT EXISTS ix_refresh_tokens_token_hash ON refresh_tokens(token_hash)",
]


async def main():
    async with engine.begin() as conn:
        for stmt in _STATEMENTS:
            await conn.execute(text(stmt))
    print("✅ Tabla refresh_tokens creada (o ya existía).")


if __name__ == "__main__":
    asyncio.run(main())

