"""SQLAlchemy model for incentivi (construction incentives)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Date, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Incentivo(Base):
    """Model for construction incentives: Superbonus, Ecobonus, Sismabonus, etc."""

    __tablename__ = "incentivi"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    titolo: Mapped[str] = mapped_column(Text, nullable=False)
    descrizione: Mapped[str | None] = mapped_column(Text)
    ente_erogatore: Mapped[str | None] = mapped_column(String(255))
    tipo: Mapped[str | None] = mapped_column(String(100))
    aliquota: Mapped[float | None] = mapped_column(Numeric(5, 2))
    scadenza: Mapped[datetime | None] = mapped_column(Date)
    requisiti: Mapped[str | None] = mapped_column(Text)
    url_fonte: Mapped[str | None] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Incentivo(id={self.id}, titolo='{self.titolo}', tipo='{self.tipo}')>"
