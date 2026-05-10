"""Pydantic schemas for incentivi endpoints."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IncentivoBase(BaseModel):
    """Base schema for a construction incentive."""

    id: UUID
    titolo: str
    descrizione: str | None = None
    ente_erogatore: str | None = None
    tipo: str | None = None
    aliquota: float | None = None
    scadenza: date | None = None
    requisiti: str | None = None
    url_fonte: str | None = None

    model_config = {"from_attributes": True}


class IncentivoDetail(IncentivoBase):
    """Detailed schema for a single incentive."""

    id: UUID
    created_at: datetime


class IncentivoListResponse(BaseModel):
    """Paginated response for incentive listings."""

    items: list[IncentivoBase]
    total: int
    page: int
    page_size: int


class IncentivoFilter(BaseModel):
    """Filter parameters for incentive search."""

    tipo: str | None = Field(default=None, description="Filter by incentive type")
    ente_erogatore: str | None = Field(
        default=None, description="Filter by granting entity"
    )
    scadenza_dopo: date | None = Field(
        default=None, description="Filter by expiration date (after)"
    )
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
