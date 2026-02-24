from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from src.infrastructure.database.connection import Base
from datetime import datetime


class UserModel(Base):
    """Modelo de base de datos para usuarios (anónimos y registrados)"""
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid          = Column(String(36), unique=True, index=True, nullable=False)
    email         = Column(String(255), unique=True, nullable=True)   # NULL = anónimo
    password_hash = Column(String(255), nullable=True)
    is_anonymous  = Column(Boolean, default=True, nullable=False)
    created_at    = Column(DateTime, default=datetime.now, nullable=False)

    # Relaciones
    documents = relationship("DocumentModel", back_populates="user")
    refresh_tokens = relationship(
        "RefreshTokenModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class DocumentModel(Base):
    """Modelo de base de datos para documentos PDF"""
    __tablename__ = "documents"

    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename    = Column(String(255), nullable=False)
    file_path   = Column(String(512), nullable=False)
    file_size   = Column(Integer, nullable=False)
    total_pages = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.now, nullable=False)
    processed   = Column(Boolean, default=False, nullable=False)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relaciones
    user = relationship("UserModel", back_populates="documents")
    chunks = relationship(
        "DocumentChunkModel",
        back_populates="document",
        cascade="all, delete-orphan"
    )
    conversations = relationship(
        "ConversationModel",
        back_populates="document",
        cascade="all, delete-orphan"
    )


class DocumentChunkModel(Base):
    """Modelo para chunks de documentos con embeddings vectoriales"""
    __tablename__ = "document_chunks"

    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    content       = Column(Text, nullable=False)
    page_number   = Column(Integer, nullable=False)
    chunk_index   = Column(Integer, nullable=False)
    # nomic-embed-text genera embeddings de 768 dimensiones
    embedding     = Column(Vector(768), nullable=True)

    # Relaciones
    document = relationship("DocumentModel", back_populates="chunks")


class ConversationModel(Base):
    """Modelo para conversaciones sobre documentos (una por documento)"""
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint('document_id', name='uq_conversations_document_id'),
    )

    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    title      = Column(String(255), nullable=True)

    # Relaciones
    document = relationship("DocumentModel", back_populates="conversations")
    messages = relationship(
        "MessageModel",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="MessageModel.created_at"
    )


class MessageModel(Base):
    """Modelo para mensajes dentro de conversaciones"""
    __tablename__ = "messages"

    id              = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role       = Column(String(20), nullable=False)  # "user" o "assistant"
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Metadatos de citación (JSON como texto)
    cited_chunks = Column(Text, nullable=True)  # JSON serializado con IDs de chunks

    # Relaciones
    conversation = relationship("ConversationModel", back_populates="messages")


class RefreshTokenModel(Base):
    """
    Almacena el hash SHA-256 de los refresh tokens activos.
    Guardar el hash (no el token en claro) permite:
      - Invalidar un token robado sin exponer el valor original.
      - Implementar refresh token rotation: cada uso genera un nuevo par.
    """
    __tablename__ = "refresh_tokens"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA-256 hex
    expires_at = Column(DateTime, nullable=False)
    revoked    = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relaciones
    user = relationship("UserModel", back_populates="refresh_tokens")
