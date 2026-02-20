"""
migrate_users_sync.py  —  simple synchronous psycopg2 migration
Run: conda run -n documind python migrate_users_sync.py
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Convert asyncpg URL to psycopg2-compatible
raw_url = os.environ.get("DATABASE_URL", "")
# postgresql+asyncpg://user:password@localhost:5432/documind
#   ->  host=localhost dbname=documind user=user password=password port=5432
raw_url = raw_url.replace("postgresql+asyncpg://", "")
userinfo, hostinfo = raw_url.split("@")
username, password = userinfo.split(":")
hostport, dbname = hostinfo.split("/")
if ":" in hostport:
    host, port = hostport.split(":")
else:
    host, port = hostport, "5432"

conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=username, password=password)
conn.autocommit = True
cur = conn.cursor()

print("Creating users table...")
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    uuid          VARCHAR(36) UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    is_anonymous  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);
""")

print("Creating indexes on users...")
cur.execute("CREATE INDEX IF NOT EXISTS ix_users_uuid  ON users (uuid);")
cur.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);")

print("Adding FK from documents.user_id to users.id (if not exists)...")
cur.execute("""
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'documents_user_id_fkey'
          AND table_name = 'documents'
    ) THEN
        ALTER TABLE documents
            ADD CONSTRAINT documents_user_id_fkey
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
    END IF;
END;
$$;
""")

print("Creating index on documents.user_id...")
cur.execute("CREATE INDEX IF NOT EXISTS ix_documents_user_id ON documents (user_id);")

cur.close()
conn.close()
print("✅ Migration complete.")
