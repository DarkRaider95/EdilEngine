"""Pydantic schemas for vincoli (territorial constraints) endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class VincoloBase(BaseModel):
    """Base schema for a territorial constraint."""

    id: UUID
    regione: str | None = None
    provincia: str | None = None
    comune: str | None = None
    tipo_zona: str | None = None
    descrizione: str | None = None
    norma_riferimento: str | None = None

    model_config = {"from_attributes": True}


class VincoloListResponse(BaseModel):
    """Paginated response for vincolo listings."""

    items: list[VincoloBase]
    total: int
    page: int
    page_size: int
