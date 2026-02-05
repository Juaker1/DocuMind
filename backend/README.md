# DocuMind Backend - API Completa ✅

Backend del proyecto DocuMind implementado con FastAPI, Python 3.12, Clean Architecture y RAG.

## 🚀 Quick Start

### 1. Instalar dependencias faltantes

```powershell
conda activate documind
cd backend
pip install pgvector
```

### 2. Configurar variables de entorno

El archivo `.env` ya está creado con la configuración por defecto. Si necesitas cambiar algo:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/documind
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### 3. Iniciar PostgreSQL

**Opción A: Docker** (cuando Docker Desktop esté disponible)
```powershell
cd ..  # Volver al directorio principal
docker-compose up -d
```

**Opción B: PostgreSQL Local**
- Asegúrate de tener PostgreSQL instalado con la extensión pgvector
- Crea la base de datos `documind`
- Actualiza `DATABASE_URL` en `.env` si es necesario

Ver [DATABASE_SETUP.md](file:///c:/Users/joaco/OneDrive/Escritorio/Proyectos/DocuMind/backend/DATABASE_SETUP.md) para más detalles.

### 4. Crear tablas

```powershell
$env:PYTHONPATH = "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"
python init_db.py
```

### 5. Iniciar el servidor

```powershell
.\start_server.ps1
```

O manualmente:
```powershell
$env:PYTHONPATH = "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Probar la API

Abre tu navegador en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📚 API Endpoints

### Health Check
- `GET /health` - Verifica que el servidor esté funcionando

### Documentos
- `POST /api/documents/upload` - Sube un PDF (procesamiento automático en background)
- `GET /api/documents/` - Lista todos los documentos
- `GET /api/documents/{id}` - Obtiene detalles de un documento
- `POST /api/documents/{id}/process` - Procesa manualmente un documento
- `DELETE /api/documents/{id}` - Elimina un documento

### Chat
- `POST /api/chat/` - Envía un mensaje para chatear con un documento
- `GET /api/chat/conversations/{id}` - Obtiene el historial de una conversación
- `GET /api/chat/documents/{id}/conversations` - Lista conversaciones de un documento
- `DELETE /api/chat/conversations/{id}` - Elimina una conversación

---

## 🏗️ Estructura del Proyecto

```
backend/
├── src/
│   ├── domain/              # Entidades y reglas de negocio
│   │   ├── entities/        # Document, Conversation, Message, DocumentChunk
│   │   └── repositories/    # Interfaces de repositorios
│   ├── application/         # Casos de uso
│   │   ├── dtos/           # DTOs para request/response
│   │   └── use_cases/      # UploadDocument, ProcessDocument, ChatWithDocument
│   ├── infrastructure/      # Implementaciones
│   │   ├── database/       # PostgreSQL + pgvector
│   │   ├── ai/             # Ollama client + embeddings
│   │   └── document_processing/  # Docling + chunker
│   ├── api/                # Rutas HTTP
│   │   ├── routes/         # documents.py, chat.py, health.py
│   │   └── dependencies.py # Dependency injection
│   ├── config/             # Settings
│   └── main.py             # FastAPI app
├── uploads/                # PDFs subidos
├── init_db.py             # Script para crear tablas
├── requirements.txt        # Dependencias
├── .env                   # Variables de entorno
└── start_server.ps1       # Script para iniciar servidor
```

---

## 🔄 Flujo RAG (Retrieval-Augmented Generation)

1. **Usuario sube PDF** → `POST /api/documents/upload`
2. **Docling extrae texto** y estructura del PDF
3. **Text chunker** divide en fragmentos con overlap
4. **Ollama genera embeddings** usando nomic-embed-text (768 dims)
5. **Chunks guardados en PostgreSQL** con vectores
6. **Usuario hace pregunta** → `POST /api/chat/`
7. **Pregunta se convierte en embedding**
8. **pgvector busca** los 5 chunks más similares
9. **Contexto + pregunta enviados a llama3.2**
10. **Respuesta generada con citas de páginas**

---

## 🛠️ Tecnologías Utilizadas

| Capa | Tecnología |
|------|------------|
| **Framework** | FastAPI 0.128.0 |
| **Base de datos** | PostgreSQL + pgvector |
| **ORM** | SQLAlchemy 2.0.46 (async) |
| **LLM** | Ollama (llama3.2) |
| **Embeddings** | nomic-embed-text (768 dims) |
| **PDF Processing** | Docling 2.72.0 |
| **Validation** | Pydantic 2.12.5 |

---

## 📊 Base de Datos

### Tablas creadas:

1. **documents** - Metadatos de PDFs
2. **document_chunks** - Fragmentos de texto con embeddings vectoriales
3. **conversations** - Conversaciones sobre documentos
4. **messages** - Mensajes del chat

### Relaciones:
- Document → Chunks (1:N, CASCADE)
- Document → Conversations (1:N, CASCADE)
- Conversation → Messages (1:N, CASCADE)

---

## 🧪 Ejemplos de Uso

### Subir un PDF

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@mi_documento.pdf"
```

Respuesta:
```json
{
  "id": 1,
  "filename": "mi_documento.pdf",
  "file_size": 1024000,
  "total_pages": 10,
  "upload_date": "2026-02-05T02:00:00",
  "processed": false
}
```

El documento se procesará automáticamente en background.

### Chatear con el documento

```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "message": "¿De qué trata este documento?"
  }'
```

Respuesta:
```json
{
  "conversation_id": 1,
  "message_id": 2,
  "response": "Según la página 3, este documento trata sobre...",
  "cited_pages": [3, 5, 7]
}
```

### Listar documentos

```bash
curl "http://localhost:8000/api/documents/"
```

---

## 🎯 Características Implementadas

✅ **Upload de PDFs con validación**
✅ **Procesamiento automático en background**
✅ **Extracción inteligente con Docling** (detecta títulos, tablas, etc.)
✅ **Chunking con overlap** para mejor contexto
✅ **Embeddings vectoriales** (nomic-embed-text)
✅ **Búsqueda de similitud** con pgvector
✅ **RAG completo** para chat contextual
✅ **Citación de páginas** en respuestas
✅ **Historial de conversaciones**
✅ **Clean Architecture**
✅ **Type-safe** con Pydantic
✅ **Async/await** para performance
✅ **CORS habilitado** para Next.js
✅ **Swagger UI** para testing

---

## 🔍 Troubleshooting

### Error: "No module named 'src'"
```powershell
$env:PYTHONPATH = "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"
```

### Error: "Connection refused" a la base de datos
- Verifica que PostgreSQL esté corriendo
- Si usas Docker: `docker-compose up -d`
- Verifica `DATABASE_URL` en `.env`

### Error: "Ollama not available"
```powershell
ollama list  # Verifica que Ollama esté corriendo
```

### Error: "No module named 'pgvector'"
```powershell
pip install pgvector
```

---

## 📖 Documentación Adicional

- [DATABASE_SETUP.md](file:///c:/Users/joaco/OneDrive/Escritorio/Proyectos/DocuMind/backend/DATABASE_SETUP.md) - Guía detallada de setup de base de datos
- Ver Swagger UI en http://localhost:8000/docs para documentación interactiva

---

## 🔜 Próximos Pasos

### Para el Frontend (Next.js)
1. Conectar con la API
2. Interfaz de subida de archivos
3. Chat UI con historial
4. Gestión de documentos

### Mejoras Futuras
- Sistema de usuarios y autenticación
- Chat con múltiples documentos simultáneamente
- Generación automática de títulos para conversaciones
- Preview de PDFs en la interfaz
- Soporte para más formatos (DOCX, TXT, etc.)
- Índices HNSW para búsqueda vectorial más rápida
- Caché de embeddings

---

## ✅ Estado del Proyecto

**Fase 1**: ✅ Estructura base y configuración
**Fase 2**: ✅ RAG completo con todas las funcionalidades
**Listo para**: 🚀 Integración con frontend Next.js

---

## 👨‍💻 Desarrollo

Para ejecutar en modo desarrollo con hot reload:

```powershell
$env:PYTHONPATH = "c:\Users\joaco\OneDrive\Escritorio\Proyectos\DocuMind\backend"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor se recargará automáticamente cuando detecte cambios en el código.
