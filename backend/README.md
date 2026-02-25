# DocuMind — Backend API

API REST para el sistema de chat con documentos PDF usando RAG (Retrieval-Augmented Generation) con modelos de lenguaje locales a través de Ollama.

---

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Framework | FastAPI 0.128.0 |
| Base de datos | PostgreSQL + pgvector |
| ORM | SQLAlchemy 2.0.46 (async) |
| LLM | Ollama (configurable, default: qwen2.5:14b) |
| Embeddings | nomic-embed-text — 768 dimensiones |
| PDF Processing | Docling 2.72.0 + PyPDF (fallback) |
| Validación | Pydantic 2.12.5 |
| Autenticación | JWT (access + refresh tokens) via python-jose |
| Rate Limiting | slowapi 0.1.9 |
| Python | 3.12 (conda env `documind`) |

---

## Arquitectura

El backend sigue **Clean Architecture** en cuatro capas con dependencias que apuntan siempre hacia adentro:

```
api/ → application/ → domain/ ← infrastructure/
```

| Capa | Responsabilidad |
|------|----------------|
| `domain/` | Entidades, Value Objects, interfaces de repositorios, excepciones de dominio |
| `application/` | Use Cases, DTOs, interfaces de servicios externos (Ports) |
| `infrastructure/` | Implementaciones: PostgreSQL, Ollama, Docling |
| `api/` | Rutas FastAPI, middleware, dependency injection |

### Estructura de carpetas

```
backend/
├── src/
│   ├── domain/
│   │   ├── entities/           # User, Document, DocumentChunk, Conversation, Message
│   │   ├── repositories/       # Interfaces abstractas (Ports)
│   │   ├── value_objects/      # Email, EmbeddingVector, UserId, DocumentId, ConversationId
│   │   └── exceptions.py       # Excepciones de dominio
│   ├── application/
│   │   ├── dtos/               # Request/Response schemas (Pydantic)
│   │   ├── ports.py            # Interfaces de servicios externos
│   │   └── use_cases/          # Lógica de negocio
│   ├── infrastructure/
│   │   ├── ai/                 # OllamaClient, EmbeddingService
│   │   ├── database/
│   │   │   ├── models.py       # Modelos SQLAlchemy
│   │   │   ├── connection.py   # Engine + session factory
│   │   │   └── repositories/   # Implementaciones concretas
│   │   └── document_processing/ # PDFProcessor, TextChunker
│   ├── api/
│   │   ├── middleware/
│   │   │   └── security_headers.py
│   │   ├── routes/             # auth, documents, chat, health
│   │   ├── dependencies.py     # Composition Root (DI)
│   │   ├── limiter.py          # Instancia compartida slowapi
│   │   └── main.py
│   └── config/
│       └── settings.py         # Configuración centralizada (pydantic-settings)
├── uploads/                    # PDFs subidos por los usuarios
├── init_db.py                  # Crea todas las tablas desde cero
├── migrate_refresh_tokens.py   # Migración para DBs existentes
├── requirements.txt
├── .env
└── start_server.ps1
```

---

## Requisitos previos

- **conda** con el environment `documind` creado
- **PostgreSQL** corriendo con la extensión `pgvector` instalada
- **Ollama** corriendo localmente con los modelos descargados

### Modelos Ollama necesarios

```powershell
ollama pull qwen2.5:14b          # LLM para respuestas
ollama pull nomic-embed-text     # Embeddings (768 dims)
```

> Si querés usar otro LLM, cambia `OLLAMA_MODEL` en `.env`.

---

## Instalación

### 1. Crear el environment conda

```powershell
conda create -n documind python=3.12 -y
conda activate documind
```

### 2. Instalar dependencias

```powershell
cd backend
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia o edita el archivo `.env` en `backend/`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/documind

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Application
APP_NAME=DocuMind
DEBUG=True

# CORS — orígenes permitidos del frontend
ALLOWED_ORIGINS=["http://localhost:3000"]

# Auth
SECRET_KEY=cambia-esto-en-produccion-cadena-larga-aleatoria
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
```

