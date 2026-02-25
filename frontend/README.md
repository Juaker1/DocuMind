# DocuMind — Frontend

Aplicación Next.js 16 que provee la interfaz de usuario de DocuMind: un chatbot basado en RAG que permite subir documentos PDF y mantener conversaciones en tiempo real con ellos, impulsado por Ollama.

---

## Tecnologías

| Tecnología | Versión | Propósito |
|---|---|---|
| Next.js | 16.1.6 | Framework React — App Router |
| React | 19.2.3 | Biblioteca de UI |
| TypeScript | 5 | Tipado estático |
| Tailwind CSS | 4 | Estilos utilitarios |
| Axios | 1.13.4 | Cliente HTTP con interceptor JWT |
| EventSource / SSE | — | Streaming en tiempo real desde el backend |
| clsx + tailwind-merge | — | Utilidades para clases condicionales |
| React Compiler | 1.0.0 | Memorización automática (experimental) |
| pnpm | — | Gestor de paquetes |

---

## Arquitectura

El proyecto sigue una **arquitectura basada en funcionalidades** con una capa de servicios clara, manteniendo cada responsabilidad en su propio módulo.

```
src/
├── app/                    # Páginas del App Router de Next.js
│   ├── layout.tsx          # Layout raíz (proveedores, header)
│   ├── globals.css         # Estilos globales + scrollbar personalizado
│   ├── page.tsx            # Home — lista y subida de documentos
│   └── chat/
│       └── [documentId]/
│           └── page.tsx    # Interfaz de chat para un documento
│
├── components/             # Componentes compartidos y reutilizables
│   ├── ui/                 # Componentes UI primitivos
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Modal.tsx
│   │   └── Spinner.tsx
│   └── layout/             # Componentes de layout
│       ├── Header.tsx      # Barra de navegación con auth + modo oscuro
│       ├── Container.tsx
│       └── ThemeProvider.tsx
│
├── features/               # Módulos de funcionalidades autocontenidos
│   ├── auth/               # Autenticación
│   │   ├── AuthProvider.tsx        # Contexto + lógica JWT
│   │   └── components/
│   │       └── AuthModal.tsx       # Modal de login / registro
│   ├── chat/               # Interfaz de chat
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx   # Componente raíz del chat
│   │   │   ├── MessageList.tsx     # Lista de mensajes con scroll
│   │   │   ├── MessageBubble.tsx   # Burbujas usuario/asistente + citas
│   │   │   ├── MessageInput.tsx    # Textarea con contador de caracteres
│   │   │   ├── StreamingMessage.tsx# Burbuja de streaming en vivo
│   │   │   └── TypingIndicator.tsx # Puntos animados antes del primer token
│   │   └── hooks/
│   │       ├── useChat.ts          # Gestión del estado del chat
│   │       └── useStreamingResponse.ts # Ciclo de vida del SSE
│   └── documents/          # Gestión de documentos
│       ├── components/
│       │   ├── DocumentUpload.tsx  # Carga drag-and-drop
│       │   ├── DocumentCard.tsx    # Tarjeta con confirmaciones inline
│       │   └── DocumentList.tsx    # Grilla responsiva
│       └── hooks/
│           ├── useDocuments.ts     # Estado de CRUD y carga
│           └── useDocumentPolling.ts # Polling automático del estado de procesado
│
├── hooks/                  # Hooks personalizados compartidos
│   ├── useApiError.ts      # Estado de error normalizado
│   └── useDebounce.ts      # Debouncing de valores
│
├── lib/                    # Utilidades y constantes
│   ├── constants.ts        # Constantes globales (límites, rutas)
│   ├── identity.ts         # Gestión de tokens JWT + UUID (localStorage)
│   └── utils.ts            # cn(), formatFileSize(), formatDate(), etc.
│
├── services/               # Capa de comunicación con la API
│   ├── api.ts              # Instancia Axios + interceptor de auto-refresh 401
│   ├── documents.service.ts
│   ├── conversations.service.ts
│   ├── chat.service.ts
│   └── sse-client.ts       # Clase SSEClient (wrapper de EventSource)
│
└── types/                  # Tipos TypeScript globales
    ├── api.ts
    ├── chat.ts
    └── document.ts
```

