"""
Scrapy Pipelines for EdilEngine project.

Handles text cleaning, chunking, embedding generation, and database storage.
"""

import asyncio
import logging
import re
from typing import Any

from scrapy import Spider
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from edilengine.items import IncentivoItem, LeggeItem, VincoloItem
from edilengine.processors.chunker import chunk_text
from edilengine.processors.embedder import Embedder
from edilengine.processors.text_cleaner import clean_html_text

logger = logging.getLogger(__name__)


class TextCleaningPipeline:
    """
    Pipeline for cleaning and normalizing scraped text.
    
    Removes HTML tags, normalizes whitespace, handles encoding issues,
    and ensures consistent text formatting.
    """
    
    def __init__(self):
        """Initialize the text cleaning pipeline."""
        pass
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler settings."""
        return cls()
    
    def process_item(self, item: Any, spider: Spider) -> Any:
        """Process item and clean text fields."""
        if isinstance(item, LeggeItem):
            item = self._clean_legge_item(item)
        elif isinstance(item, IncentivoItem):
            item = self._clean_incentivo_item(item)
        elif isinstance(item, VincoloItem):
            item = self._clean_vincolo_item(item)
        
        return item
    
    def _clean_legge_item(self, item: LeggeItem) -> LeggeItem:
        """Clean LeggeItem text fields."""
        if item.get("titolo"):
            item["titolo"] = clean_html_text(item["titolo"])
        if item.get("testo_completo"):
            item["testo_completo"] = clean_html_text(item["testo_completo"])
        if item.get("autorita"):
            item["autorita"] = clean_html_text(item["autorita"])
        if item.get("categorie"):
            item["categorie"] = [
                clean_html_text(cat) for cat in item["categorie"]
            ]
        return item
    
    def _clean_incentivo_item(self, item: IncentivoItem) -> IncentivoItem:
        """Clean IncentivoItem text fields."""
        if item.get("titolo"):
            item["titolo"] = clean_html_text(item["titolo"])
        if item.get("descrizione"):
            item["descrizione"] = clean_html_text(item["descrizione"])
        if item.get("ente_erogatore"):
            item["ente_erogatore"] = clean_html_text(item["ente_erogatore"])
        if item.get("requisiti"):
            item["requisiti"] = clean_html_text(item["requisiti"])
        return item
    
    def _clean_vincolo_item(self, item: VincoloItem) -> VincoloItem:
        """Clean VincoloItem text fields."""
        if item.get("regione"):
            item["regione"] = clean_html_text(item["regione"])
        if item.get("provincia"):
            item["provincia"] = clean_html_text(item["provincia"])
        if item.get("comune"):
            item["comune"] = clean_html_text(item["comune"])
        if item.get("descrizione"):
            item["descrizione"] = clean_html_text(item["descrizione"])
        if item.get("norma_riferimento"):
            item["norma_riferimento"] = clean_html_text(item["norma_riferimento"])
        return item


class ChunkingPipeline:
    """
    Pipeline for splitting text into chunks for embedding.
    
    Divides text into overlapping chunks of specified size,
    respecting paragraph and sentence boundaries when possible.
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        """Initialize chunking pipeline with configuration."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler settings."""
        settings = crawler.settings
        return cls(
            chunk_size=settings.getint("CHUNK_SIZE", 512),
            chunk_overlap=settings.getint("CHUNK_OVERLAP", 50),
        )
    
    def process_item(self, item: Any, spider: Spider) -> Any:
        """Process item and create text chunks."""
        if isinstance(item, LeggeItem):
            item = self._chunk_legge_item(item)
        elif isinstance(item, IncentivoItem):
            item = self._chunk_incentivo_item(item)
        elif isinstance(item, VincoloItem):
            item = self._chunk_vincolo_item(item)
        
        return item
    
    def _chunk_legge_item(self, item: LeggeItem) -> LeggeItem:
        """Create chunks from LeggeItem text."""
        text = item.get("testo_completo", "")
        if text:
            chunks = chunk_text(
                text,
                chunk_size=self.chunk_size,
                overlap=self.chunk_overlap,
            )
            item["chunks"] = chunks
            logger.debug(f"Created {len(chunks)} chunks for {item.get('titolo', 'Unknown')}")
        else:
            item["chunks"] = []
            logger.warning(f"No text to chunk for {item.get('titolo', 'Unknown')}")
        return item
    
    def _chunk_incentivo_item(self, item: IncentivoItem) -> IncentivoItem:
        """Create chunks from IncentivoItem text."""
        text_parts = []
        if item.get("titolo"):
            text_parts.append(f"Titolo: {item['titolo']}")
        if item.get("descrizione"):
            text_parts.append(f"Descrizione: {item['descrizione']}")
        if item.get("requisiti"):
            text_parts.append(f"Requisiti: {item['requisiti']}")
        
        text = "\n\n".join(text_parts)
        if text:
            item["chunks"] = chunk_text(
                text,
                chunk_size=self.chunk_size,
                overlap=self.chunk_overlap,
            )
        else:
            item["chunks"] = []
        return item
    
    def _chunk_vincolo_item(self, item: VincoloItem) -> VincoloItem:
        """Create chunks from VincoloItem text."""
        text_parts = []
        if item.get("regione"):
            text_parts.append(f"Regione: {item['regione']}")
        if item.get("provincia"):
            text_parts.append(f"Provincia: {item['provincia']}")
        if item.get("comune"):
            text_parts.append(f"Comune: {item['comune']}")
        if item.get("descrizione"):
            text_parts.append(f"Descrizione: {item['descrizione']}")
        if item.get("norma_riferimento"):
            text_parts.append(f"Norma: {item['norma_riferimento']}")
        
        text = "\n\n".join(text_parts)
        if text:
            item["chunks"] = chunk_text(
                text,
                chunk_size=self.chunk_size,
                overlap=self.chunk_overlap,
            )
        else:
            item["chunks"] = []
        return item


