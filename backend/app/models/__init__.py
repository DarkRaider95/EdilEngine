# EdilEngine Backend - Models
# Import all models so SQLAlchemy registers them with Base.metadata

from app.models.leggi import Categoria, EmbeddingChunk, Legge, LeggeCategoria
from app.models.incentivi import Incentivo
from app.models.vincoli import Vincolo
from app.models.chat import ChatMessage, ChatSession

__all__ = [
    "Legge",
    "Categoria",
    "LeggeCategoria",
    "EmbeddingChunk",
    "Incentivo",
    "Vincolo",
    "ChatSession",
    "ChatMessage",
]
