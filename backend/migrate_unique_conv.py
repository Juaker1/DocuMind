"""
Migration: Add UNIQUE constraint on conversations.document_id
Run once: python migrate_unique_conv.py
"""
import asyncio
from sqlalchemy import text
from src.infrastructure.database.connection import engine


async def run():
    async with engine.begin() as conn:
        # Check if constraint already exists
        result = await conn.execute(text("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'conversations'
              AND constraint_name = 'uq_conversations_document_id'
        """))
        exists = result.fetchone()

        if exists:
            print("✅ Constraint already exists — nothing to do.")
        else:
            # Remove any duplicate conversations first (keep the one with the highest id per document)
            await conn.execute(text("""
                DELETE FROM conversations
                WHERE id NOT IN (
                    SELECT MAX(id) FROM conversations GROUP BY document_id
                )
            """))
            print("🧹 Removed duplicate conversations (kept newest per document)")

            await conn.execute(text("""
                ALTER TABLE conversations
                ADD CONSTRAINT uq_conversations_document_id UNIQUE (document_id)
            """))
            print("✅ Unique constraint added successfully")


asyncio.run(run())
