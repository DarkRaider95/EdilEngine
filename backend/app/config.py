"""EdilEngine application configuration."""

import logging
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://edilengine:edilengine_dev@localhost:5432/edilengine",
        description="Async PostgreSQL connection string",
    )

    # LLM Provider per chatbot (qualsiasi provider OpenAI-compatible)
    # OpenAI:       https://api.openai.com/v1      → modelli: gpt-4o, gpt-4o-mini
    # DeepSeek:     https://api.deepseek.com        → modelli: deepseek-chat, deepseek-reasoner
    # OpenRouter:   https://openrouter.ai/api/v1    → modelli: 100+ provider, anche gratuiti
    # Groq:         https://api.groq.com/openai/v1  → modelli: llama-3.1, mixtral (GRATIS con limiti)
    # Together:     https://api.together.ai/v1      → modelli: llama, mistral, ecc.
    # Mistral:      https://api.mistral.ai/v1       → modelli: mistral-large, codestral
    OPENAI_API_KEY: str = Field(
        default="",
        description="API key per il provider LLM (OpenAI, DeepSeek, OpenRouter, Groq, ecc.)",
    )
    OPENAI_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL del provider LLM (vedi commenti sopra per i vari provider)",
    )
    OPENAI_CHAT_MODEL: str = Field(
        default="gpt-4o",
        description="Modello per chat/completions (es. gpt-4o, deepseek-chat, meta-llama/llama-3.1-8b-instruct)",
    )

    # Embedding provider: "local" per modelli gratuiti, "openai" per API
    EMBEDDING_PROVIDER: str = Field(
        default="local",
        description="Provider per embeddings: 'local' (sentence-transformers, gratuito) o 'openai' (API a pagamento)",
    )
    EMBEDDING_MODEL_NAME: str = Field(
        default="paraphrase-multilingual-MiniLM-L12-v2",
        description="Nome modello embeddings locale (paraphrase-multilingual-MiniLM-L12-v2=384dim, intfloat/multilingual-e5-small=384dim)",
    )
    EMBEDDING_DIMENSION: int = Field(
        default=384,
        description="Dimensione vettore embeddings (384 per modelli locali, 1536 per OpenAI text-embedding-3-small)",
    )
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="Modello per embeddings OpenAI (usato solo se EMBEDDING_PROVIDER=openai)",
    )
    OPENAI_EMBEDDING_BASE_URL: str = Field(
        default="",
        description="Base URL per embeddings OpenAI se diverso dal chat provider",
    )

    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )

    # Security
    SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="Secret key for sessions/tokens",
    )

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(
        default=60,
        description="Maximum requests per window per IP",
    )
    RATE_LIMIT_WINDOW_SECONDS: int = Field(
        default=60,
        description="Rate limit window in seconds",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def log_level(self) -> int:
        """Parse LOG_LEVEL into logging constant."""
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)


@lru_cache
def get_settings() -> Settings:
    """Cached singleton for application settings."""
    return Settings()