> En producción: `DEBUG=False` oculta `/docs` y `/redoc`, activa HSTS y cambia el nivel de log a INFO.

### 4. Inicializar la base de datos

**Base de datos nueva:**

```powershell
$env:PYTHONPATH = "$PWD"
python init_db.py
```

Esto crea las tablas: `users`, `documents`, `document_chunks`, `conversations`, `messages`, `refresh_tokens`.

**Base de datos existente (migraciones):**

```powershell
# Agregar tabla refresh_tokens (JWT refresh)
conda run -n documind python backend/migrate_refresh_tokens.py
```

---

## Iniciar el servidor

```powershell
.\start_server.ps1
```

O manualmente:

```powershell
$env:PYTHONPATH = "c:\ruta\a\DocuMind\backend"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor queda disponible en `http://localhost:8000`.

Documentación interactiva (solo con `DEBUG=True`):
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Endpoints

### Auth — `/api/auth`

| Método | Ruta | Descripción | Auth requerida |
|--------|------|-------------|----------------|
| `POST` | `/register` | Registra usuario (convierte anónimo → registrado) | No |
| `POST` | `/login` | Login con email y contraseña | No |
| `POST` | `/refresh` | Renueva access token usando refresh token | No |
| `POST` | `/logout` | Revoca el refresh token del dispositivo | No |
| `GET` | `/me` | Info del usuario actual | Sí |
| `DELETE` | `/account` | Elimina cuenta y todos sus datos | Sí |

#### Autenticación de requests

Cada request debe incluir **uno** de los siguientes headers:

```
Authorization: Bearer <access_token>    # Usuario registrado
X-User-UUID: <uuid>                     # Usuario anónimo
```

#### Flujo de tokens

```
POST /login  →  { access_token, refresh_token, user }
                       │               │
                  expira en        expira en
                  60 minutos        7 días
                       │
            Cuando expira → POST /refresh con refresh_token
                         →  { access_token, refresh_token }  (rotation)
```

El frontend renueva el `access_token` automáticamente (interceptor en `api.ts`).

### Documentos — `/api/documents`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/upload` | Sube un PDF (procesamiento en background) |
| `GET` | `/` | Lista documentos del usuario |
| `GET` | `/{id}` | Detalle de un documento |
| `POST` | `/{id}/process` | Reprocesa un documento manualmente |
| `DELETE` | `/{id}` | Elimina documento y sus datos asociados |

Todos los endpoints verifican que el documento pertenezca al usuario autenticado.

### Chat — `/api/chat`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/` | Envía mensaje (respuesta completa) |
| `GET` | `/stream` | Envía mensaje con respuesta en streaming (SSE) |
| `GET` | `/documents/{id}/conversations` | Conversaciones de un documento |
| `DELETE` | `/conversations/{id}` | Reinicia conversación |

### Health

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado del servidor |

---

## Flujo RAG

```
1. Usuario sube PDF
        ↓
2. Docling extrae texto y estructura (con PyPDF como fallback)
        ↓
3. TextChunker divide en fragmentos (chunk_size=1500, overlap=300)
        ↓
4. OllamaClient genera embeddings con nomic-embed-text (768 dims)
        ↓
5. Chunks + embeddings guardados en PostgreSQL (columna vector pgvector)
        ↓
6. Usuario envía pregunta
        ↓
7. Pregunta convertida a embedding
        ↓
8. pgvector busca los N chunks más similares (cosine distance)
        ↓
9. Contexto + pregunta enviados a Ollama (qwen2.5:14b)
        ↓
10. LLM genera respuesta incluyendo @@FUENTES:[id1,id2]@@ al final
        ↓
11. Backend parsea fuentes, deduplica, devuelve respuesta limpia + cited_chunks
```

