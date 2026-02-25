# DocuMind

Sistema de chat con documentos PDF impulsado por IA local. Sube un PDF, hazle preguntas y obtén respuestas en tiempo real con citas de las páginas exactas del documento — sin enviar tus datos a ningún servicio externo.

> Stack: **FastAPI** · **Next.js 16** · **PostgreSQL + pgvector** · **Ollama**

---

## Características principales

- **Chat RAG en tiempo real** — streaming token a token via Server-Sent Events (SSE)
- **IA 100% local** — LLM y embeddings corren en Ollama, sin APIs de terceros
- **Citas verificables** — el asistente indica las páginas exactas y muestra los fragmentos del documento de donde proviene cada respuesta
- **Autenticación completa** — JWT con access token (60 min) + refresh token (7 días), rotación automática y revocación en logout
- **Modo anónimo** — los usuarios pueden subir documentos y chatear sin registrarse
- **Procesado de PDFs** — extracción de texto con Docling (PyPDF como fallback), chunking y almacenamiento de embeddings vectoriales
- **Arquitectura limpia** — backend en Clean Architecture (4 capas), frontend en arquitectura por funcionalidades

---

## Tecnologías

### Backend
| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.12 | Lenguaje base |
| FastAPI | 0.128.0 | Framework web async |
| SQLAlchemy | 2.0.46 | ORM async |
| PostgreSQL + pgvector | 16 | Base de datos + búsqueda vectorial |
| Ollama | — | Servidor LLM local |
| qwen2.5:14b | — | Modelo de lenguaje (configurable) |
| nomic-embed-text | — | Modelo de embeddings (768 dims) |
| Docling | 2.72.0 | Extracción de texto de PDFs |
| python-jose | — | JWT access + refresh tokens |
| slowapi | 0.1.9 | Rate limiting |

### Frontend
| Tecnología | Versión | Propósito |
|---|---|---|
| Next.js | 16.1.6 | Framework React — App Router |
| React | 19.2.3 | Biblioteca de UI |
| TypeScript | 5 | Tipado estático |
| Tailwind CSS | 4 | Estilos utilitarios |
| Axios | 1.13.4 | Cliente HTTP con interceptor JWT |
| EventSource / SSE | — | Streaming en tiempo real |

---

## Arquitectura

```
DocuMind/
├── backend/        # API REST — Clean Architecture
│   └── src/
│       ├── domain/         # Entidades, Value Objects, interfaces
│       ├── application/    # Use Cases, DTOs, Ports
│       ├── infrastructure/ # PostgreSQL, Ollama, Docling
│       └── api/            # Rutas FastAPI, middleware, DI
│
├── frontend/       # SPA — Next.js App Router
│   └── src/
│       ├── app/            # Páginas (Home, Chat)
│       ├── features/       # auth, chat, documents
│       ├── components/     # UI primitivos, layout
│       └── services/       # Axios + SSEClient
│
└── docker-compose.yml  # PostgreSQL + pgvector
```

### Flujo RAG

```
Usuario → mensaje
    → Backend busca los N chunks más similares (pgvector cosine similarity)
    → Construye prompt con contexto
    → Ollama genera respuesta en streaming
    → SSE envía tokens al frontend en tiempo real
    → Al finalizar: extrae citas (@@FUENTES:[]@@) y las guarda junto al mensaje
```

---

## Requisitos previos

