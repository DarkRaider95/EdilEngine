"""
SQLAlchemy models for EdilEngine database.

Defines ORM models matching the PostgreSQL schema with pgvector support.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    event,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID as PG_UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Relationship,
    relationship,
    validates,
)


class Base(DeclarativeBase):
    """Base class for all models."""
    
    pass


class Legge(Base):
    """
    Model for leggi table.
    
    Represents laws, decrees, circulars, and regulations.
    """
    
    __tablename__ = "leggi"
    
    id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    titolo: Mapped[str] = Column(Text, nullable=False)
    tipo: Mapped[Optional[str]] = Column(String(50))
    numero: Mapped[Optional[str]] = Column(String(50))
    data_emanazione: Mapped[Optional[datetime]] = Column(Date)
    data_pubblicazione: Mapped[Optional[datetime]] = Column(Date)
    data_vigore: Mapped[Optional[datetime]] = Column(Date)
    autorita: Mapped[Optional[str]] = Column(String(255))
    testo_completo: Mapped[Optional[str]] = Column(Text)
    url_fonte: Mapped[Optional[str]] = Column(String(1024))
    testo_tsvector: Mapped[Optional[str]] = Column(TSVECTOR)
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Relationships
    categorie: Mapped[List["Categoria"]] = relationship(
        secondary="leggi_categorie",
        back_populates="leggi",
    )
    chunks: Mapped[List["EmbeddingChunk"]] = relationship(
        back_populates="legge",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index("idx_leggi_testo_tsvector", "testo_tsvector", postgresql_using="gin"),
        Index("idx_leggi_titolo", "titolo"),
        Index("idx_leggi_data_emanazione", "data_emanazione"),
        Index("idx_leggi_autorita", "autorita"),
        Index("idx_leggi_tipo", "tipo"),
        Index(
            "idx_leggi_vigore",
            "data_vigore",
            postgresql_where=(data_vigore.isnot(None)),
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Legge(id={self.id}, titolo='{self.titolo[:30]}...')>"


class Categoria(Base):
    """
    Model for categorie table.
    
    Represents categories for organizing laws hierarchically.
    """
    
    __tablename__ = "categorie"
    
    id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    nome: Mapped[str] = Column(String(255), unique=True, nullable=False)
    parent_id: Mapped[Optional[UUID]] = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("categorie.id"),
    )
    
    # Relationships
    parent: Mapped[Optional["Categoria"]] = relationship(
        remote_side="Categoria.id",
        back_populates="children",
    )
    children: Mapped[List["Categoria"]] = relationship(
        back_populates="parent",
    )
    leggi: Mapped[List["Legge"]] = relationship(
        secondary="leggi_categorie",
        back_populates="categorie",
    )
    
    def __repr__(self) -> str:
        return f"<Categoria(id={self.id}, nome='{self.nome}')>"


class LeggeCategoria(Base):
    """
    Model for leggi_categorie junction table.
    
    Many-to-many relationship between laws and categories.
    """
    
    __tablename__ = "leggi_categorie"
    
    legge_id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("leggi.id", ondelete="CASCADE"),
        primary_key=True,
    )
    categoria_id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("categorie.id", ondelete="CASCADE"),
        primary_key=True,
    )
    
    def __repr__(self) -> str:
        return f"<LeggeCategoria(legge_id={self.legge_id}, categoria_id={self.categoria_id})>"


class Incentivo(Base):
    """
    Model for incentivi table.
    
    Represents building incentives like superbonus, ecobonus, etc.
    """
    
    __tablename__ = "incentivi"
    
    id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    titolo: Mapped[str] = Column(Text, nullable=False)
    descrizione: Mapped[Optional[str]] = Column(Text)
    ente_erogatore: Mapped[Optional[str]] = Column(String(255))
    tipo: Mapped[Optional[str]] = Column(String(100))
    aliquota: Mapped[Optional[float]] = Column(Numeric(5, 2))
    scadenza: Mapped[Optional[datetime]] = Column(Date)
    requisiti: Mapped[Optional[str]] = Column(Text)
    url_fonte: Mapped[Optional[str]] = Column(String(1024))
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    
    __table_args__ = (
        Index("idx_incentivi_tipo", "tipo"),
        Index("idx_incentivi_scadenza", "scadenza"),
        Index(
            "idx_incentivi_attivi",
            "scadenza",
            postgresql_where=(scadenza.isnot(None)) & (scadenza > func.current_date()),
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Incentivo(id={self.id}, titolo='{self.titolo[:30]}...')>"


class Vincolo(Base):
    """
    Model for vincoli table.
    
    Represents territorial constraints and zoning regulations.
    """
    
    __tablename__ = "vincoli"
    
    id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    regione: Mapped[Optional[str]] = Column(String(255))
    provincia: Mapped[Optional[str]] = Column(String(255))
    comune: Mapped[Optional[str]] = Column(String(255))
    tipo_zona: Mapped[Optional[str]] = Column(String(100))
    descrizione: Mapped[Optional[str]] = Column(Text)
    norma_riferimento: Mapped[Optional[str]] = Column(Text)
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    
    __table_args__ = (
        Index("idx_vincoli_comune", "comune"),
        Index("idx_vincoli_regione", "regione"),
        Index("idx_vincoli_tipo_zona", "tipo_zona"),
    )
    
    def __repr__(self) -> str:
        return f"<Vincolo(id={self.id}, regione='{self.regione}', comune='{self.comune}')>"


class EmbeddingChunk(Base):
    """
    Model for embedding_chunks table.
    
    Stores text chunks with vector embeddings for RAG retrieval.
    """
    
    __tablename__ = "embedding_chunks"
    
    id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    legge_id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("leggi.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_text: Mapped[str] = Column(Text, nullable=False)
    chunk_index: Mapped[int] = Column(Integer)
    embedding: Mapped[Optional[List[float]]] = Column(
        String,  # Will be handled by pgvector
    )
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    
    # Relationship
    legge: Mapped["Legge"] = relationship(back_populates="chunks")
    
    __table_args__ = (
        Index(
            "idx_embedding_chunks_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
    
    def __repr__(self) -> str:
        return f"<EmbeddingChunk(id={self.id}, legge_id={self.legge_id}, index={self.chunk_index})>"


class ChatSession(Base):
    """
    Model for chat_sessions table.
    
    Tracks chatbot sessions for conversation history.
    """
    
    __tablename__ = "chat_sessions"
    
    id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    session_id: Mapped[str] = Column(String(255), unique=True, nullable=False)
    user_agent: Mapped[Optional[str]] = Column(Text)
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    
    # Relationships
    messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index("idx_chat_sessions_session_id", "session_id"),
    )
    
    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}')>"


class ChatMessage(Base):
    """
    Model for chat_messages table.
    
    Stores chat messages with role and source references.
    """
    
    __tablename__ = "chat_messages"
    
    id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    session_id: Mapped[str] = Column(
        String(255),
        ForeignKey("chat_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = Column(
        String(20),
        nullable=False,
    )
    content: Mapped[Optional[str]] = Column(Text)
    sources: Mapped[Optional[dict]] = Column(JSONB)
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    
    # Relationship
    session: Mapped["ChatSession"] = relationship(back_populates="messages")
    
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="check_role_values",
        ),
        Index("idx_chat_messages_session_id", "session_id"),
        Index("idx_chat_messages_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, role='{self.role}', session_id='{self.session_id}')>"