---

## Seguridad implementada

### Rate Limiting (slowapi)

| Endpoint | Límite |
|----------|--------|
| `POST /register` | 5 req/min por IP |
| `POST /login` | 10 req/min por IP |
| `POST /refresh` | 20 req/min por IP |
| `POST /documents/upload` | 5 req/min por IP |
| `GET /chat/stream` | 10 req/min por IP |
| `POST /chat/` | 20 req/min por IP |

### Validación de uploads

- Extensión: solo `.pdf`
- Content-Type: solo `application/pdf`
- Tamaño máximo: configurable via `MAX_FILE_SIZE` (default 10 MB)
- Magic number: verifica que los primeros 4 bytes sean `%PDF`

### Validación de mensajes

- Longitud máxima: 4000 caracteres
- Detección de patrones de prompt injection (logging de intentos)
- Mensaje del usuario enviado únicamente en `role: user`, nunca en el system prompt

### JWT

- Access tokens con claim `type: access` — no se pueden usar como refresh
- Refresh tokens almacenados como hash SHA-256 en BD — nunca el valor original
- Refresh token rotation: cada uso genera un nuevo par y revoca el anterior
- `POST /logout` revoca el token del dispositivo actual

### Security Headers

Todas las respuestas incluyen:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), ...
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
Strict-Transport-Security: max-age=31536000 (solo en producción)
```

### Ownership

Todos los endpoints de documentos y chat verifican que el recurso pertenezca al usuario autenticado. Un recurso ajeno devuelve `404` (no `403`) para no revelar su existencia.

### CORS

Orígenes permitidos configurados en `.env` via `ALLOWED_ORIGINS`. En producción, reemplazar con el dominio real del frontend.

---

## Base de datos

### Tablas

| Tabla | Descripción |
|-------|-------------|
| `users` | Usuarios anónimos y registrados |
| `documents` | Metadatos de PDFs subidos |
| `document_chunks` | Fragmentos de texto con embeddings vectoriales (768 dims) |
| `conversations` | Una conversación por documento por usuario |
| `messages` | Mensajes del chat con metadatos de citación |
| `refresh_tokens` | Hashes SHA-256 de refresh tokens activos/revocados |

### Relaciones

```
users ──< documents ──< document_chunks
               └──< conversations ──< messages
users ──< refresh_tokens
```

Todas las FK usan `ON DELETE CASCADE`.

---

## Ejemplos de uso (curl)

### Registrar usuario

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword", "uuid": "mi-uuid-anonimo"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword"}'
```

Respuesta:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": { "id": 1, "uuid": "...", "email": "user@example.com", "is_anonymous": false }
}
```

### Subir un PDF

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@mi_documento.pdf"
```

### Chatear con streaming

```bash
curl "http://localhost:8000/api/chat/stream?document_id=1&message=De+que+trata+este+documento" \
  -H "Authorization: Bearer <access_token>" \
  --no-buffer
```

### Renovar access token

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJ..."}'
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

```powershell
$env:PYTHONPATH = "c:\ruta\completa\a\DocuMind\backend"
```

### `Connection refused` a PostgreSQL

- Verificar que PostgreSQL esté corriendo
- Con Docker: `docker-compose up -d` desde la raíz del proyecto
- Verificar `DATABASE_URL` en `.env`

### `Ollama not available`

```powershell
ollama list        # Ver modelos instalados
ollama serve       # Iniciar Ollama si no está corriendo
```

### `asyncpg.exceptions.PostgresSyntaxError: cannot insert multiple commands`

`asyncpg` no admite múltiples sentencias SQL en un único `execute()`. Ejecutar las sentencias por separado.

### Los documentos no terminan de procesarse

Verificar que el `commit()` de la sesión se ejecute **antes** de agregar la tarea al `BackgroundTasks`. El procesamiento en background necesita que el documento ya esté en la BD al iniciarse.


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
