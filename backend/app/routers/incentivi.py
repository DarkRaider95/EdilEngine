"""Router for incentivi (incentives) endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.incentivi import Incentivo
from app.schemas.incentivi import (
    IncentivoBase,
    IncentivoDetail,
    IncentivoFilter,
    IncentivoListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/incentivi", tags=["incentivi"])


@router.get("/", response_model=IncentivoListResponse)
async def list_incentivi(
    tipo: str | None = Query(default=None, description="Filter by incentive type"),
    ente_erogatore: str | None = Query(default=None, description="Filter by granting entity"),
    scadenza_dopo: str | None = Query(default=None, description="Filter by expiration date (YYYY-MM-DD)"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> IncentivoListResponse:
    """List construction incentives with optional filters.

    Supports filtering by type, granting entity, and expiration date.
    """
    offset = (page - 1) * page_size

    stmt = select(Incentivo)

    if tipo:
        stmt = stmt.where(Incentivo.tipo == tipo)
    if ente_erogatore:
        stmt = stmt.where(Incentivo.ente_erogatore.ilike(f"%{ente_erogatore}%"))
    if scadenza_dopo:
        stmt = stmt.where(Incentivo.scadenza >= scadenza_dopo)

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Get paginated results
    stmt = stmt.order_by(Incentivo.scadenza.asc().nulls_last()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    incentivi = result.scalars().all()

    items = [IncentivoBase.model_validate(inc) for inc in incentivi]

    return IncentivoListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{incentivo_id}", response_model=IncentivoDetail)
async def get_incentivo(
    incentivo_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> IncentivoDetail:
    """Get detailed information about a single incentive."""
    stmt = select(Incentivo).where(Incentivo.id == incentivo_id)
    result = await db.execute(stmt)
    incentivo = result.scalar_one_or_none()

    if not incentivo:
        raise HTTPException(status_code=404, detail="Incentivo non trovato")

    return IncentivoDetail.model_validate(incentivo)
