# PDF Text Extraction Issue - Investigation & Fix

## Problem: Chat Returns Only Numbers

**Symptoms**:
- Chat responses say "no puedo determinar el contenido" or "serie de números sin relación"
- LLM receives numbers instead of actual text
- cited_pages show pages like [2, 4, 67] but no meaningful content

**Root Cause**:
Docling's extraction method may not work well with all PDF types. Some PDFs (especially scanned or image-based PDFs) require different processing.

---

## Investigation Steps

### 1. Check What's in Database

Run the debug script to see actual chunk content:

```powershell
$env:PYTHONPATH = "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"
conda activate documind
cd backend
python debug_chunks.py 1
```

This will show:
- First 10 chunks
- Content length
- First 200 characters of each chunk
- Warning if chunk contains only numbers

**Expected Output (GOOD)**:
```
Chunk #0 (Página 1)
Longitud contenido: 523 caracteres
Contenido: 
This is the actual text from the PDF...
```

**Bad Output (PROBLEM)**:
```
Chunk #0 (Página 1)
Longitud contenido: 50 caracteres
Contenido:
2 4 67 123 456...
⚠️  WARNING: Este chunk solo contiene números!
```

---

## Solution Applied

### Updated PDF Processor

**Changes**:
1. **pypdf as primary** - More reliable for standard text PDFs
2. **Docling as fallback** - For complex layouts (tables, multi-column)
3. **Better error handling** - Shows which method is being used
4. **Logging** - Shows character count per page

**New Processing Flow**:
```
1. Try pypdf first (fast, reliable for text)
   ↓ Success → Return extracted text
   ↓ Fail → Try Docling
2. Try Docling (advanced structure detection)
   ↓ Success → Return extracted text
   ↓ Fail → Error with both methods
```

**File Modified**: [pdf_processor.py](file:///c:/Users/joaco/OneDrive/Escritorio/Proyectos/DocuMind/backend/src/infrastructure/document_processing/pdf_processor.py)

---

## How to Fix Existing Documents

### Option 1: Reprocess Documents

Delete and re-upload documents to use the new processor:

```bash
# Delete document
curl -X DELETE "http://localhost:8000/api/documents/1"

# Upload again
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@your_document.pdf"
```

### Option 2: Manual Reprocess

Force reprocess existing document:

```bash
# First, mark as not processed in database
psql -d documind -c "UPDATE documents SET processed = false WHERE id = 1;"

# Delete old chunks
psql -d documind -c "DELETE FROM document_chunks WHERE document_id = 1;"

# Reprocess
curl -X POST "http://localhost:8000/api/documents/1/process"
```

---

## Testing the Fix

### 1. Check Debug Output

After reprocessing, run debug script again:

```powershell
python debug_chunks.py 1
```

Look for:
```
✅ pypdf: 10 páginas, 45231 caracteres totales
  Página 1: 4523 caracteres
  Página 2: 4112 caracteres
```

### 2. Test Chat

```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "message": "Resume el contenido de este documento"
  }'
```

**Good Response**:
```json
{
  "response": "Este documento trata sobre [real content]...",
  "cited_pages": [1, 2, 3]
}
```

**Bad Response** (still showing numbers):
```json
{
  "response": "Solo encuentro una serie de números...",
}
```

---

## If Still Not Working

### Possible Issues:

1. **Scanned PDF (Image-based)**
   - Solution: Needs OCR
   - Consider: pytesseract or pdf2image + OCR

2. **Encrypted PDF**
   - Solution: Decrypt first
   - Check: `reader.is_encrypted`

3. **Complex Layout**
   - Solution: Try pdfplumber
   - Better for: Tables, multi-column layouts

4. **Corrupted PDF**
   - Solution: Repair with ghostscript
   - Or: Ask user for different version

---

## Next Steps

1. Run `debug_chunks.py` to confirm problem
2. Restart server to use new PDF processor
3. Reprocess problematic documents
4. Test chat with fixed documents

**If pypdf still fails**, we can add additional extraction methods:
- pdfplumber (best for tables)
- pdfminer (low-level, very thorough)
- OCR (for scanned documents)