| Herramienta | Versión mínima | Instalación |
|---|---|---|
| Docker + Docker Compose | 24+ | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Ollama | — | [ollama.com](https://ollama.com/) |
| conda | — | [docs.conda.io](https://docs.conda.io/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| pnpm | — | `npm install -g pnpm` |

---

## Inicio rápido

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd DocuMind
```

### 2. Levantar la base de datos

```bash
docker compose up -d
```

Esto inicia PostgreSQL 16 con la extensión `pgvector` en `localhost:5432`.

### 3. Descargar los modelos de Ollama

```bash
ollama pull qwen2.5:14b        # LLM para respuestas
ollama pull nomic-embed-text   # Embeddings (768 dims)
```

> Asegúrate de que Ollama esté corriendo (`ollama serve`).

### 4. Configurar el backend

```bash
cd backend
```

Crea el archivo `.env` (o edita el existente):

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/documind
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
SECRET_KEY=cambia-esto-por-una-cadena-larga-y-aleatoria
ALLOWED_ORIGINS=["http://localhost:3000"]
DEBUG=True
```

Crea el environment e instala dependencias:

```bash
conda create -n documind python=3.12 -y
conda activate documind
pip install -r requirements.txt
```

Inicializa las tablas de la base de datos:

```bash
$env:PYTHONPATH = "$PWD/.."   # PowerShell
# export PYTHONPATH="$(pwd)/.."  # bash
python init_db.py
```

Inicia el servidor:

```bash
# PowerShell
.\start_server.ps1

# O directamente
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API disponible en [http://localhost:8000](http://localhost:8000) · Docs en [http://localhost:8000/docs](http://localhost:8000/docs).

### 5. Configurar el frontend

```bash
cd ../frontend
```

Crea el archivo `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=DocuMind
```

Instala dependencias e inicia:

```bash
pnpm install
pnpm dev
```

Aplicación disponible en [http://localhost:3000](http://localhost:3000).

---

## Variables de entorno

### Backend (`backend/.env`)

| Variable | Default | Descripción |
|---|---|---|
| `DATABASE_URL` | — | Conexión a PostgreSQL |
| `OLLAMA_HOST` | `http://localhost:11434` | URL del servidor Ollama |
| `OLLAMA_MODEL` | `qwen2.5:14b` | Modelo LLM |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Modelo de embeddings |
| `SECRET_KEY` | — | Clave para firmar JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Duración del access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duración del refresh token |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | Orígenes CORS permitidos |
| `MAX_FILE_SIZE` | `10485760` | Tamaño máximo de subida (10 MB) |
| `DEBUG` | `False` | Activa docs, logs verbose, desactiva HSTS |

### Frontend (`frontend/.env.local`)

| Variable | Default | Descripción |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | URL base del backend |
| `NEXT_PUBLIC_APP_NAME` | `DocuMind` | Nombre de la aplicación |

---

## Estructura del repositorio

```
DocuMind/
├── backend/
│   ├── src/
│   │   ├── api/                    # Rutas, middleware, dependencias
│   │   ├── application/            # Use Cases y DTOs
│   │   ├── domain/                 # Entidades y repositorios abstractos
│   │   └── infrastructure/         # DB, Ollama, procesado PDF
│   ├── uploads/                    # PDFs subidos (ignorado en git)
│   ├── init_db.py                  # Crea todas las tablas
│   ├── migrate_refresh_tokens.py   # Migración para DBs existentes
│   ├── requirements.txt
│   ├── start_server.ps1
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── app/                    # Páginas Next.js
│   │   ├── features/               # auth, chat, documents
│   │   ├── components/             # UI + layout
│   │   ├── services/               # API + SSE client
│   │   ├── hooks/                  # useApiError, useDebounce
│   │   ├── lib/                    # constants, identity, utils
│   │   └── types/                  # Tipos TypeScript globales
│   ├── package.json
│   └── .env.local
│
├── docker-compose.yml              # PostgreSQL + pgvector
└── README.md
```

---

## API — Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/auth/register` | Registro de usuario |
| `POST` | `/api/auth/login` | Login |
| `POST` | `/api/auth/refresh` | Rotar refresh token |
| `POST` | `/api/auth/logout` | Revocar refresh token |
| `GET` | `/api/auth/me` | Perfil del usuario autenticado |
| `POST` | `/api/documents/upload` | Subir PDF |
| `GET` | `/api/documents/` | Listar documentos |
| `DELETE` | `/api/documents/{id}` | Eliminar documento |
| `GET` | `/api/chat/stream` | Chat con streaming SSE |
| `GET` | `/api/chat/documents/{id}/conversations` | Historial de conversación |
| `GET` | `/api/health` | Estado del servicio |

Documentación interactiva completa en `/docs` (solo con `DEBUG=True`).

---

## Seguridad

- **Ownership** — cada documento y conversación está vinculado al usuario; se verifica en cada operación
- **Rate limiting** — login/registro: 5–10 req/min; upload: 5/min; chat: 10–20/min
- **Validación de PDFs** — tipo MIME, extensión, tamaño y magic number `%PDF`
- **Límite de mensajes** — máx. 4 000 caracteres por mensaje (backend + frontend)
- **Mitigación de prompt injection** — regex sobre el input del usuario con logging
- **Security Headers** — `X-Content-Type-Options`, `X-Frame-Options`, `CSP`, `Referrer-Policy`, `Permissions-Policy`, HSTS (solo producción)
- **JWT con rotación** — refresh token hasheado (SHA-256) en base de datos; cada refresh emite un nuevo par y revoca el anterior
- **CORS** — orígenes configurables via `ALLOWED_ORIGINS`

---

## Docker Compose

El `docker-compose.yml` incluído levanta únicamente la base de datos para desarrollo local (el backend corre directamente con conda/uvicorn y Ollama corre en el host):

```bash
docker compose up -d    # Inicia PostgreSQL en localhost:5432
docker compose down     # Detiene el contenedor
docker compose down -v  # Detiene y elimina el volumen (borra todos los datos)
```

Credenciales por defecto: usuario `user`, contraseña `password`, base de datos `documind`.

---

## Documentación detallada

- [backend/README.md](backend/README.md) — arquitectura, endpoints completos, ejemplos curl, migraciones, troubleshooting del backend
- [frontend/README.md](frontend/README.md) — estructura, servicios, hooks, gestión de tokens, troubleshooting del frontend