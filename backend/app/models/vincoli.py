"""SQLAlchemy model for vincoli (territorial constraints)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Vincolo(Base):
    """Model for territorial constraints: urban plans, zoning, restrictions."""

    __tablename__ = "vincoli"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    regione: Mapped[str | None] = mapped_column(String(255))
    provincia: Mapped[str | None] = mapped_column(String(255))
    comune: Mapped[str | None] = mapped_column(String(255))
    tipo_zona: Mapped[str | None] = mapped_column(String(100))
    descrizione: Mapped[str | None] = mapped_column(Text)
    norma_riferimento: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Vincolo(id={self.id}, comune='{self.comune}', tipo_zona='{self.tipo_zona}')>"
