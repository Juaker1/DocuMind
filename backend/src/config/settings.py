from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    """Configuración de la aplicación DocuMind"""
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/documind"
    
    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_embedding_model: str = "nomic-embed-text"
    
    # Application
    app_name: str = "DocuMind"
    debug: bool = True

    # CORS — lista de orígenes permitidos, separados por coma en .env
    # Ejemplo producción: ALLOWED_ORIGINS=https://app.documind.com
    allowed_origins: List[str] = ["http://localhost:3000"]

    # Auth
    secret_key: str = "change-me-in-production-use-a-long-random-string"
    
    # Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"
    allowed_extensions: List[str] = [".pdf"]
    
    # Embedding & Chunking
    chunk_size: int = 1500
    chunk_overlap: int = 300
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    """Devuelve una instancia singleton de Settings"""
    return Settings()
