"""Router for personalized construction guide generation."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.guide_generator import GuideGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personalized-guide", tags=["guide"])


class VincoloItem(BaseModel):
    """Territorial constraint item in guide response."""

    id: UUID
    regione: str | None = None
    provincia: str | None = None
    comune: str | None = None
    tipo_zona: str | None = None
    descrizione: str | None = None
    norma_riferimento: str | None = None


class PermessoItem(BaseModel):
    """Required permit item in guide response."""

    tipo: str
    descrizione: str


class IncentivoItem(BaseModel):
    """Incentive item in guide response."""

    id: UUID
    titolo: str
    tipo: str | None = None
    aliquota: float | None = None
    scadenza: str | None = None
    requisiti: str | None = None
    url_fonte: str | None = None


class GuideResponse(BaseModel):
    """Response model for personalized guide generation."""

    vincoli: list[VincoloItem]
    permessi: list[PermessoItem]
    incentivi: list[IncentivoItem]
    checklist: list[str]
    markdown: str


class GuideRequest(BaseModel):
    """Request body for personalized guide generation."""

    regione: str = Field(..., description="Italian region")
    provincia: str = Field(..., description="Italian province")
    comune: str = Field(..., description="Italian municipality")
    tipo_intervento: str = Field(..., description="Type of construction intervention")
    materiale_costruzione: str | None = Field(
        default=None, description="Construction material"
    )
    destinazione_uso: str = Field(..., description="Intended use of the building")
    num_unita: int = Field(default=1, ge=1, description="Number of units")
    superficie_terreno_mq: float | None = Field(
        default=None, description="Land surface in square meters"
    )
    volume_previsto_mc: float | None = Field(
        default=None, description="Planned volume in cubic meters"
    )


@router.post("/", response_model=GuideResponse)
async def generate_guide(
    data: GuideRequest,
    db: AsyncSession = Depends(get_db),
) -> GuideResponse:
    """Generate a personalized step-by-step construction guide.

    The guide includes:
    - Territorial constraints for the specified location
    - Required building permits (CILA/SCIA/Permesso di Costruire)
    - Applicable incentives
    - AI-generated checklist of steps

    Args:
        data: Project details including location, intervention type, and specs.

    Returns:
        Structured guide with vincoli, permits, incentives, checklist, and markdown.
    """
    try:
        guide_generator = GuideGenerator(db)
        guide = await guide_generator.generate_guide(data.model_dump())
        return GuideResponse(**guide)
    except Exception as e:
        logger.error(f"Error generating guide: {e}")
        raise HTTPException(
            status_code=500,
            detail="Errore nella generazione della guida personalizzata",
        )
