"""Pydantic schemas for leggi endpoints."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


# -------------------------------------------
# Legge schemas
# -------------------------------------------


class LeggeBase(BaseModel):
    """Base schema for a law/normative source."""

    id: UUID
    titolo: str
    tipo: str | None = None
    numero: str | None = None
    data_emanazione: date | None = None
    data_pubblicazione: date | None = None
    data_vigore: date | None = None
    autorita: str | None = None
    url_fonte: str | None = None

    model_config = {"from_attributes": True}


class LeggeDetail(LeggeBase):
    """Detailed schema for a single law with full text and categories."""

    id: UUID
    testo_completo: str | None = None
    categorie: list["CategoriaBase"] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class LeggeListResponse(BaseModel):
    """Paginated response for law listings."""

    items: list[LeggeBase]
    total: int
    page: int
    page_size: int


# -------------------------------------------
# Categoria schemas
# -------------------------------------------


class CategoriaBase(BaseModel):
    """Base schema for a category."""

    id: UUID
    nome: str
    parent_id: UUID | None = None

    model_config = {"from_attributes": True}


class CategoriaTree(CategoriaBase):
    """Hierarchical category with children."""

    children: list["CategoriaTree"] = Field(default_factory=list)


# -------------------------------------------
# Search schemas
# -------------------------------------------


class SearchQuery(BaseModel):
    """Query parameters for full-text search."""

    q: str = Field(..., min_length=1, description="Search query")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    tipo: str | None = Field(default=None, description="Filter by law type")
    autorita: str | None = Field(default=None, description="Filter by authority")
    data_da: date | None = Field(default=None, description="Filter from date")
    data_a: date | None = Field(default=None, description="Filter to date")


class SearchResult(BaseModel):
    """Response for search results."""

    items: list[LeggeBase]
    total: int
    page: int
    page_size: int


# -------------------------------------------
# Semantic search schemas
# -------------------------------------------


class SemanticSearchQuery(BaseModel):
    """Query parameters for semantic search."""

    q: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results")


class SemanticSearchResult(BaseModel):
    """Single result from semantic search."""

    chunk_id: UUID
    legge_id: UUID
    chunk_text: str
    chunk_index: int | None = None
    similarity: float
    legge_titolo: str | None = None
    legge_tipo: str | None = None
    legge_numero: str | None = None
    legge_url_fonte: str | None = None
