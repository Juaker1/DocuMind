import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.api.limiter import limiter
from src.config.settings import get_settings
from src.api.routes import health, documents, chat, auth
from src.domain.exceptions import (
    DomainException,
    InvalidCredentialsError,
    EmailAlreadyRegisteredError,
    DocumentNotFoundError,
    AccessDeniedError,
)

settings = get_settings()

# ---------------------------------------------------------------------------
# Logging — formato estructurado, nivel INFO en producción
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("documind")

# ---------------------------------------------------------------------------
# App — en producción ocultamos /docs y /redoc para no exponer contratos
# ---------------------------------------------------------------------------
app = FastAPI(
    title="DocuMind API",
    description="API para chatear con documentos PDF usando IA local (Ollama)",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# ---------------------------------------------------------------------------
# Rate limiter — adjuntar al state para que slowapi lo encuentre
# ---------------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS — orígenes desde settings (variable de entorno ALLOWED_ORIGINS)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers globales
# ---------------------------------------------------------------------------

# Mapa de excepciones de dominio → código HTTP
_DOMAIN_STATUS_MAP = {
    InvalidCredentialsError: 401,
    EmailAlreadyRegisteredError: 409,
    AccessDeniedError: 404,    # Intencional: 404 no revela que el recurso existe
    DocumentNotFoundError: 404,
}

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """
    Captura excepciones de dominio conocidas y las traduce a HTTP.
    Los mensajes de DomainException son seguros para mostrar al cliente.
    """
    status_code = _DOMAIN_STATUS_MAP.get(type(exc), 400)
    logger.warning(
        "Domain exception | %s %s | %s: %s",
        request.method, request.url.path,
        type(exc).__name__, str(exc),
    )
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Red de seguridad para cualquier error no manejado.
    - Loguea el stack trace completo internamente.
    - Al cliente: mensaje genérico sin información técnica.
    """
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(
        "Error no manejado | %s %s\n%s",
        request.method, request.url.path, tb,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Ha ocurrido un error interno. Por favor intenta de nuevo."},
    )

# Registrar rutas
app.include_router(health.router, tags=["Health"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

@app.on_event("startup")
async def startup_event():
    """Inicialización de recursos al arrancar"""
    logger.info("=" * 60)
    logger.info("🚀 DocuMind API iniciando...")
    logger.info("📊 Database: %s", settings.database_url)
    logger.info("🤖 Ollama Host: %s", settings.ollama_host)
    logger.info("🧠 Modelo: %s", settings.ollama_model)
    logger.info("📝 Embedding Model: %s", settings.ollama_embedding_model)
    logger.info("📁 Upload Directory: %s", settings.upload_dir)
    logger.info("🌐 CORS Origins: %s", settings.allowed_origins)
    logger.info("🔒 Debug mode: %s", settings.debug)
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza de recursos al cerrar"""
    logger.info("👋 DocuMind API cerrando...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