class EmbeddingPipeline:
    """
    Pipeline for generating OpenAI embeddings for text chunks.
    
    Uses OpenAI's text-embedding-3-small model to generate
    vector embeddings for each text chunk.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        rate_limit: int = 10,
    ):
        """Initialize embedding pipeline with OpenAI configuration."""
        self.embedder = Embedder(api_key=api_key, model=model)
        self.rate_limit = rate_limit
        self._request_count = 0
        self._last_request_time = 0.0
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler settings."""
        settings = crawler.settings
        api_key = settings.get("OPENAI_API_KEY", "")
        model = settings.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        rate_limit = settings.getint("OPENAI_RATE_LIMIT", 10)
        
        if not api_key:
            logger.warning("OPENAI_API_KEY not set, embeddings will not be generated")
        
        return cls(api_key=api_key, model=model, rate_limit=rate_limit)
    
    def process_item(self, item: Any, spider: Spider) -> Any:
        """Process item and generate embeddings for chunks."""
        if not self.embedder.api_key:
            logger.debug("Skipping embedding generation - no API key")
            return item
        
        chunks = item.get("chunks", [])
        if not chunks:
            logger.debug(f"No chunks to embed for {item.get('titolo', 'Unknown')}")
            return item
        
        embeddings = []
        for i, chunk in enumerate(chunks):
            try:
                embedding = self.embedder.generate_embedding(chunk)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to generate embedding for chunk {i}: {e}")
                embeddings.append(None)
        
        item["embeddings"] = embeddings
        logger.debug(f"Generated {len(embeddings)} embeddings")
        return item


