from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import get_settings
from src.api.routes import health, documents, chat, auth

settings = get_settings()

app = FastAPI(
    title="DocuMind API",
    description="API para chatear con documentos PDF usando IA local (Ollama)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Permitir peticiones desde el frontend Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(health.router, tags=["Health"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

@app.on_event("startup")
async def startup_event():
    """Inicialización de recursos al arrancar"""
    print("=" * 60)
    print("🚀 DocuMind API iniciando...")
    print(f"📊 Database: {settings.database_url}")
    print(f"🤖 Ollama Host: {settings.ollama_host}")
    print(f"🧠 Modelo: {settings.ollama_model}")
    print(f"📝 Embedding Model: {settings.ollama_embedding_model}")
    print(f"📁 Upload Directory: {settings.upload_dir}")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza de recursos al cerrar"""
    print("👋 DocuMind API cerrando...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
