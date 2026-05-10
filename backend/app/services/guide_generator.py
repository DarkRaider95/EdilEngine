"""Personalized guide generator for construction projects."""

import json
import logging
from datetime import date

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.incentivi import Incentivo
from app.models.vincoli import Vincolo

logger = logging.getLogger(__name__)

settings = get_settings()

# Mapping of intervention types to required permits
PERMIT_MAPPING = {
    "nuova_costruzione": "Permesso di Costruire",
    "ristrutturazione_edilizia": "Permesso di Costruire (ristrutturazione)",
    "ristrutturazione_pesante": "SCIA",
    "ristrutturazione_leggera": "CILA",
    "manutenzione_straordinaria": "CILA",
    "manutenzione_ordinaria": "Nessun titolo abilitativo (edilizia libera)",
    "cambio_destinazione_uso": "SCIA o Permesso di Costruire",
    "demolizione_ricostruzione": "Permesso di Costruire",
    "ampliamento": "Permesso di Costruire o SCIA",
}


class GuideGenerator:
    """Generates personalized step-by-step construction guides."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self.openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )

    async def _get_vincoli(
        self, regione: str, provincia: str, comune: str
    ) -> list[Vincolo]:
        """Retrieve territorial constraints for the specified location.

        Args:
            regione: Region name.
            provincia: Province name.
            comune: Municipality name.

        Returns:
            List of applicable Vincolo records.
        """
        stmt = select(Vincolo).where(
            Vincolo.comune.ilike(f"%{comune}%")
        )
        if provincia:
            stmt = stmt.where(Vincolo.provincia.ilike(f"%{provincia}%"))
        if regione:
            stmt = stmt.where(Vincolo.regione.ilike(f"%{regione}%"))

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _get_applicabili_incentivi(
        self, tipo_intervento: str, materiale_costruzione: str | None = None
    ) -> list[Incentivo]:
        """Retrieve applicable incentives based on intervention type.

        Args:
            tipo_intervento: Type of construction intervention.
            materiale_costruzione: Optional construction material.

        Returns:
            List of applicable Incentivo records.
        """
        stmt = select(Incentivo)

        # Filter by intervention type keywords
        tipo_keywords = []
        if "nuova" in tipo_intervento or "costruzione" in tipo_intervento:
            tipo_keywords.extend(["nuova costruzione", "efficientamento"])
        if "ristrutturazione" in tipo_intervento:
            tipo_keywords.extend(["ristrutturazione", "bonus casa"])
        if "materiale" in tipo_intervento or materiale_costruzione:
            if materiale_costruzione and "legno" in materiale_costruzione.lower():
                tipo_keywords.extend(["bioedilizia", "legno", "sostenibile"])

        # For now, return all active incentives (scadenza > today or no scadenza)
        today = date.today()
        stmt = stmt.where(
            (Incentivo.scadenza.is_(None)) | (Incentivo.scadenza >= today)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    def _identify_permesso(self, tipo_intervento: str) -> str:
        """Identify the required building permit based on intervention type.

        Args:
            tipo_intervento: Type of construction intervention.

        Returns:
            Name of the required permit.
        """
        tipo_lower = tipo_intervento.lower().replace(" ", "_")

        # Direct match
        if tipo_lower in PERMIT_MAPPING:
            return PERMIT_MAPPING[tipo_lower]

        # Partial match
        for key, permit in PERMIT_MAPPING.items():
            if key in tipo_lower or tipo_lower in key:
                return permit

        return "Da verificare con il comune (tipo intervento non riconosciuto)"

    async def generate_guide(self, data: dict) -> dict:
        """Generate a personalized construction guide.

        Steps:
        1. Retrieve territorial constraints for the municipality
        2. Identify required permits (CILA/SCIA/Permesso di Costruire)
        3. List applicable incentives
        4. Generate checklist via LLM
        5. Return structured JSON + markdown

        Args:
            data: Dictionary with user's construction project details.
                Expected keys: regione, provincia, comune, tipo_intervento,
                materiale_costruzione, destinazione_uso, num_unita,
                superficie_terreno_mq, volume_previsto_mc

        Returns:
            Dictionary with guide data including vincoli, permesso,
            incentivi, checklist, and markdown summary.
        """
        regione = data.get("regione", "")
        provincia = data.get("provincia", "")
        comune = data.get("comune", "")
        tipo_intervento = data.get("tipo_intervento", "")
        materiale_costruzione = data.get("materiale_costruzione")
        destinazione_uso = data.get("destinazione_uso", "")
        num_unita = data.get("num_unita", 1)
        superficie_terreno_mq = data.get("superficie_terreno_mq")
        volume_previsto_mc = data.get("volume_previsto_mc")

        # Step 1: Get territorial constraints
        vincoli = await self._get_vincoli(regione, provincia, comune)
        vincoli_data = [
            {
                "id": str(v.id),
                "regione": v.regione,
                "provincia": v.provincia,
                "comune": v.comune,
                "tipo_zona": v.tipo_zona,
                "descrizione": v.descrizione,
                "norma_riferimento": v.norma_riferimento,
            }
            for v in vincoli
        ]

        # Step 2: Identify required permits
        permesso_necessario = self._identify_permesso(tipo_intervento)
        permessi_data = [
            {"tipo": permesso_necessario, "descrizione": f"Permesso richiesto per: {tipo_intervento}"},
        ]

        # Step 3: Get applicable incentives
        incentivi = await self._get_applicabili_incentivi(
            tipo_intervento, materiale_costruzione
        )
        incentivi_data = [
            {
                "id": str(i.id),
                "titolo": i.titolo,
                "tipo": i.tipo,
                "aliquota": float(i.aliquota) if i.aliquota else None,
                "scadenza": str(i.scadenza) if i.scadenza else None,
                "requisiti": i.requisiti,
                "url_fonte": i.url_fonte,
            }
            for i in incentivi
        ]

        # Step 4: Generate checklist via LLM
        checklist = await self._generate_llm_checklist(
            regione=regione,
            provincia=provincia,
            comune=comune,
            tipo_intervento=tipo_intervento,
            materiale_costruzione=materiale_costruzione,
            destinazione_uso=destinazione_uso,
            num_unita=num_unita,
            superficie_terreno_mq=superficie_terreno_mq,
            volume_previsto_mc=volume_previsto_mc,
            vincoli=vincoli_data,
            permessi=permessi_data,
            incentivi=incentivi_data,
        )

        # Step 5: Build markdown summary
        markdown = self._build_markdown(
            comune=comune,
            provincia=provincia,
            regione=regione,
            tipo_intervento=tipo_intervento,
            destinazione_uso=destinazione_uso,
            num_unita=num_unita,
            superficie_terreno_mq=superficie_terreno_mq,
            volume_previsto_mc=volume_previsto_mc,
            permessi=permessi_data,
            vincoli=vincoli_data,
            incentivi=incentivi_data,
            checklist=checklist,
        )

        return {
            "vincoli": vincoli_data,
            "permessi": permessi_data,
            "incentivi": incentivi_data,
            "checklist": checklist,
            "markdown": markdown,
        }

    async def _generate_llm_checklist(self, **kwargs) -> list[str]:
        """Generate a step-by-step checklist using GPT-4o.

        Args:
            **kwargs: Project details for context.

        Returns:
            List of checklist items as strings.
        """
        prompt = f"""Sei un esperto di edilizia e urbanistica italiana.
