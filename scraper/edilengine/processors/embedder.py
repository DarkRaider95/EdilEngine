"""
Embedding generation utilities for EdilEngine scraper.

Supports both local (sentence-transformers, FREE) and OpenAI embedding providers.
"""

import asyncio
import logging
import time
from typing import Optional

import openai
from openai import OpenAI, RateLimitError, APIConnectionError, APITimeoutError

logger = logging.getLogger(__name__)


class LocalEmbedder:
    """
    Local embedding generator using sentence-transformers (FREE, no API key needed).
    
    Best models for Italian text:
    - paraphrase-multilingual-MiniLM-L12-v2 (384 dim, fast, 471MB)
    - intfloat/multilingual-e5-small (384 dim, best for retrieval, 470MB)
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self._model = None
        self._request_count = 0
    
    @property
    def model(self):
        """Lazy-load the model on first use."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded: {self.model_name}")
        return self._model
    
    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        if not text:
            logger.warning("Empty text provided for embedding")
            return []
        
        embedding = self.model.encode(text, normalize_embeddings=True)
        self._request_count += 1
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        
        embeddings = self.model.encode(texts, normalize_embeddings=True, batch_size=batch_size)
        self._request_count += len(texts)
        return [emb.tolist() for emb in embeddings]
    
    async def generate_embedding_async(self, text: str) -> list[float]:
        """Generate embedding asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_embedding, text)
    
    def get_stats(self) -> dict:
        return {
            "request_count": self._request_count,
            "model": self.model_name,
            "provider": "local",
        }


class Embedder:
    """
    OpenAI embedding generator with rate limiting and retry logic.
    
    Generates embeddings using OpenAI's text-embedding models
    with exponential backoff for rate limit handling.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimensions: Optional[int] = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ):
        """
        Initialize the embedder.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for embeddings
            dimensions: Number of dimensions for embedding (optional)
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff
            max_delay: Maximum delay between retries
        """
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        
        self._client: Optional[OpenAI] = None
        self._request_count = 0
        self._last_request_time = 0.0
    
    @property
    def client(self) -> OpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    def _calculate_delay(self, attempt: int, response_headers: dict) -> float:
        """
        Calculate delay for retry with exponential backoff.
        
        Respects Retry-After header if present.
        
        Args:
            attempt: Current retry attempt number
            response_headers: Response headers from API
            
        Returns:
            Delay in seconds
        """
        # Check for Retry-After header
        retry_after = response_headers.get("retry-after")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        
        # Exponential backoff with jitter
        delay = self.base_delay * (2 ** attempt)
        
        # Add small jitter to avoid thundering herd
        import random
        jitter = random.uniform(0, 0.1 * delay)
        delay += jitter
        
        return min(delay, self.max_delay)
    
    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as list of floats
            
        Raises:
            Exception: If embedding generation fails after all retries
        """
        if not self.api_key:
            logger.warning("No API key provided, returning empty embedding")
            return []
        
        if not text:
            logger.warning("Empty text provided for embedding")
            return []
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Rate limiting
                self._enforce_rate_limit()
                
                # Create embedding request
                kwargs = {
                    "model": self.model,
                    "input": text,
                }
                
                if self.dimensions:
                    kwargs["dimensions"] = self.dimensions
                
                response = self.client.embeddings.create(**kwargs)
                
                # Update rate limit tracking
                self._update_rate_limit_tracking(response.headers)
                
                embedding = response.data[0].embedding
                
                logger.debug(
                    f"Generated embedding ({len(embedding)} dims) "
                    f"for text ({len(text)} chars)"
                )
                
                return embedding
                
            except RateLimitError as e:
                last_exception = e
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                )
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt, e.headers or {})
                    logger.info(f"Waiting {delay:.2f}s before retry...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries exceeded for rate limit")
                    
            except APIConnectionError as e:
                last_exception = e
                logger.warning(
                    f"Connection error (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                )
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt, {})
                    logger.info(f"Waiting {delay:.2f}s before retry...")
                    time.sleep(delay)
                    
            except APITimeoutError as e:
                last_exception = e
                logger.warning(
                    f"Timeout error (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                )
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt, {})
                    logger.info(f"Waiting {delay:.2f}s before retry...")
                    time.sleep(delay)
                    
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error generating embedding: {e}")
                break
        
        # All retries exhausted
        raise last_exception or Exception("Failed to generate embedding")
    
    async def generate_embedding_async(self, text: str) -> list[float]:
        """
        Generate embedding asynchronously.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as list of floats
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.generate_embedding, text
        )
    
    def generate_embeddings_batch(
        self,
        texts: list[str],
        batch_size: int = 16,
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in parallel
            
        Returns:
            List of embeddings
        """
        if not self.api_key:
            logger.warning("No API key provided, returning empty embeddings")
            return [[] for _ in texts]
        
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.debug(f"Processing batch {i // batch_size + 1}")
            
            for text in batch:
                try:
                    embedding = self.generate_embedding(text)
                    embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"Failed to embed text: {e}")
                    embeddings.append([])
        
        return embeddings
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests."""
        # Simple rate limiting - can be enhanced with token bucket
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        # Minimum 100ms between requests
        min_interval = 0.1
        
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        
        self._last_request_time = time.time()
        self._request_count += 1
    
    def _update_rate_limit_tracking(self, headers: dict):
        """Update rate limit tracking from response headers."""
        # Log rate limit info if available
        remaining = headers.get("x-ratelimit-remaining-tokens")
        reset = headers.get("x-ratelimit-reset-tokens")
        
        if remaining:
            logger.debug(f"Rate limit remaining: {remaining} tokens")
        if reset:
            logger.debug(f"Rate limit reset in: {reset}s")
    
    def get_stats(self) -> dict:
        """
        Get embedder statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "request_count": self._request_count,
            "model": self.model,
            "dimensions": self.dimensions,
        }


class EmbeddingCache:
    """
    Simple in-memory cache for embeddings.
    
    Caches embeddings by text hash to avoid regenerating
    embeddings for the same text.
    """
    
    def __init__(self, max_size: int = 10000):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of cached embeddings
        """
        self.max_size = max_size
        self._cache: dict[str, list[float]] = {}
        self._access_order: list[str] = []
    
    def _hash_text(self, text: str) -> str:
        """Create hash for text."""
        import hashlib
        return hashlib.sha256(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[list[float]]:
        """
        Get cached embedding for text.
        
        Args:
            text: Text to look up
            
        Returns:
            Cached embedding or None
        """
        text_hash = self._hash_text(text)
        
        if text_hash in self._cache:
            # Move to end of access order (LRU)
            self._access_order.remove(text_hash)
            self._access_order.append(text_hash)
            return self._cache[text_hash]
        
        return None
    
    def set(self, text: str, embedding: list[float]):
        """
        Cache embedding for text.
        
        Args:
            text: Text to cache
            embedding: Embedding to cache
        """
        text_hash = self._hash_text(text)
        
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size:
            oldest = self._access_order.pop(0)
            del self._cache[oldest]
        
        self._cache[text_hash] = embedding
        self._access_order.append(text_hash)
    
    def clear(self):
        """Clear the cache."""
        self._cache.clear()
        self._access_order.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)


def create_embedder(
    provider: str = "local",
    api_key: str = "",
    model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
    openai_model: str = "text-embedding-3-small",
    openai_base_url: str = "https://api.openai.com/v1",
) -> LocalEmbedder | Embedder:
    """Factory function to create the appropriate embedder.
    
    Args:
        provider: "local" for sentence-transformers (FREE) or "openai" for API
        api_key: OpenAI API key (required if provider="openai")
        model_name: Local model name (used if provider="local")
        openai_model: OpenAI model name (used if provider="openai")
        openai_base_url: OpenAI base URL (used if provider="openai")
    
    Returns:
        LocalEmbedder or Embedder instance
    """
    if provider.lower() == "local":
        logger.info(f"Using local embedding provider: {model_name}")
        return LocalEmbedder(model_name=model_name)
    elif provider.lower() == "openai":
        logger.info(f"Using OpenAI embedding provider: {openai_model}")
        return Embedder(api_key=api_key, model=openai_model)
    else:
        raise ValueError(f"Unknown embedding provider: {provider}. Use 'local' or 'openai'.")