class DatabasePipeline:
    """
    Pipeline for storing scraped items in PostgreSQL database.
    
    Uses SQLAlchemy async to insert items into the database,
    handling upserts to avoid duplicates based on source URL.
    """
    
    def __init__(self, database_url: str):
        """Initialize database pipeline with connection URL."""
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self._initialized = False
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler settings."""
        settings = crawler.settings
        database_url = settings.get("DATABASE_URL")
        return cls(database_url=database_url)
    
    def open_spider(self, spider: Spider):
        """Initialize database connection when spider opens."""
        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            self._initialized = True
            logger.info(f"Database connection established: {self.database_url[:50]}...")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            self._initialized = False
    
    def close_spider(self, spider: Spider):
        """Close database connection when spider closes."""
        if self.engine:
            asyncio.run(self.engine.dispose())
            logger.info("Database connection closed")
    
    async def _get_or_create_categoria(self, session: AsyncSession, nome: str) -> int:
        """Get existing category or create new one, return ID."""
        from db.models import Categoria
        
        stmt = select(Categoria).where(Categoria.nome == nome)
        result = await session.execute(stmt)
        categoria = result.scalar_one_or_none()
        
        if not categoria:
            categoria = Categoria(nome=nome)
            session.add(categoria)
            await session.flush()
        
        return categoria.id
    
    async def _save_legge(self, session: AsyncSession, item: LeggeItem) -> int:
        """Save LeggeItem to database, return legge ID."""
        from db.models import Legge, LeggeCategoria
        
        # Check if legge already exists
        stmt = select(Legge).where(Legge.url_fonte == item.get("url_fonte"))
        result = await session.execute(stmt)
        legge = result.scalar_one_or_none()
        
        if legge:
            # Update existing legge
            legge.titolo = item.get("titolo", legge.titolo)
            legge.tipo = item.get("tipo", legge.tipo)
            legge.numero = item.get("numero", legge.numero)
            legge.data_emanazione = item.get("data_emanazione", legge.data_emanazione)
            legge.data_pubblicazione = item.get(
                "data_pubblicazione", legge.data_pubblicazione
            )
            legge.data_vigore = item.get("data_vigore", legge.data_vigore)
            legge.autorita = item.get("autorita", legge.autorita)
            legge.testo_completo = item.get("testo_completo", legge.testo_completo)
        else:
            # Create new legge
            legge = Legge(
                titolo=item.get("titolo"),
                tipo=item.get("tipo"),
                numero=item.get("numero"),
                data_emanazione=item.get("data_emanazione"),
                data_pubblicazione=item.get("data_pubblicazione"),
                data_vigore=item.get("data_vigore"),
                autorita=item.get("autorita"),
                testo_completo=item.get("testo_completo"),
                url_fonte=item.get("url_fonte"),
            )
            session.add(legge)
            await session.flush()
        
        # Handle categories
        categorie = item.get("categorie", [])
        for cat_nome in categorie:
            cat_id = await self._get_or_create_categoria(session, cat_nome)
            
            # Check if relation already exists
            stmt_rel = select(LeggeCategoria).where(
                LeggeCategoria.legge_id == legge.id,
                LeggeCategoria.categoria_id == cat_id,
            )
            result_rel = await session.execute(stmt_rel)
            if not result_rel.scalar_one_or_none():
                relazione = LeggeCategoria(legge_id=legge.id, categoria_id=cat_id)
                session.add(relazione)
        
        # Handle chunks and embeddings
        chunks = item.get("chunks", [])
        embeddings = item.get("embeddings", [])
        
        for i, (chunk_text_item, embedding) in enumerate(zip(chunks, embeddings)):
            if embedding is None:
                continue
            
            from db.models import EmbeddingChunk
            
            # Check if chunk already exists (by legge_id and chunk_index)
            stmt_chunk = select(EmbeddingChunk).where(
                EmbeddingChunk.legge_id == legge.id,
                EmbeddingChunk.chunk_index == i,
            )
            result_chunk = await session.execute(stmt_chunk)
            chunk_obj = result_chunk.scalar_one_or_none()
            
            if chunk_obj:
                # Update existing chunk
                chunk_obj.chunk_text = chunk_text_item
                chunk_obj.embedding = embedding
            else:
                # Create new chunk
                chunk_obj = EmbeddingChunk(
                    legge_id=legge.id,
                    chunk_index=i,
                    chunk_text=chunk_text_item,
                    embedding=embedding,
                )
                session.add(chunk_obj)
        
        await session.flush()
        return legge.id
    
    async def _save_incentivo(self, session: AsyncSession, item: IncentivoItem) -> int:
        """Save IncentivoItem to database, return incentivo ID."""
        from db.models import Incentivo
        
        stmt = select(Incentivo).where(Incentivo.url_fonte == item.get("url_fonte"))
        result = await session.execute(stmt)
        incentivo = result.scalar_one_or_none()
        
        if incentivo:
            incentivo.titolo = item.get("titolo", incentivo.titolo)
            incentivo.descrizione = item.get("descrizione", incentivo.descrizione)
            incentivo.ente_erogatore = item.get(
                "ente_erogatore", incentivo.ente_erogatore
            )
            incentivo.tipo = item.get("tipo", incentivo.tipo)
            incentivo.aliquota = item.get("aliquota", incentivo.aliquota)
            incentivo.scadenza = item.get("scadenza", incentivo.scadenza)
            incentivo.requisiti = item.get("requisiti", incentivo.requisiti)
        else:
            incentivo = Incentivo(
                titolo=item.get("titolo"),
                descrizione=item.get("descrizione"),
                ente_erogatore=item.get("ente_erogatore"),
                tipo=item.get("tipo"),
                aliquota=item.get("aliquota"),
                scadenza=item.get("scadenza"),
                requisiti=item.get("requisiti"),
                url_fonte=item.get("url_fonte"),
            )
            session.add(incentivo)
        
        await session.flush()
        return incentivo.id
    
    async def _save_vincolo(self, session: AsyncSession, item: VincoloItem) -> int:
        """Save VincoloItem to database, return vincolo ID."""
        from db.models import Vincolo
        
        # Create unique key for upsert
        unique_key = f"{item.get('regione')}-{item.get('provincia')}-{item.get('comune')}-{item.get('tipo_zona')}"
        
        stmt = select(Vincolo).where(Vincolo.url_fonte == item.get("url_fonte"))
        result = await session.execute(stmt)
        vincolo = result.scalar_one_or_none()
        
        if vincolo:
            vincolo.regione = item.get("regione", vincolo.regione)
            vincolo.provincia = item.get("provincia", vincolo.provincia)
            vincolo.comune = item.get("comune", vincolo.comune)
            vincolo.tipo_zona = item.get("tipo_zona", vincolo.tipo_zona)
            vincolo.descrizione = item.get("descrizione", vincolo.descrizione)
            vincolo.norma_riferimento = item.get(
                "norma_riferimento", vincolo.norma_riferimento
            )
        else:
            vincolo = Vincolo(
                regione=item.get("regione"),
                provincia=item.get("provincia"),
                comune=item.get("comune"),
                tipo_zona=item.get("tipo_zona"),
                descrizione=item.get("descrizione"),
                norma_riferimento=item.get("norma_riferimento"),
                url_fonte=item.get("url_fonte"),
            )
            session.add(vincolo)
        
        await session.flush()
        return vincolo.id
    
    def process_item(self, item: Any, spider: Spider) -> Any:
        """Process item and save to database."""
        if not self._initialized:
            logger.warning("Database not initialized, skipping item save")
            return item
        
        try:
            asyncio.run(self._process_item_async(item))
            logger.debug(f"Saved item: {item.get('titolo', 'Unknown')[:50]}...")
        except Exception as e:
            logger.error(f"Failed to save item to database: {e}", exc_info=True)
        
        return item
    
    async def _process_item_async(self, item: Any):
        """Async method to process and save item."""
        async with self.session_factory() as session:
            try:
                if isinstance(item, LeggeItem):
                    await self._save_legge(session, item)
                elif isinstance(item, IncentivoItem):
                    await self._save_incentivo(session, item)
                elif isinstance(item, VincoloItem):
                    await self._save_vincolo(session, item)
                
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
