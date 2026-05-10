"""SQLAlchemy models for leggi, categorie, and embedding_chunks."""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Legge(Base):
    """Model for normative sources: laws, decrees, circulars, resolutions."""

    __tablename__ = "leggi"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    titolo: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str | None] = mapped_column(String(50))
    numero: Mapped[str | None] = mapped_column(String(50))
    data_emanazione: Mapped[datetime | None] = mapped_column(Date)
    data_pubblicazione: Mapped[datetime | None] = mapped_column(Date)
    data_vigore: Mapped[datetime | None] = mapped_column(Date)
    autorita: Mapped[str | None] = mapped_column(String(255))
    testo_completo: Mapped[str | None] = mapped_column(Text)
    url_fonte: Mapped[str | None] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    categorie = relationship(
        "Categoria",
        secondary="leggi_categorie",
        back_populates="leggi",
        lazy="selectin",
    )
    embedding_chunks = relationship(
        "EmbeddingChunk",
        back_populates="legge",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Legge(id={self.id}, titolo='{self.titolo}', tipo='{self.tipo}')>"


class Categoria(Base):
    """Hierarchical categories for law navigation."""

    __tablename__ = "categorie"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categorie.id")
    )

    # Relationships
    leggi = relationship(
        "Legge",
        secondary="leggi_categorie",
        back_populates="categorie",
        lazy="selectin",
    )
    children = relationship(
        "Categoria",
        back_populates="parent",
        lazy="selectin",
    )
    parent = relationship(
        "Categoria",
        back_populates="children",
        remote_side=[id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Categoria(id={self.id}, nome='{self.nome}')>"


class LeggeCategoria(Base):
    """Junction table for many-to-many relationship between leggi and categorie."""

    __tablename__ = "leggi_categorie"

    legge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leggi.id", ondelete="CASCADE"),
        primary_key=True,
    )
    categoria_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categorie.id", ondelete="CASCADE"),
        primary_key=True,
    )


class EmbeddingChunk(Base):
    """Text chunks with vector embeddings for RAG retrieval (pgvector)."""

    __tablename__ = "embedding_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    legge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leggi.id", ondelete="CASCADE"), nullable=False
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int | None] = mapped_column(Integer)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    legge = relationship("Legge", back_populates="embedding_chunks")

    def __repr__(self) -> str:
        return f"<EmbeddingChunk(id={self.id}, legge_id={self.legge_id}, index={self.chunk_index})>"
