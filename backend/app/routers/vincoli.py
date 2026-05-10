"""Router for vincoli (territorial constraints) endpoints."""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.vincoli import Vincolo
from app.schemas.vincoli import VincoloBase, VincoloListResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vincoli", tags=["vincoli"])


@router.get("", response_model=VincoloListResponse)
async def list_vincoli(
    regione: str | None = Query(default=None, description="Filter by region"),
    provincia: str | None = Query(default=None, description="Filter by province"),
    comune: str | None = Query(default=None, description="Filter by municipality"),
    tipo_zona: str | None = Query(default=None, description="Filter by zone type"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> VincoloListResponse:
    """List territorial constraints with optional geographic filters.

    Supports filtering by region, province, municipality, and zone type.
    """
    offset = (page - 1) * page_size

    stmt = select(Vincolo)

    if regione:
        stmt = stmt.where(Vincolo.regione.ilike(f"%{regione}%"))
    if provincia:
        stmt = stmt.where(Vincolo.provincia.ilike(f"%{provincia}%"))
    if comune:
        stmt = stmt.where(Vincolo.comune.ilike(f"%{comune}%"))
    if tipo_zona:
        stmt = stmt.where(Vincolo.tipo_zona == tipo_zona)

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Get paginated results
    stmt = stmt.order_by(Vincolo.comune).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    vincoli = result.scalars().all()

    items = [VincoloBase.model_validate(v) for v in vincoli]

    return VincoloListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
