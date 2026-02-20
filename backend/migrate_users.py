"""
migrate_users.py
Run this script ONCE to add the `users` table and update the `documents` FK.
Usage:  python migrate_users.py
"""

import asyncio
from sqlalchemy import text
from src.infrastructure.database.connection import AsyncSessionLocal, engine, Base

# Import models so Base.metadata knows about them
from src.infrastructure.database.models import UserModel, DocumentModel  # noqa


CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    uuid          VARCHAR(36) UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    is_anonymous  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_users_uuid  ON users (uuid);
CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
"""

# Add FK constraint to documents.user_id if it doesn't exist yet
ADD_FK = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'documents_user_id_fkey'
          AND table_name = 'documents'
    ) THEN
        -- Drop the old plain integer column constraint (no FK) if present
        ALTER TABLE documents
            ADD CONSTRAINT documents_user_id_fkey
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
    END IF;
END;
$$;
"""

CREATE_USER_ID_INDEX = """
CREATE INDEX IF NOT EXISTS ix_documents_user_id ON documents (user_id);
"""


async def run():
    async with engine.begin() as conn:
        print("Creating users table...")
        await conn.execute(text(CREATE_USERS_TABLE))

        print("Adding FK constraint on documents.user_id...")
        await conn.execute(text(ADD_FK))

        print("Creating index on documents.user_id...")
        await conn.execute(text(CREATE_USER_ID_INDEX))

    print("✅ Migration complete.")


if __name__ == "__main__":
    asyncio.run(run())
