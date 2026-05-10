"""Router for leggi (laws) endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

from app.database import get_db
from app.models.leggi import Categoria, Legge
from app.schemas.leggi import (
    CategoriaBase,
    CategoriaTree,
    LeggeBase,
    LeggeDetail,
    LeggeListResponse,
    SearchQuery,
    SearchResult,
    SemanticSearchQuery,
    SemanticSearchResult,
)
from app.services.search_service import SearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/leggi", tags=["leggi"])


@router.get("/", response_model=LeggeListResponse)
async def list_leggi(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    tipo: str | None = Query(default=None, description="Filter by law type"),
    autorita: str | None = Query(default=None, description="Filter by authority"),
    data_da: str | None = Query(default=None, description="Filter from date (YYYY-MM-DD)"),
    data_a: str | None = Query(default=None, description="Filter to date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
) -> LeggeListResponse:
    """List laws with pagination and optional filters.

    Supports filtering by type, authority, and date range.
    """
    offset = (page - 1) * page_size

    # Build base query
    stmt = select(Legge)

    # Apply filters
    if tipo:
        stmt = stmt.where(Legge.tipo == tipo)
    if autorita:
        stmt = stmt.where(Legge.autorita == autorita)
    if data_da:
        stmt = stmt.where(Legge.data_emanazione >= data_da)
    if data_a:
        stmt = stmt.where(Legge.data_emanazione <= data_a)

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Get paginated results
    stmt = stmt.order_by(Legge.data_emanazione.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    leggi = result.scalars().all()

    items = [
        LeggeBase.model_validate(legge) for legge in leggi
    ]

    return LeggeListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/search", response_model=SearchResult)
async def search_leggi(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    tipo: str | None = Query(default=None, description="Filter by law type"),
    autorita: str | None = Query(default=None, description="Filter by authority"),
    data_da: str | None = Query(default=None, description="Filter from date (YYYY-MM-DD)"),
    data_a: str | None = Query(default=None, description="Filter to date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
) -> SearchResult:
    """Full-text search on laws using PostgreSQL tsvector.

    Uses Italian text search configuration for proper stemming and stop words.
    """
    search_service = SearchService(db)
    return await search_service.full_text_search(
        query=q,
        page=page,
        page_size=page_size,
        tipo=tipo,
        autorita=autorita,
        data_da=data_da,
        data_a=data_a,
    )


@router.get("/semantic-search", response_model=list[SemanticSearchResult])
async def semantic_search_leggi(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(default=5, ge=1, le=50, description="Number of results"),
    db: AsyncSession = Depends(get_db),
) -> list[SemanticSearchResult]:
    """Semantic search on laws using pgvector embeddings.

    Generates an embedding for the query and finds the most similar
    text chunks in the database using cosine similarity.
    """
    search_service = SearchService(db)
    return await search_service.semantic_search(query=q, top_k=top_k)


@router.get("/categorie", response_model=list[CategoriaTree])
async def get_categorie_tree(
    db: AsyncSession = Depends(get_db),
) -> list[CategoriaTree]:
    """Get the hierarchical category tree.

    Returns categories organized in a tree structure with parent-child relationships.
    """
    stmt = select(Categoria).options(
        noload(Categoria.leggi),
        noload(Categoria.children),
        noload(Categoria.parent),
    ).order_by(Categoria.nome)
    result = await db.execute(stmt)
    all_categories = result.scalars().all()

    # Build tree structure
    category_map: dict[UUID, CategoriaTree] = {}
    roots: list[CategoriaTree] = []

    for cat in all_categories:
        category_map[cat.id] = CategoriaTree(
            id=cat.id,
            nome=cat.nome,
            parent_id=cat.parent_id,
            children=[],
        )

    for cat in all_categories:
        node = category_map[cat.id]
        if cat.parent_id and cat.parent_id in category_map:
            category_map[cat.parent_id].children.append(node)
        else:
            roots.append(node)

    return roots


@router.get("/{legge_id}", response_model=LeggeDetail)
async def get_legge(
    legge_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> LeggeDetail:
    """Get detailed information about a single law including categories."""
    stmt = (
        select(Legge)
        .where(Legge.id == legge_id)
        .options(selectinload(Legge.categorie))
    )
    result = await db.execute(stmt)
    legge = result.scalar_one_or_none()

    if not legge:
        raise HTTPException(status_code=404, detail="Legge non trovata")

    return LeggeDetail.model_validate(legge)
