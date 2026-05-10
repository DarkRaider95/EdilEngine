"""Embedding service supporting both local (sentence-transformers) and OpenAI providers.

Local models are FREE and run in-process. Recommended for development and low-cost deployment.
OpenAI models require an API key but offer higher quality embeddings.

Supported local models (multilingual, good for Italian):
- paraphrase-multilingual-MiniLM-L12-v2 (384 dim, fast, 471MB)
- intfloat/multilingual-e5-small (384 dim, excellent for retrieval, 470MB)
- intfloat/multilingual-e5-base (768 dim, better quality, 1.1GB)
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text string."""
        ...

    @abstractmethod
    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        ...


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local embedding provider using sentence-transformers (FREE, no API key needed).

    Downloads the model on first use and caches it locally.
    Best models for Italian text:
    - paraphrase-multilingual-MiniLM-L12-v2 (384 dim, fast)
    - intfloat/multilingual-e5-small (384 dim, best for retrieval)
    """

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None
        logger.info(f"Local embedding provider initialized with model: {model_name}")

    def _load_model(self):
        """Lazy-load the model on first use."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading local embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully: {self.model_name}")

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text string using local model.

        Args:
            text: The text to embed.

        Returns:
            List of floats representing the embedding vector.
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")

        self._load_model()
        embedding = self._model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts using local model.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors, one per input text.
        """
        if not texts:
            return []

        self._load_model()
        embeddings = self._model.encode(texts, normalize_embeddings=True, batch_size=64)
        return [emb.tolist() for emb in embeddings]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI-compatible embedding provider (requires API key).

    Supports OpenAI, DeepSeek (if they add embeddings), and any OpenAI-compatible API.
    """

    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        logger.info(f"OpenAI embedding provider initialized: model={model}, base_url={base_url}")

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text string via OpenAI API.

        Args:
            text: The text to embed.

        Returns:
            List of floats representing the embedding vector.
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")

        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding via OpenAI: {e}")
            raise

    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts via OpenAI API.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors, one per input text.
        """
        if not texts:
            return []

        all_embeddings: list[list[float]] = []
        batch_size = 100

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                )
                sorted_data = sorted(response.data, key=lambda x: x.index)
                batch_embeddings = [item.embedding for item in sorted_data]
                all_embeddings.extend(batch_embeddings)
                logger.debug(
                    f"Generated embeddings for batch {i // batch_size + 1} "
                    f"({len(batch)} texts)"
                )
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i // batch_size + 1}: {e}")
                all_embeddings.extend([[0.0] * 1536] * len(batch))

        return all_embeddings


class EmbeddingService:
    """Facade for embedding generation that delegates to the configured provider.

    Provider is selected via EMBEDDING_PROVIDER env var:
    - "local" (default): uses sentence-transformers, FREE, no API key
    - "openai": uses OpenAI API, requires OPENAI_API_KEY
    """

    def __init__(self) -> None:
        provider = settings.EMBEDDING_PROVIDER.lower().strip()

        if provider == "local":
            self._provider = LocalEmbeddingProvider(
                model_name=settings.EMBEDDING_MODEL_NAME,
            )
            self._dimension = settings.EMBEDDING_DIMENSION
            logger.info(
                f"EmbeddingService: using LOCAL provider "
                f"(model={settings.EMBEDDING_MODEL_NAME}, dim={self._dimension})"
            )
        elif provider == "openai":
            base_url = settings.OPENAI_EMBEDDING_BASE_URL or settings.OPENAI_BASE_URL
            self._provider = OpenAIEmbeddingProvider(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_EMBEDDING_MODEL,
                base_url=base_url,
            )
            # OpenAI text-embedding-3-small = 1536 dimensions
            self._dimension = 1536
            logger.info(
                f"EmbeddingService: using OPENAI provider "
                f"(model={settings.OPENAI_EMBEDDING_MODEL}, dim={self._dimension})"
            )
        else:
            raise ValueError(
                f"Unknown EMBEDDING_PROVIDER: '{provider}'. "
                f"Must be 'local' or 'openai'."
            )

    @property
    def dimension(self) -> int:
        """Return the embedding vector dimension."""
        return self._dimension

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text string."""
        return await self._provider.generate_embedding(text)

    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        return await self._provider.generate_embeddings_batch(texts)