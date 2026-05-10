"""Search service for full-text and semantic search on leggi."""

import logging
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.leggi import LeggeBase, SearchResult, SemanticSearchResult
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching laws via full-text and semantic search."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self.embedding_service = EmbeddingService()

    async def full_text_search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        tipo: str | None = None,
        autorita: str | None = None,
        data_da: str | None = None,
        data_a: str | None = None,
    ) -> SearchResult:
        """Perform full-text search using PostgreSQL tsvector.

        Uses Italian text search configuration for proper stemming and stop words.

        Args:
            query: Search query string.
            page: Page number (1-indexed).
            page_size: Number of results per page.
            tipo: Optional filter by law type.
            autorita: Optional filter by authority.
            data_da: Optional filter from date (ISO format).
            data_a: Optional filter to date (ISO format).

        Returns:
            SearchResult with paginated items and total count.
        """
        offset = (page - 1) * page_size

        # Build filter conditions
        filter_conditions: list[str] = []
        params: dict[str, object] = {"query": query}

        if tipo:
            filter_conditions.append("l.tipo = :tipo")
            params["tipo"] = tipo
        if autorita:
            filter_conditions.append("l.autorita = :autorita")
            params["autorita"] = autorita
        if data_da:
            filter_conditions.append("l.data_emanazione >= :data_da")
            params["data_da"] = data_da
        if data_a:
            filter_conditions.append("l.data_emanazione <= :data_a")
            params["data_a"] = data_a

        filters_sql = ""
        if filter_conditions:
            filters_sql = " AND " + " AND ".join(filter_conditions)

        # Count query
        count_sql = f"""
            SELECT COUNT(*) FROM leggi l
            WHERE l.testo_tsvector @@ plainto_tsquery('italian', :query)
            {filters_sql}
        """

        # Search query
        search_sql = f"""
            SELECT
                l.id, l.titolo, l.tipo, l.numero,
                l.data_emanazione, l.data_pubblicazione, l.data_vigore,
                l.autorita, l.url_fonte, l.created_at, l.updated_at,
                ts_rank(l.testo_tsvector, plainto_tsquery('italian', :query)) AS rank
            FROM leggi l
            WHERE l.testo_tsvector @@ plainto_tsquery('italian', :query)
            {filters_sql}
            ORDER BY rank DESC
            LIMIT :limit OFFSET :offset
        """

        params["limit"] = page_size
        params["offset"] = offset

        # Get total count
        count_result = await self.db.execute(text(count_sql), params)
        total = count_result.scalar() or 0

        # Get results
        result = await self.db.execute(text(search_sql), params)
        rows = result.mappings().all()

        items = [
            LeggeBase(
                titolo=row["titolo"],
                tipo=row["tipo"],
                numero=row["numero"],
                data_emanazione=row["data_emanazione"],
                data_pubblicazione=row["data_pubblicazione"],
                data_vigore=row["data_vigore"],
                autorita=row["autorita"],
                url_fonte=row["url_fonte"],
            )
            for row in rows
        ]

        return SearchResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def semantic_search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SemanticSearchResult]:
        """Perform semantic search using pgvector cosine similarity.

        Generates an embedding for the query and finds the most similar
        text chunks in the database.

        Args:
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of SemanticSearchResult with similarity scores.
        """
        # Generate embedding for the query
        query_embedding = await self.embedding_service.generate_embedding(query)

        # Search for similar chunks using pgvector cosine distance
        # <=> is the cosine distance operator in pgvector
        search_sql = text("""
            SELECT
                ec.id AS chunk_id,
                ec.legge_id,
                ec.chunk_text,
                ec.chunk_index,
                1 - (ec.embedding <=> :embedding) AS similarity,
                l.titolo AS legge_titolo,
                l.tipo AS legge_tipo,
                l.numero AS legge_numero,
                l.url_fonte AS legge_url_fonte
            FROM embedding_chunks ec
            JOIN leggi l ON l.id = ec.legge_id
            ORDER BY ec.embedding <=> :embedding
            LIMIT :limit
        """)

        result = await self.db.execute(
            search_sql,
            {"embedding": str(query_embedding), "limit": top_k},
        )
        rows = result.mappings().all()

        items = [
            SemanticSearchResult(
                chunk_id=row["chunk_id"],
                legge_id=row["legge_id"],
                chunk_text=row["chunk_text"],
                chunk_index=row["chunk_index"],
                similarity=float(row["similarity"]),
                legge_titolo=row["legge_titolo"],
                legge_tipo=row["legge_tipo"],
                legge_numero=row["legge_numero"],
                legge_url_fonte=row["legge_url_fonte"],
            )
            for row in rows
        ]

        logger.info(
            "Semantic search returned %d results for query: %s...",
            len(items),
            query[:50],
        )
        return items