Genera una checklist ordinata e pratica per il seguente progetto edilizio:

- Comune: {kwargs.get('comune')} ({kwargs.get('provincia')}, {kwargs.get('regione')})
- Tipo intervento: {kwargs.get('tipo_intervento')}
- Materiale costruzione: {kwargs.get('materiale_costruzione', 'N/D')}
- Destinazione d'uso: {kwargs.get('destinazione_uso', 'N/D')}
- Numero unità: {kwargs.get('num_unita', 'N/D')}
- Superficie terreno: {kwargs.get('superficie_terreno_mq', 'N/D')} mq
- Volume previsto: {kwargs.get('volume_previsto_mc', 'N/D')} mc
- Permesso necessario: {json.dumps(kwargs.get('permessi', []), ensure_ascii=False)}
- Vincoli trovati: {json.dumps(kwargs.get('vincoli', []), ensure_ascii=False)}
- Incentivi applicabili: {json.dumps(kwargs.get('incentivi', []), ensure_ascii=False)}

Rispondi SOLO con una lista JSON di stringhe, ogni stringa è un passo della checklist.
Esempio: ["Passo 1: ...", "Passo 2: ...", "Passo 3: ..."]
Non aggiungere altro testo, solo il JSON array."""

        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )

            content = response.choices[0].message.content or "[]"
            # Parse JSON from response (might be wrapped in markdown code blocks)
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                if content.startswith("json"):
                    content = content[4:].strip()

            checklist = json.loads(content)
            if isinstance(checklist, list):
                return checklist
            return [str(checklist)]

        except Exception as e:
            logger.error(f"Error generating LLM checklist: {e}")
            return [
                "Verifica la documentazione urbanistica del comune",
                "Presenta la richiesta di permesso necessario",
                "Attendi l'approvazione prima di iniziare i lavori",
                "Verifica la presenza di incentivi applicabili",
            ]

    def _build_markdown(self, **kwargs) -> str:
        """Build a markdown summary of the guide.

        Args:
            **kwargs: All guide data for formatting.

        Returns:
            Markdown-formatted guide summary.
        """
        lines = [
            f"# Guida Personalizzata - {kwargs['comune']} ({kwargs['provincia']})",
            "",
            "## Dati del Progetto",
            f"- **Tipo intervento:** {kwargs['tipo_intervento']}",
            f"- **Destinazione d'uso:** {kwargs['destinazione_uso']}",
            f"- **Numero unità:** {kwargs['num_unita']}",
        ]
        if kwargs.get("superficie_terreno_mq"):
            lines.append(f"- **Superficie terreno:** {kwargs['superficie_terreno_mq']} mq")
        if kwargs.get("volume_previsto_mc"):
            lines.append(f"- **Volume previsto:** {kwargs['volume_previsto_mc']} mc")

        lines.extend([
            "",
            "## Permessi Necessari",
        ])
        for p in kwargs["permessi"]:
            lines.append(f"- **{p['tipo']}**: {p['descrizione']}")
        lines.append("")

        if kwargs["vincoli"]:
            lines.append("## Vincoli Territoriali")
            for v in kwargs["vincoli"]:
                lines.append(f"- **{v['tipo_zona']}**: {v['descrizione']}")
                if v.get("norma_riferimento"):
                    lines.append(f"  - Norma: {v['norma_riferimento']}")
            lines.append("")

        if kwargs["incentivi"]:
            lines.append("## Incentivi Applicabili")
            for i in kwargs["incentivi"]:
                aliquota_str = f" ({i['aliquota']}%)" if i.get("aliquota") else ""
                scadenza_str = f" - Scadenza: {i['scadenza']}" if i.get("scadenza") else ""
                lines.append(f"- **{i['titolo']}**{aliquota_str}{scadenza_str}")
            lines.append("")

        lines.extend([
            "## Checklist Passo-Passo",
        ])
        for idx, item in enumerate(kwargs["checklist"], 1):
            lines.append(f"{idx}. {item}")

        return "\n".join(lines)