---

## Requisitos previos

- **Node.js** ≥ 18
- **pnpm** (`npm install -g pnpm`)
- **Backend de DocuMind** corriendo en `http://localhost:8000`

---

## Instalación

```bash
# Desde la raíz del proyecto
cd frontend

# Instalar dependencias
pnpm install
```

---

## Variables de entorno

Crea un archivo `.env.local` en el directorio `frontend/`:

```dotenv
# URL del backend FastAPI en ejecución
NEXT_PUBLIC_API_URL=http://localhost:8000

# Nombre de la aplicación
NEXT_PUBLIC_APP_NAME=DocuMind
```

Ambas variables son opcionales — los valores mostrados arriba son los valores por defecto.

---

## Servidor de desarrollo

```bash
pnpm dev
```

Abre en [http://localhost:3000](http://localhost:3000). La página se recarga automáticamente al guardar.

---

## Build para producción

```bash
# Compilar
pnpm build

# Iniciar servidor de producción
pnpm start
```

---

## Scripts

| Comando | Descripción |
|---|---|
| `pnpm dev` | Servidor de desarrollo con hot reload (puerto 3000) |
| `pnpm build` | Build de producción (genera `.next/`) |
| `pnpm start` | Inicia el servidor de producción |
| `pnpm lint` | Ejecuta ESLint |

---

## Funcionalidades

### Gestión de documentos

- **Carga de PDFs drag-and-drop** — valida el tipo de archivo (`application/pdf`) y el tamaño (máx. 10 MB) antes de enviar
- **Grilla de documentos** — muestra nombre, tamaño, páginas, fecha de subida y estado de procesado
- **Polling automático de estado** — consulta cada 3 segundos mientras algún documento está siendo procesado, se detiene cuando todos están listos
- **Eliminar documento** — confirmación inline para evitar eliminaciones accidentales
- **Resetear conversación** — borra la conversación de un documento sin eliminarlo

### Chat RAG

- **Streaming SSE** — respuesta token a token en tiempo real via `EventSource`; se muestra un `TypingIndicator` antes de que llegue el primer token
- **Sistema de citas** — al finalizar el streaming, la UI muestra:
  - **Nivel 2** — números de página referenciados por la IA
  - **Nivel 3** — fragmentos exactos del documento fuente, agrupados por página, en una sección colapsable "Fuentes"
- **Filtrado del marcador @@FUENTES** — el marcador `@@FUENTES:[]@@` del backend se elimina del texto mostrado tanto durante el streaming como en la burbuja final
- **Una conversación por documento** — el backend encuentra o crea automáticamente una única conversación por par usuario–documento
- **Historial de conversación** — se carga al entrar a la página para que los mensajes anteriores sean visibles de inmediato
- **Reset de conversación** — disponible tanto desde el header del chat como desde la tarjeta del documento
- **Límite de caracteres** — los mensajes están limitados a 4 000 caracteres; aparece un contador cuando el uso supera el 80% del límite

### Autenticación

- **Sistema de tokens JWT access + refresh** — token de acceso (60 min), token de refresco (7 días)
- **Refresco automático de token** — el interceptor de respuesta de Axios captura los 401, llama a `POST /api/auth/refresh` y reintenta la solicitud original; una cola evita llamadas duplicadas de refresco entre solicitudes concurrentes
- **Modo anónimo** — los usuarios sin cuenta reciben un UUID almacenado en `localStorage`; pueden subir documentos y chatear sin registrarse
- **Modal de login / registro** — modal con pestañas accesible desde el header
- **Logout** — llama a `POST /api/auth/logout` para revocar el refresh token en el servidor antes de limpiar el localStorage
- **Eliminar cuenta** — revoca todos los tokens y elimina la cuenta

### UI / UX

- **Modo oscuro / claro** — toggle en el header; preferencia persistida en `localStorage`
- **Layout responsivo** — adaptado para móviles gracias a las clases utilitarias de Tailwind CSS v4
- **Scrollbar personalizado** — estilizado para los temas claro y oscuro mediante CSS
- **Auto-scroll** — la ventana de chat se desplaza al último mensaje en cada actualización

---

## Gestión de tokens (`src/lib/identity.ts`)

Todos los datos de identidad y tokens se almacenan en `localStorage`:

| Clave | Valor |
|---|---|
| `documind_uuid` | UUID de sesión anónima |
| `documind_token` | Token de acceso JWT |
| `documind_refresh_token` | Token de refresco JWT |

Funciones utilitarias: `getAuthToken`, `setAuthToken`, `clearAuthToken`, `getRefreshToken`, `setRefreshToken`, `clearRefreshToken`, `clearAllTokens`, `isAuthenticated`.

---

## Comunicación con la API (`src/services/api.ts`)

La instancia de Axios incluye dos interceptores:

1. **Interceptor de solicitud** — adjunta automáticamente `Authorization: Bearer <token>` del `localStorage` si el usuario está autenticado, o `X-Anonymous-ID: <uuid>` si no lo está.
2. **Interceptor de respuesta (manejador 401)** — ante una respuesta 401:
   - Llama a `POST /api/auth/refresh` con el refresh token almacenado
   - Guarda los nuevos tokens de acceso y refresco
   - Reintenta la solicitud original con el nuevo token de acceso
   - Si el refresco falla, llama a `clearAllTokens()` y rechaza todas las solicitudes en cola

Los endpoints de autenticación (`/api/auth/login`, `/api/auth/register`, `/api/auth/refresh`) están excluidos del ciclo de reintento 401 para evitar recursión infinita.

---

## Streaming SSE (`src/services/sse-client.ts`)

La clase `SSEClient` envuelve la API `EventSource` del navegador:

- Escucha eventos `message` (fragmentos de tokens) y los reenvía al callback `onMessage`
- Escucha eventos `complete` (el backend envía metadatos de conversación + citas)
- Escucha eventos `error` y llama a un callback opcional `onError`
- Expone `disconnect()` para cerrar la conexión de forma limpia

El hook `useStreamingResponse` gestiona el ciclo de vida del SSE (iniciar, detener, resetear) y expone el `streamingText` acumulado y el estado `isStreaming` a los componentes.

---

## Constantes (`src/lib/constants.ts`)

| Constante | Valor | Descripción |
|---|---|---|
| `API_BASE_URL` | `NEXT_PUBLIC_API_URL` | URL base del backend |
| `MAX_FILE_SIZE` | 10 MB | Tamaño máximo de subida (validado en cliente) |
| `ALLOWED_FILE_TYPES` | `['application/pdf']` | Tipos MIME aceptados |
| `MAX_MESSAGE_LENGTH` | 4 000 | Límite de caracteres del chat (sincronizado con backend) |
| `MESSAGES_PER_PAGE` | 50 | Tamaño de paginación del historial |
| `DEBOUNCE_DELAY` | 300 ms | Delay de debounce por defecto |
| `ROUTES` | `HOME`, `DOCUMENTS`, `CHAT(id)` | Rutas tipadas de la aplicación |

---

## Linting

ESLint está configurado mediante `eslint.config.mjs` usando `eslint-config-next`.

```bash
pnpm lint
```

---

## Solución de problemas

**`ECONNREFUSED` / errores de red en el navegador**
Verifica que el backend esté corriendo en la URL definida en `NEXT_PUBLIC_API_URL` (por defecto `http://localhost:8000`).

**Errores de token / bucle infinito de 401**
Limpia el `localStorage` desde las DevTools del navegador (`Application → Local Storage → Clear All`) y recarga la página. Esto resetea todos los tokens almacenados.

**El stream SSE nunca inicia**
Verifica que el `allowed_origins` de CORS del backend incluya `http://localhost:3000`. `EventSource` no admite cabeceras personalizadas, por lo que el UUID anónimo se envía como parámetro de consulta en los endpoints SSE.

**El build falla con errores de TypeScript**
Ejecuta `pnpm lint` para ver todos los errores y revisa el `tsconfig.json` — el modo estricto está habilitado.
