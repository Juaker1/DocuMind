# Additional Bug Fix - Vector Parsing

## Issue: "could not convert string to float: '['"

**Error Details**:
```json
{
  "detail": "Error en búsqueda vectorial: could not convert string to float: '['"
}
```

**Root Cause**:
- When using `text()` for raw SQL queries in SQLAlchemy with asyncpg, PostgreSQL returns vector columns as **strings**
- The string format is: `"[1.0,2.0,3.0,...]"` (JSON-like)
- The code was trying to do: `[float(x) for x in row[5]]`
- This iterates over **characters** of the string: `['[', ',', '1', '.', '0', ...]` instead of values
- Result: `float('[')` → error

**The Fix**:
```python
# BEFORE (❌ Iterates over characters)
embedding_value = [float(x) for x in row[5]]

# AFTER (✅ Properly parses JSON string)
if isinstance(row[5], str):
    embedding_value = json.loads(row[5])  # Parse JSON string
else:
    embedding_value = [float(x) for x in row[5]]  # pgvector object
```

**Why This Happens**:
- `text()` queries bypass SQLAlchemy's type system
- PostgreSQL returns custom types (like `vector`) as their text representation
- For `vector` type, the text representation is a JSON array string
- We need to parse it back to a Python list

**Files Modified**:
- [document_chunk_repository_impl.py](file:///c:/Users/joaco/OneDrive/Escritorio/Proyectos/DocuMind/backend/src/infrastructure/database/repositories/document_chunk_repository_impl.py)
  - Added `import json`
  - Fixed `search_similar()` method to parse string vectors
  - Fixed `_to_entity()` method to handle both string and object types

**Error Handling**:
Now includes try-catch for parsing errors with warning logs:
```python
try:
    if isinstance(row[5], str):
        embedding_value = json.loads(row[5])
    else:
        embedding_value = [float(x) for x in row[5]]
except (ValueError, TypeError, json.JSONDecodeError) as e:
    print(f"⚠️ Error al parsear embedding: {e}")
    embedding_value = None
```

This should now work correctly! 🎯
